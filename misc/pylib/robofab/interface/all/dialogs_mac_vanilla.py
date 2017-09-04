"""

    Dialogs for environments that support cocao / vanilla.

"""

import vanilla.dialogs
from AppKit import NSApp, NSModalPanelWindowLevel, NSWindowCloseButton, NSWindowZoomButton, NSWindowMiniaturizeButton

__all__ = [
    "AskString",
    "AskYesNoCancel",
    "FindGlyph",
    "GetFile",
    "GetFileOrFolder",
    "GetFolder",
    "Message",
    "OneList",
    "PutFile",
    "SearchList",
    "SelectFont",
    "SelectGlyph",
#    "TwoChecks",
#    "TwoFields",
    "ProgressBar",
]

class _ModalWindow(vanilla.Window):
    
    nsWindowLevel = NSModalPanelWindowLevel 
    
    def __init__(self, *args, **kwargs):
        super(_ModalWindow, self).__init__(*args, **kwargs)
        self._window.standardWindowButton_(NSWindowCloseButton).setHidden_(True)
        self._window.standardWindowButton_(NSWindowZoomButton).setHidden_(True)
        self._window.standardWindowButton_(NSWindowMiniaturizeButton).setHidden_(True)
    
    def open(self):
        super(_ModalWindow, self).open()
        self.center()
        NSApp().runModalForWindow_(self._window)
        
    def windowWillClose_(self, notification):
        super(_ModalWindow, self).windowWillClose_(notification)
        NSApp().stopModal()


class _baseWindowController(object):
    
    def setUpBaseWindowBehavior(self):
        self._getValue = None
        
        self.w.okButton = vanilla.Button((-70, -30, -15, 20), "OK", callback=self.okCallback, sizeStyle="small")
        self.w.setDefaultButton(self.w.okButton)
        
        self.w.closeButton = vanilla.Button((-150, -30, -80, 20), "Cancel", callback=self.closeCallback, sizeStyle="small")
        self.w.closeButton.bind(".", ["command"])
        self.w.closeButton.bind(unichr(27), [])
        
        self.cancelled = False
    
    def okCallback(self, sender):
        self.w.close()
    
    def closeCallback(self, sender):
        self.cancelled = True
        self.w.close()
    
    def get(self):
        raise NotImplementedError


class _AskStringController(_baseWindowController):

    def __init__(self, message, value, title):
        self.w = _ModalWindow((370, 110), title)
        
        self.w.infoText = vanilla.TextBox((15, 10, -15, 22), message)
        self.w.input = vanilla.EditText((15, 40, -15, 22))
        self.w.input.set(value)
        
        self.setUpBaseWindowBehavior()
        self.w.open()
    
    def get(self):
        if self.cancelled:
            return None
        return self.w.input.get()
    

class _listController(_baseWindowController):
    
    def __init__(self, items, message, title, showSearch=False):
        
        self.items = items
        
        self.w = _ModalWindow((350, 300), title)
        y = 10
        self.w.infoText = vanilla.TextBox((15, y, -15, 22), message)
        y += 25
        if showSearch:
            self.w.search = vanilla.SearchBox((15, y, -15, 22), callback=self.searchCallback)
            y += 25
        self.w.itemList = vanilla.List((15, y, -15, -40), self.items, allowsMultipleSelection=False)
        
        self.setUpBaseWindowBehavior()
        self.w.open()
        
    def searchCallback(self, sender):
        search = sender.get()
        
        newItems = [item for item in self.items if repr(item).startswith(search)]
        self.w.itemList.set(newItems)
        if newItems:
            self.w.itemList.setSelection([0])
        
    def get(self):
        index = self.w.itemList.getSelection()
        if index:
            index = index[0]
            return self.w.itemList[index]
        return None


def AskString(message, value='', title='RoboFab'):
    """
        AskString Dialog
        
        message      the string
        value       a default value
        title       a title of the window (may not be supported everywhere)
    """
    w = _AskStringController(message, value, title)
    return w.get()

def AskYesNoCancel(message, title='RoboFab', default=0, informativeText=""):
    """
        AskYesNoCancel Dialog
        
        message              the string
        title*              a title of the window
                            (may not be supported everywhere)
        default*            index number of which button should be default
                            (i.e. respond to return)
        informativeText*    A string with secundary information

        * may not be supported everywhere
    """
    return vanilla.dialogs.askYesNoCancel(messageText=message, informativeText=informativeText)

def FindGlyph(aFont, message="Search for a glyph:", title='RoboFab'):
    items = aFont.keys()
    items.sort()
    w = _listController(items, message, title, showSearch=True)
    glyphName = w.get()
    if glyphName is not None:
        return aFont[glyphName]
    return None

def GetFile(message=None, title=None, directory=None, fileName=None, allowsMultipleSelection=False, fileTypes=None):
    result = vanilla.dialogs.getFile(messageText=message, title=title, directory=directory, fileName=fileName, allowsMultipleSelection=allowsMultipleSelection, fileTypes=fileTypes)
    if result is None:
        return None
    if not allowsMultipleSelection:
        return str(list(result)[0])
    else:
        return [str(n) for n in list(result)]

def GetFolder(message=None, title=None, directory=None, allowsMultipleSelection=False):
    result = vanilla.dialogs.getFolder(messageText=message, title=title, directory=directory, allowsMultipleSelection=allowsMultipleSelection)
    if result is None:
        return None
    if not allowsMultipleSelection:
        return str(list(result)[0])
    else:
        return [str(n) for n in list(result)]

def GetFileOrFolder(message=None, title=None, directory=None, fileName=None, allowsMultipleSelection=False, fileTypes=None):
    result = vanilla.dialogs.getFileOrFolder(messageText=message, title=title, directory=directory, fileName=fileName, allowsMultipleSelection=allowsMultipleSelection, fileTypes=fileTypes)
    if result is None:
        return None
    if not allowsMultipleSelection:
        return str(list(result)[0])
    else:
        return [str(n) for n in list(result)]

def Message(message, title='RoboFab', informativeText=""):
    vanilla.dialogs.message(messageText=message, informativeText=informativeText)

def OneList(items, message="Select an item:", title='RoboFab'):
    w = _listController(items, message, title, showSearch=False)
    return w.get()

def PutFile(message=None, fileName=None):
    return vanilla.dialogs.putFile(messageText=message, fileName=fileName)

def SearchList(list, message="Select an item:", title='RoboFab'):
    w = _listController(list, message, title, showSearch=True)
    return w.get()

def SelectFont(message="Select a font:", title='RoboFab', allFonts=None):
    if allFonts is None:
        from robofab.world import AllFonts
        fonts = AllFonts()
    else:
        fonts = allFonts
    
    data = dict()
    for font in fonts:
        data["%s" %font] = font
    
    items = data.keys()
    items.sort()
    w = _listController(items, message, title, showSearch=False)
    value = w.get()
    return data.get(value, None)

def SelectGlyph(aFont, message="Select a glyph:", title='RoboFab'):
    items = aFont.keys()
    items.sort()
    w = _listController(items, message, title, showSearch=False)
    glyphName = w.get()
    if glyphName is not None:
        return aFont[glyphName]
    return None

def TwoChecks(title_1="One",  title_2="Two", value1=1, value2=1, title='RoboFab'):
    raise NotImplementedError

def TwoFields(title_1="One:", value_1="0", title_2="Two:", value_2="0", title='RoboFab'):
    raise NotImplementedError


class ProgressBar(object):
    def __init__(self, title="RoboFab...", ticks=None, label=""):
        self.w = vanilla.Window((250, 60), title)
        if ticks is None:
            isIndeterminate = True
            ticks = 0
        else:
            isIndeterminate = False
        self.w.progress = vanilla.ProgressBar((15, 15, -15, 12), maxValue=ticks, isIndeterminate=isIndeterminate, sizeStyle="small")
        self.w.text = vanilla.TextBox((15, 32, -15, 14), label, sizeStyle="small")
        self.w.progress.start()
        self.w.center()
        self.w.open()
    
    def close(self):
        self.w.progress.stop()
        self.w.close()
    
    def getCurrentTick(self):
        return self.w.progress.get()
    
    def label(self, label):
        self.w.text.set(label)
        self.w.text._nsObject.display()
    
    def tick(self, tickValue=None):
        if tickValue is None:
            self.w.progress.increment()
        else:
            self.w.progress.set(tickValue)
    

if __name__ == "__main__":
    pass