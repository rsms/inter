"""

    Dialogs for FontLab < 5.1. 
    
    This one should be loaded for various platforms, using dialogKit
    http://www.robofab.org/tools/dialogs.html
    
"""

from FL import *
from dialogKit import ModalDialog, Button, TextBox, EditText

__all__ = [
    #"AskString",
    #"AskYesNoCancel",
    #"FindGlyph",
    "GetFile",
    "GetFolder",
    #"Message",
    #"OneList",
    #"PutFile",
    #"SearchList",
    #"SelectFont",
    #"SelectGlyph",
    #"TwoChecks",
    #"TwoFields",
    "ProgressBar",
]


def GetFile(message=None, title=None, directory=None, fileName=None, allowsMultipleSelection=False, fileTypes=None):
    strFilter = "All Files  (*.*)|*.*|"
    defaultExt = ""
    # using fontlab's internal file dialogs
    return fl.GetFileName(1, defaultExt, message, strFilter)

def GetFolder(message=None, title=None, directory=None, allowsMultipleSelection=False):
    # using fontlab's internal file dialogs
    if message is None:
        message = ""
    return fl.GetPathName(message)
    
def PutFile(message=None, fileName=None):
    # using fontlab's internal file dialogs
    # message is not used
    if message is None:
        message = ""
    if fileName is None:
        fileName = ""
    defaultExt = ""
    return fl.GetFileName(0, defaultExt, fileName, '')

class ProgressBar(object):

    def __init__(self, title="RoboFab...", ticks=0, label=""):
        self._tickValue = 1
        fl.BeginProgress(title, ticks)

    def getCurrentTick(self):
        return self._tickValue

    def tick(self, tickValue=None):
        if not tickValue:
            tickValue = self._tickValue
        fl.TickProgress(tickValue)
        self._tickValue = tickValue + 1

    def label(self, label):
        pass

    def close(self):
        fl.EndProgress()

