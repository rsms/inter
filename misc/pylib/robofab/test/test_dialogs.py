import robofab.interface.all.dialogs
reload(robofab.interface.all.dialogs)
from robofab.interface.all.dialogs import *

import unittest


__all__ = [
    "AskString",            #x
    "AskYesNoCancel",       #x
    "FindGlyph",
    "GetFile",              #x
    "GetFolder",            #x
    "GetFileOrFolder",      #x
    "Message",              #x
    "OneList",
    "PutFile",              #x
    "SearchList",
    "SelectFont",
    "SelectGlyph",
    "TwoChecks",
    "TwoFields",
    "ProgressBar",          
]

class DialogRunner(object):
    def __init__(self):
        prompt = "The prompt for %s."
        message = "The message for %s."
        title = "The title for %s."
        informativeText = "The informative text for %s."
        fileTypes = ['ufo']
        fileName = "The_filename.txt"
        
        self.fonts = fonts = [self.makeTestFont(n) for n in range(4)]
        
        t = "AskString"
        try:
            print "About to try", t
            print "\t>>>", AskString(
                message=prompt%t,
                value='',
                title=title%t
        )
        except NotImplementedError:
            print t, "is not implemented."
        
        t = "AskYesNoCancel"
        try:
            print "About to try", t
            print "\t>>>", AskYesNoCancel(
                message=prompt%t+" default set to 0",
                title=title%t,
                default=0,
                informativeText=informativeText%t
            )
            print "\t>>>", AskYesNoCancel(
                message=prompt%t+" default set to 1",
                title=title%t,
                default=1,
                informativeText=informativeText%t
            )
        except NotImplementedError:
            print t, "is not implemented."
        
        t = "GetFile"
        try:
            print "About to try", t
            print "\t>>>", GetFile(
                message=message%t+" Only fileTypes "+`fileTypes`,
                title=title%t,
                directory=None,
                fileName=fileName,
                allowsMultipleSelection=False,
                fileTypes=fileTypes
            )
            print "\t>>>", GetFile(
                message=message%t+" All filetypes, allow multiple selection.",
                title=title%t,
                directory=None,
                fileName=fileName,
                allowsMultipleSelection=True,
                fileTypes=None
            )
        except NotImplementedError:
            print t, "is not implemented."
        
        t = "GetFolder"
        try:
            print "About to try", t
            print "\t>>>", GetFolder(
                message=message%t,
                title=title%t,
                directory=None,
                allowsMultipleSelection=False
            )
            print "\t>>>", GetFolder(
                message=message%t + " Allow multiple selection.",
                title=title%t,
                directory=None,
                allowsMultipleSelection=True
            )
        except NotImplementedError:
            print t, "is not implemented."
         
        t = "GetFileOrFolder"
        try:
            print "About to try", t
            print "\t>>>", GetFileOrFolder(
                message=message%t+" Only fileTypes "+`fileTypes`,
                title=title%t,
                directory=None,
                fileName=fileName,
                allowsMultipleSelection=False,
                fileTypes=fileTypes
            )
            print "\t>>>", GetFileOrFolder(
                message=message%t + " Allow multiple selection.",
                title=title%t,
                directory=None,
                fileName=fileName,
                allowsMultipleSelection=True,
                fileTypes=None
            )
        except NotImplementedError:
            print t, "is not implemented."
        
        t = "Message"
        try:
            print "About to try", t
            print "\t>>>", Message(
                message=message%t,
                title=title%t,
                informativeText=informativeText%t
            )
        except NotImplementedError:
            print t, "is not implemented."
        
        t = "PutFile"
        try:
            print "About to try", t
            print "\t>>>", PutFile(
                message=message%t,
                fileName=fileName,
            )
        except NotImplementedError:
            print t, "is not implemented."
        
    #   t = "SelectFont"
    #   try:
            #print "About to try", t
    #       print "\t>>>", SelectFont(
    #           message=message%t,
    #           title=title%t,
    #           allFonts=fonts,
    #       )
    #   except NotImplementedError:
    #       print t, "is not implemented."
        
    #   t = 'SelectGlyph'
    #   try:
            #print "About to try", t
    #       print "\t>>>", SelectGlyph(
    #           font=fonts[0],
    #           message=message%t,
    #           title=title%t,
    #       )
    #   except NotImplementedError:
    #       print t, "is not implemented."
    
    print 'No more tests.'
            
    def makeTestFont(self, number):
        from robofab.objects.objectsRF import RFont as _RFont
        f = _RFont()
        f.info.familyName = "TestFamily"
        f.info.styleName = "weight%d"%number
        f.info.postscriptFullName = "%s %s"%(f.info.familyName, f.info.styleName)
        # make some glyphs
        for name in ['A', 'B', 'C']:
            g = f.newGlyph(name)
            pen = g.getPen()
            pen.moveTo((0,0))
            pen.lineTo((500, 0))
            pen.lineTo((500, 800))
            pen.lineTo((0, 800))
            pen.closePath()
        return f


class DialogTests(unittest.TestCase):
    def setUp(self):
        from robofab.interface.all.dialogs import test
        test()
        
    def tearDown(self):
        pass
        
    def testDialogs(self):
        import robofab.interface.all.dialogs
        dialogModuleName = robofab.interface.all.dialogs.platformApplicationModuleName
        application = robofab.interface.all.dialogs.application
        
        if application is None and dialogModuleName == "dialogs_mac_vanilla":
            # in vanilla, but not in a host application, run with executeVanillaTest
            print
            print "I'm running these tests with executeVanillaTest"
            from vanilla.test.testTools import executeVanillaTest
            executeVanillaTest(DialogRunner)
        else:
            print
            print "I'm running these tests natively in"
            DialogRunner()
        

if __name__ == "__main__":
    from robofab.test.testSupport import runTests
    runTests()
