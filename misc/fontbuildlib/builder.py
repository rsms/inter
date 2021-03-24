import logging
import ufo2ft
from defcon import Font
from ufo2ft.util import _LazyFontName
from ufo2ft.filters.removeOverlaps import RemoveOverlapsFilter
from fontTools.designspaceLib import DesignSpaceDocument
from .name import getFamilyName, setFullName
from .info import updateFontVersion
from .glyph import findGlyphDirectives, composedGlyphIsTrivial, decomposeGlyphs
from .stat import rebuildStatTable

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

    # decompose some glyphs
    glyphNamesToDecompose = set()
    componentReferences = set(ufo.componentReferences)
    for g in ufo:
      directives = findGlyphDirectives(g.note)
      if self._shouldDecomposeGlyph(g, directives, componentReferences):
        glyphNamesToDecompose.add(g.name)
    self._decompose([ufo], glyphNamesToDecompose)

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

    # rebuild STAT table to correct VF instance information
    rebuildStatTable(font, designspace)

    log.debug("writing %s", outputFilename)
    font.save(outputFilename)


  def _decompose(self, ufos, glyphNamesToDecompose):
    # Note: Used for building both static and variable fonts
    if glyphNamesToDecompose:
      if log.isEnabledFor(logging.DEBUG):
        log.debug('Decomposing glyphs:\n  %s', "\n  ".join(glyphNamesToDecompose))
      elif log.isEnabledFor(logging.INFO):
        log.info('Decomposing %d glyphs', len(glyphNamesToDecompose))
      decomposeGlyphs(ufos, glyphNamesToDecompose)

  def _shouldDecomposeGlyph(self, g, directives, componentReferences):
    # Note: Used for building both static and variable fonts
    if 'decompose' in directives:
      return True
    if g.components:
      if g.name in componentReferences:
        # This means that the glyph...
        # a) has component instances and
        # b) is itself a component used by other glyphs as instances.
        # Decomposing these glyphs satisfies the fontbakery check
        #   com.google.fonts/check/glyf_nested_components
        #   "Check glyphs do not have components which are themselves components."
        #   https://github.com/googlefonts/fontbakery/issues/2961
        #   https://github.com/arrowtype/recursive/issues/412
        #
        # ufo.componentReferences:
        #   A dict of describing the component relationships in the font’s main layer.
        #   The dictionary is of form {"base_glyph_name": ["ref_glyph_name"]}.
        log.debug("decompose %r (glyf_nested_components)" % g.name)
        return True
      if not composedGlyphIsTrivial(g):
        return True
    return False

  def _loadDesignspace(self, designspace):
    # Note: Only used for building variable fonts
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

    log.info("Preprocessing glyphs")
    # find glyphs subject to decomposition and/or overlap removal
    # TODO: Find out why this loop is SO DAMN SLOW. It might just be so that defcon is
    #       really slow when reading glyphs. Perhaps we can sidestep defcon and just
    #       read & parse the .glif files ourselves.
    glyphNamesToDecompose  = set()  # glyph names
    glyphsToRemoveOverlaps = set()  # glyph objects
    for ufo in masters:
      # Note: ufo is of type defcon.objects.font.Font
      # update font version
      updateFontVersion(ufo, dummy=False, isVF=True)
      componentReferences = set(ufo.componentReferences)
      for g in ufo:
        directives = findGlyphDirectives(g.note)
        if self._shouldDecomposeGlyph(g, directives, componentReferences):
          glyphNamesToDecompose.add(g.name)
        if 'removeoverlap' in directives:
          if g.components and len(g.components) > 0:
            glyphNamesToDecompose.add(g.name)
          glyphsToRemoveOverlaps.add(g)

    self._decompose(masters, glyphNamesToDecompose)

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

