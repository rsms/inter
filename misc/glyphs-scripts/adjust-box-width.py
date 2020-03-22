#MenuTitle: Adjust glyph box width
# -*- coding: utf-8 -*-
from __future__ import print_function
import GlyphsApp
from math import ceil, floor
from os.path import basename
import vanilla
from vanilla import FloatingWindow, TextBox, EditText, Button

prefsKey = "me.rsms.adjust-sidebearings"


# glyphs which should never be resized
excludedGlyphNames = set([
  "emquad",
  "emspace",
  "enspace",
  "thirdemspace",
  "sixthemspace",
  "quarteremspace",
  "emdash", "emdash.case",
  "endash", "endash.case",
])

class Script( object ):
  def __init__(self):
    self.valuesPrefsKey = prefsKey + ".delta." + basename(Glyphs.font.filepath)
    # UI metrics
    spacing = 8
    height = 22
    # calculate window height
    minWinSize = (220, 120 + (len(Glyphs.font.masters) * (height + spacing)))
    # create UI window
    self.w = FloatingWindow(
      minWinSize,
      "Adjust sidebearings",
      minSize=minWinSize,
      maxSize=(500, 500),
      autosaveName=prefsKey + ".win")
    # layout UI controls
    y = 16
    self.w.label = TextBox((16, y, -16, height), "Sidebearing delta adjustment:")
    y += height + spacing

    inputWidth = 64
    for master in Glyphs.font.masters:
      setattr(self.w, "deltaLabel%s" % master.id,
        TextBox((16, y, -16-inputWidth, height), master.name))
      setattr(self.w, "deltaInput%s" % master.id,
        EditText((-16-inputWidth, y, -16, height), "16"))
      # print("self.w.deltaInputs[master.id]", getattr(self.w, "deltaInput%s" % master.id))
      y += height + spacing

    self.w.submitButton = Button(
      (16, -16-height, -16, height),
      "Adjust all sidebearings",
      callback=self.onSubmit)
    # finalize UI
    self.w.setDefaultButton(self.w.submitButton)
    self.loadPreferences()
    self.w.bind("close", self.savePreferences)

    # make sure window is large enough to show all masters
    x, y, w, h = self.w.getPosSize()
    if w < minWinSize[0] and h < minWinSize[1]:
      self.w.setPosSize((x, y, minWinSize[0], minWinSize[1]), animate=False)
    elif w < minWinSize[0]:
      self.w.setPosSize((x, y, minWinSize[0], h), animate=False)
    elif h < minWinSize[1]:
      self.w.setPosSize((x, y, w, minWinSize[1]), animate=False)

    self.w.open()
    self.w.makeKey()


  def getDeltaInputForMaster(self, masterId):
    return getattr(self.w, "deltaInput%s" % masterId)


  def loadPreferences(self):
    try:
      Glyphs.registerDefault(self.valuesPrefsKey, [])
      for t in Glyphs.defaults[self.valuesPrefsKey]:
        try:
          masterId, value = t
          self.getDeltaInputForMaster(masterId).set(value)
        except:
          pass
    except:
      print("failed to load preferences")


  def savePreferences(self, sender):
    try:
      values = []
      for master in Glyphs.font.masters:
        values.append((master.id, self.getDeltaInputForMaster(master.id).get()))
      Glyphs.defaults[self.valuesPrefsKey] = values
    except:
      print("failed to save preferences")


  def onSubmit(self, sender):
    try:
      sender.enable(False)
      if performFontChanges(self.action1):
        self.w.close()
    except Exception, e:
      Glyphs.showMacroWindow()
      print("error: %s" % e)
    finally:
      sender.enable(True)


  def action1(self, font):
    print(font)

    deltas = {}  # keyed on master.id
    for master in Glyphs.font.masters:
      deltas[master.id] = int(self.getDeltaInputForMaster(master.id).get())
    syncLayers = set()  # layers that need syncMetrics() to be called

    # [debug] alterntive loop over a few select glyphs, for debugging.
    # debugGlyphNames = set([
    #   ".null",
    #   "A", "Adieresis", "Lambda",
    #   "Bhook",
    #   "C", "Chook",
    #   "endash",
    #   "space",
    # ])
    # for g in [g for g in font.glyphs if g.name in debugGlyphNames]:
    for g in font.glyphs:
      # print(">> %s  (%s)" % (g.name, g.productionName))
      if g.name in excludedGlyphNames:
        # glyph is exlcuded
        print("ignoring excluded glyph %r" % g.name)
        continue
      g.beginUndo()
      try:
        for master in font.masters:
          layer = g.layers[master.id]
          delta = deltas[master.id]
          if delta == 0:
            # no adjustment
            continue

          if layer.width == 0:
            # ignore glyphs with zero-width layers
            print("ignoring zero-width glyph", g.name)
            break

          if layer.isAligned:
            # ignore glyphs which are auto-aligned from components
            print("ignoring auto-aligned glyph", g.name)
            break

          if len(layer.paths) == 0 and len(layer.components) == 0:
            # adjust width instead of LSB & RSB of empty glyphs
            if layer.widthMetricsKey is None:
              layer.width = max(0, layer.width + (delta * 2))
            else:
              syncLayers.add(layer)
            continue

          # offset components by delta to counter-act effect of also applying delta
          # to the component glyphs.
          if layer.components is not None:
            for cn in layer.components:
              m = cn.transform
              #         auto-aligned       or offset x or offset y   or contains shapes
              if not cn.automaticAlignment or m[4] != 0 or m[5] != 0 or len(layer.paths) > 0:
                cn.transform = (
                  m[0], # x scale factor
                  m[1], # x skew factor
                  m[2], # y skew factor
                  m[3], # y scale factor
                  m[4] - delta, # x position (+ since transform is inverse)
                  m[5]     # y position
                )

          # Note:
          # layer metrics keys are expressions, e.g. "==H+10"
          # glyph metrics keys are other glyphs, e.g. U+0041

          if g.leftMetricsKey is None and layer.leftMetricsKey is None:
            layer.LSB = layer.LSB + delta
          else:
            syncLayers.add(layer)

          if g.rightMetricsKey is None and layer.rightMetricsKey is None:
            layer.RSB = layer.RSB + delta
          else:
            syncLayers.add(layer)

      finally:
        g.endUndo()

    # end for g in font

    # sync layers that use metricsKey
    if len(syncLayers) > 0:
      print("Syncing LSB & RSB for %r layers..." % len(syncLayers))
      for layer in syncLayers:
        layer.syncMetrics()
    print("Done")



def performFontChanges(f):
  font = Glyphs.font
  font.disableUpdateInterface()
  try:
    f(font)
    return True  # success (as a result, the ui window will be closed)
  finally:
    font.enableUpdateInterface()
  return False  # error


Glyphs.clearLog()
Script()
