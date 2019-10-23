import logging
import ufo2ft
from defcon import Font
from ufo2ft.util import _LazyFontName
from ufo2ft.filters.removeOverlaps import RemoveOverlapsFilter
from fontTools.designspaceLib import DesignSpaceDocument
from .name import getFamilyName, setFullName
from .info import updateFontVersion
from .glyph import findGlyphDirectives, composedGlyphIsTrivial, decomposeGlyphs

log = logging.getLogger(__name__)


class FontBuilder:
  # def __init__(self, *args, **kwargs)

  def buildStatic(self,
    ufo,             # input UFO as filename string or defcon.Font object
    outputFilename,  # output filename string
    cff=True,        # true = makes CFF outlines. false = makes TTF outlines.
    **kwargs,        # passed along to ufo2ft.compile*()
  ):
    if isinstance(ufo, str):
      ufo = Font(ufo)

    # update version to actual, real version. Must come after any call to setFontInfo.
    updateFontVersion(ufo, dummy=False, isVF=False)

    compilerOptions = dict(
      useProductionNames=True,
      inplace=True,  # avoid extra copy
      removeOverlaps=True,
      overlapsBackend='pathops', # use Skia's pathops
    )

    log.info("compiling %s -> %s (%s)", _LazyFontName(ufo), outputFilename,
             "OTF/CFF-2" if cff else "TTF")

    if cff:
      font = ufo2ft.compileOTF(ufo, **compilerOptions)
    else: # ttf
      font = ufo2ft.compileTTF(ufo, **compilerOptions)

    log.debug("writing %s", outputFilename)
    font.save(outputFilename)



  def buildVariable(self,
    designspace,    # designspace filename string or DesignSpaceDocument object
    outputFilename, # output filename string
    cff=False,      # if true, builds CFF-2 font, else TTF
    **kwargs,       # passed along to ufo2ft.compileVariable*()
  ):
    designspace = self._loadDesignspace(designspace)

    # check in the designspace's <lib> element if user supplied a custom featureWriters
    # configuration; if so, use that for all the UFOs built from this designspace.
    featureWriters = None
    if ufo2ft.featureWriters.FEATURE_WRITERS_KEY in designspace.lib:
      featureWriters = ufo2ft.featureWriters.loadFeatureWriters(designspace)

    compilerOptions = dict(
      useProductionNames=True,
      featureWriters=featureWriters,
      inplace=True,  # avoid extra copy
      **kwargs
    )

    if log.isEnabledFor(logging.INFO):
      log.info("compiling %s -> %s (%s)", designspace.path, outputFilename,
               "OTF/CFF-2" if cff else "TTF")

    if cff:
      font = ufo2ft.compileVariableCFF2(designspace, **compilerOptions)
    else:
      font = ufo2ft.compileVariableTTF(designspace, **compilerOptions)

    # Rename fullName record to familyName (VF only).
    # Note: Even though we set openTypeNameCompatibleFullName it seems that the fullName
    # record is still computed by fonttools, so we override it here.
    setFullName(font, getFamilyName(font))

    log.debug("writing %s", outputFilename)
    font.save(outputFilename)



  @staticmethod
  def _loadDesignspace(designspace):
    log.info("loading designspace sources")
    if isinstance(designspace, str):
      designspace = DesignSpaceDocument.fromfile(designspace)
    else:
      # copy that we can mess with
      designspace = DesignSpaceDocument.fromfile(designspace.path)

    masters = designspace.loadSourceFonts(opener=Font)
    # masters = [s.font for s in designspace.sources]  # list of UFO font objects

    # Update the default source's full name to not include style name
    defaultFont = designspace.default.font
    defaultFont.info.openTypeNameCompatibleFullName = defaultFont.info.familyName

    for ufo in masters:
      # update font version
      updateFontVersion(ufo, dummy=False, isVF=True)

    log.info("Preprocessing glyphs")
    # find glyphs subject to decomposition and/or overlap removal
    # TODO: Find out why this loop is SO DAMN SLOW. It might just be so that defcon is
    #       really slow when reading glyphs. Perhaps we can sidestep defcon and just
    #       read & parse the .glif files ourselves.
    glyphNamesToDecompose  = set()  # glyph names
    glyphsToRemoveOverlaps = set()  # glyph objects
    for ufo in masters:
      for g in ufo:
        if g.components and not composedGlyphIsTrivial(g):
          glyphNamesToDecompose.add(g.name)
        if 'removeoverlap' in findGlyphDirectives(g.note):
          if g.components and len(g.components) > 0:
            glyphNamesToDecompose.add(g.name)
          glyphsToRemoveOverlaps.add(g)

    # decompose
    if glyphNamesToDecompose:
      if log.isEnabledFor(logging.DEBUG):
        log.debug('Decomposing glyphs:\n  %s', "\n  ".join(glyphNamesToDecompose))
      elif log.isEnabledFor(logging.INFO):
        log.info('Decomposing %d glyphs', len(glyphNamesToDecompose))
      decomposeGlyphs(masters, glyphNamesToDecompose)

    # remove overlaps
    if glyphsToRemoveOverlaps:
      rmoverlapFilter = RemoveOverlapsFilter(backend='pathops')
      rmoverlapFilter.start()
      if log.isEnabledFor(logging.DEBUG):
        log.debug(
          'Removing overlaps in glyphs:\n  %s',
          "\n  ".join(set([g.name for g in glyphsToRemoveOverlaps])),
        )
      elif log.isEnabledFor(logging.INFO):
        log.info('Removing overlaps in %d glyphs', len(glyphsToRemoveOverlaps))
      for g in glyphsToRemoveOverlaps:
        rmoverlapFilter.filter(g)

    # handle control back to fontmake
    return designspace

