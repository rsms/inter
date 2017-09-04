"""

    Dialog prototypes.
    
    These are loaded before any others. So if a specific platform implementation doesn't
    have all functions, these will make sure a NotImplemtedError is raised.
    
    http://www.robofab.org/tools/dialogs.html
    
"""

__all__ = [
    "AskString",
    "AskYesNoCancel",
    "FindGlyph",
    "GetFile",
    "GetFolder",
    "GetFileOrFolder", 
    "Message",
    "OneList",
    "PutFile",
    "SearchList",
    "SelectFont",
    "SelectGlyph",
    "TwoChecks",
    "TwoFields",
    "ProgressBar",
]

# start with all the defaults. 

def AskString(message, value='', title='RoboFab'):
    raise NotImplementedError

def AskYesNoCancel(message, title='RoboFab', default=0):
    raise NotImplementedError

def FindGlyph(font, message="Search for a glyph:", title='RoboFab'):
    raise NotImplementedError

def GetFile(message=None):
    raise NotImplementedError

def GetFolder(message=None):
    raise NotImplementedError

def GetFileOrFolder(message=None):
    raise NotImplementedError

def Message(message, title='RoboFab'):
    raise NotImplementedError

def OneList(list, message="Select an item:", title='RoboFab'):
    raise PendingDeprecationWarning
    
def PutFile(message=None, fileName=None):
    raise NotImplementedError

def SearchList(list, message="Select an item:", title='RoboFab'):
    raise NotImplementedError

def SelectFont(message="Select a font:", title='RoboFab'):
    raise NotImplementedError

def SelectGlyph(font, message="Select a glyph:", title='RoboFab'):
    raise NotImplementedError

def TwoChecks(title_1="One",  title_2="Two", value1=1, value2=1, title='RoboFab'):
    raise PendingDeprecationWarning

def TwoFields(title_1="One:", value_1="0", title_2="Two:", value_2="0", title='RoboFab'):
    raise PendingDeprecationWarning

class ProgressBar(object):
    pass

