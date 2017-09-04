"""

    Dialogs for FontLab 5.1.
    This might work in future versions of FontLab as well. 
    This is basically a butchered version of vanilla.dialogs.
    No direct import of, or dependency on Vanilla
    
    March 7 2012
    It seems only the dialogs that deal with the file system
    need to be replaced, the other dialogs still work. 
    As we're not entirely sure whether it is worth to maintain
    these dialogs, let's fix the imports in dialogs.py.
    
    This is the phenolic aldehyde version of dialogs.

"""

#__import__("FL")
from FL import *

from Foundation import NSObject
from AppKit import NSApplication, NSInformationalAlertStyle, objc, NSAlert, NSAlertFirstButtonReturn, NSAlertSecondButtonReturn, NSAlertThirdButtonReturn, NSSavePanel, NSOKButton, NSOpenPanel

NSApplication.sharedApplication()

__all__ = [
#    "AskString",
    "AskYesNoCancel",
#    "FindGlyph",
    "GetFile",
    "GetFolder",
	"GetFileOrFolder",
    "Message",
#    "OneList",
    "PutFile",
#    "SearchList",
#    "SelectFont",
#    "SelectGlyph",
#    "TwoChecks",
#    "TwoFields",
    "ProgressBar",
]


class BaseMessageDialog(NSObject):

    def initWithMessageText_informativeText_alertStyle_buttonTitlesValues_window_resultCallback_(self,
            messageText="",
            informativeText="", 
            alertStyle=NSInformationalAlertStyle,
            buttonTitlesValues=None,
            parentWindow=None,
            resultCallback=None):
        if buttonTitlesValues is None:
            buttonTitlesValues = []
        self = super(BaseMessageDialog, self).init()
        self.retain()
        self._resultCallback = resultCallback
        self._buttonTitlesValues = buttonTitlesValues
        #
        alert = NSAlert.alloc().init()
        alert.setMessageText_(messageText)
        alert.setInformativeText_(informativeText)
        alert.setAlertStyle_(alertStyle)
        for buttonTitle, value in buttonTitlesValues:
            alert.addButtonWithTitle_(buttonTitle)
        self._value = None
        code = alert.runModal()
        self._translateValue(code)
        return self

    def _translateValue(self, code):
        if code == NSAlertFirstButtonReturn:
            value = 1
        elif code == NSAlertSecondButtonReturn:
            value = 2
        elif code == NSAlertThirdButtonReturn:
            value = 3
        else:
            value = code - NSAlertThirdButtonReturn + 3
        self._value = self._buttonTitlesValues[value-1][1]

    def windowWillClose_(self, notification):
        self.autorelease()


class BasePutGetPanel(NSObject):

    def initWithWindow_resultCallback_(self, parentWindow=None, resultCallback=None):
        self = super(BasePutGetPanel, self).init()
        self.retain()
        self._parentWindow = parentWindow
        self._resultCallback = resultCallback
        return self

    def windowWillClose_(self, notification):
        self.autorelease()


class PutFilePanel(BasePutGetPanel):

    def initWithWindow_resultCallback_(self, parentWindow=None, resultCallback=None):
        self = super(PutFilePanel, self).initWithWindow_resultCallback_(parentWindow, resultCallback)
        self.messageText = None
        self.title = None
        self.fileTypes = None
        self.directory = None
        self.fileName = None
        self.canCreateDirectories = True
        self.accessoryView = None
        self._result = None
        return self

    def run(self):
        panel = NSSavePanel.alloc().init()
        if self.messageText:
            panel.setMessage_(self.messageText)
        if self.title:
            panel.setTitle_(self.title)
        if self.directory:
            panel.setDirectory_(self.directory)
        if self.fileTypes:
            panel.setAllowedFileTypes_(self.fileTypes)
        panel.setCanCreateDirectories_(self.canCreateDirectories)
        panel.setCanSelectHiddenExtension_(True)
        panel.setAccessoryView_(self.accessoryView)
        if self._parentWindow is not None:
            panel.beginSheetForDirectory_file_modalForWindow_modalDelegate_didEndSelector_contextInfo_(
                    self.directory, self.fileName, self._parentWindow, self, "savePanelDidEnd:returnCode:contextInfo:", 0)
        else:
            isOK = panel.runModalForDirectory_file_(self.directory, self.fileName)
            if isOK == NSOKButton:
                self._result = panel.filename()

    def savePanelDidEnd_returnCode_contextInfo_(self, panel, returnCode, context):
        panel.close()
        if returnCode:
            self._result = panel.filename()
            if self._resultCallback is not None:
                self._resultCallback(self._result)

    savePanelDidEnd_returnCode_contextInfo_ = objc.selector(savePanelDidEnd_returnCode_contextInfo_, signature="v@:@ii")


class GetFileOrFolderPanel(BasePutGetPanel):

    def initWithWindow_resultCallback_(self, parentWindow=None, resultCallback=None):
        self = super(GetFileOrFolderPanel, self).initWithWindow_resultCallback_(parentWindow, resultCallback)
        self.messageText = None
        self.title = None
        self.directory = None
        self.fileName = None
        self.fileTypes = None
        self.allowsMultipleSelection = False
        self.canChooseDirectories = True
        self.canChooseFiles = True
        self.resolvesAliases = True
        self._result = None
        return self

    def run(self):
        panel = NSOpenPanel.alloc().init()
        if self.messageText:
            panel.setMessage_(self.messageText)
        if self.title:
            panel.setTitle_(self.title)
        if self.directory:
            panel.setDirectory_(self.directory)
        if self.fileTypes:
            panel.setAllowedFileTypes_(self.fileTypes)
        panel.setCanChooseDirectories_(self.canChooseDirectories)
        panel.setCanChooseFiles_(self.canChooseFiles)
        panel.setAllowsMultipleSelection_(self.allowsMultipleSelection)
        panel.setResolvesAliases_(self.resolvesAliases)
        if self._parentWindow is not None:
            panel.beginSheetForDirectory_file_types_modalForWindow_modalDelegate_didEndSelector_contextInfo_(
                    self.directory, self.fileName, self.fileTypes, self._parentWindow, self, "openPanelDidEnd:returnCode:contextInfo:", 0)
        else:
            isOK = panel.runModalForDirectory_file_types_(self.directory, self.fileName, self.fileTypes)
            if isOK == NSOKButton:
                self._result = panel.filenames()

    def openPanelDidEnd_returnCode_contextInfo_(self, panel, returnCode, context):
        panel.close()
        if returnCode:
            self._result = panel.filenames()
            if self._resultCallback is not None:
                self._resultCallback(self._result)

    openPanelDidEnd_returnCode_contextInfo_ = objc.selector(openPanelDidEnd_returnCode_contextInfo_, signature="v@:@ii")


def Message(message="", title='noLongerUsed', informativeText=""):
    """Legacy robofab dialog compatible wrapper."""
    #def _message(messageText="", informativeText="", alertStyle=NSInformationalAlertStyle, parentWindow=None, resultCallback=None):
    resultCallback = None
    alert = BaseMessageDialog.alloc().initWithMessageText_informativeText_alertStyle_buttonTitlesValues_window_resultCallback_(
                messageText=message,
                informativeText=informativeText,
                alertStyle=NSInformationalAlertStyle,
                buttonTitlesValues=[("OK", 1)],
                parentWindow=None,
                resultCallback=None)
    if resultCallback is None:
        return 1


def AskYesNoCancel(message, title='noLongerUsed', default=None, informativeText=""):
    """
        AskYesNoCancel Dialog
        
        message             the string
        title*              a title of the window
                            (may not be supported everywhere)
        default*            index number of which button should be default
                            (i.e. respond to return)
        informativeText*    A string with secundary information

        * may not be supported everywhere
    """
    parentWindow = None
    alert = BaseMessageDialog.alloc().initWithMessageText_informativeText_alertStyle_buttonTitlesValues_window_resultCallback_(
        messageText=message,
        informativeText=informativeText,
        alertStyle=NSInformationalAlertStyle,
        buttonTitlesValues=[("Cancel", -1), ("Yes", 1), ("No", 0)],
        parentWindow=None,
        resultCallback=None)
    return alert._value

def _askYesNo(messageText="", informativeText="", alertStyle=NSInformationalAlertStyle, parentWindow=None, resultCallback=None):
    parentWindow = None
    alert = BaseMessageDialog.alloc().initWithMessageText_informativeText_alertStyle_buttonTitlesValues_window_resultCallback_(
        messageText=messageText, informativeText=informativeText, alertStyle=alertStyle, buttonTitlesValues=[("Yes", 1), ("No", 0)], parentWindow=parentWindow, resultCallback=resultCallback)
    if resultCallback is None:
        return alert._value

def GetFile(message=None, title=None, directory=None, fileName=None, allowsMultipleSelection=False, fileTypes=None):
    """ Legacy robofab dialog compatible wrapper.
        This will select UFO on OSX 10.7, FL5.1
    """
    parentWindow = None
    resultCallback=None
    basePanel = GetFileOrFolderPanel.alloc().initWithWindow_resultCallback_(parentWindow, resultCallback)
    basePanel.messageText = message
    basePanel.title = title
    basePanel.directory = directory
    basePanel.fileName = fileName
    basePanel.fileTypes = fileTypes
    basePanel.allowsMultipleSelection = allowsMultipleSelection
    basePanel.canChooseDirectories = False
    basePanel.canChooseFiles = True
    basePanel.run()
    if basePanel._result is None:
        return None
    if not allowsMultipleSelection:
        # compatibly return only one as we expect
        return str(list(basePanel._result)[0])
    else:
        # return more if we explicitly expect
        return [str(n) for n in list(basePanel._result)]

def GetFolder(message=None, title=None, directory=None, allowsMultipleSelection=False):
    parentWindow = None
    resultCallback = None
    basePanel = GetFileOrFolderPanel.alloc().initWithWindow_resultCallback_(parentWindow, resultCallback)
    basePanel.messageText = message
    basePanel.title = title
    basePanel.directory = directory
    basePanel.allowsMultipleSelection = allowsMultipleSelection
    basePanel.canChooseDirectories = True
    basePanel.canChooseFiles = False
    basePanel.run()
    if basePanel._result is None:
        return None
    if not allowsMultipleSelection:
        # compatibly return only one as we expect
        return str(list(basePanel._result)[0])
    else:
        # return more if we explicitly expect
        return [str(n) for n in list(basePanel._result)]

def GetFileOrFolder(message=None, title=None, directory=None, fileName=None, allowsMultipleSelection=False, fileTypes=None, parentWindow=None, resultCallback=None):
    parentWindow = None
    basePanel = GetFileOrFolderPanel.alloc().initWithWindow_resultCallback_(parentWindow, resultCallback)
    basePanel.messageText = message
    basePanel.title = title
    basePanel.directory = directory
    basePanel.fileName = fileName
    basePanel.fileTypes = fileTypes
    basePanel.allowsMultipleSelection = allowsMultipleSelection
    basePanel.canChooseDirectories = True
    basePanel.canChooseFiles = True
    basePanel.run()
    if basePanel._result is None:
        return None
    if not allowsMultipleSelection:
        # compatibly return only one as we expect
        return str(list(basePanel._result)[0])
    else:
        # return more if we explicitly expect
        return [str(n) for n in list(basePanel._result)]

def PutFile(message=None, title=None, directory=None, fileName=None, canCreateDirectories=True, fileTypes=None):
    parentWindow = None
    resultCallback=None
    accessoryView=None
    basePanel = PutFilePanel.alloc().initWithWindow_resultCallback_(parentWindow, resultCallback)
    basePanel.messageText = message
    basePanel.title = title
    basePanel.directory = directory
    basePanel.fileName = fileName
    basePanel.fileTypes = fileTypes
    basePanel.canCreateDirectories = canCreateDirectories
    basePanel.accessoryView = accessoryView
    basePanel.run()
    return str(basePanel._result)


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


# we seem to have problems importing from here.
# so let's see what happens if we make the robofab compatible wrappers here as well.

# start with all the defaults. 

#def AskString(message, value='', title='RoboFab'):
#    raise NotImplementedError

#def FindGlyph(aFont, message="Search for a glyph:", title='RoboFab'):
#    raise NotImplementedError

#def OneList(list, message="Select an item:", title='RoboFab'):
#    raise NotImplementedError
    
#def PutFile(message=None, fileName=None):
#    raise NotImplementedError

#def SearchList(list, message="Select an item:", title='RoboFab'):
#    raise NotImplementedError

#def SelectFont(message="Select a font:", title='RoboFab'):
#    raise NotImplementedError

#def SelectGlyph(font, message="Select a glyph:", title='RoboFab'):
#    raise NotImplementedError

#def TwoChecks(title_1="One",  title_2="Two", value1=1, value2=1, title='RoboFab'):
#    raise NotImplementedError

#def TwoFields(title_1="One:", value_1="0", title_2="Two:", value_2="0", title='RoboFab'):
#    raise NotImplementedError

