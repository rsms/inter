"""
    
    
    Restructured dialogs for Robofab
    
                            dialog          file dialogs
                                
*   FontLab 5.04    10.6    dialogKit       fl internal     * theoretically that should work under windows as well, untested
*   FontLab 5.1     10.6    dialogKit       fl internal
*   FontLab 5.1     10.7    raw cocao       fl internal
    Glyphs          any     vanilla         vanilla
    RoboFont        any     vanilla         vanilla
    
    This module does a fair amount of sniffing in order to guess
    which dialogs to load. Linux and Windows environments are
    underrepresented at the moment. Following the prototypes in dialogs_default.py
    it is possible (with knowledge of the platform) to extend support.
    
    The platformApplicationSupport table contains very specific
    versions with which certain apps need to work. Moving forward,
    it is likely that these versions will change and need to be updated.
    
    # this calls the new dialogs infrastructure:
    from robofab.interface.all.dialogs import Message
    
    # this calls the old original legacy dialogs infrastructure:
    from robofab.interface.all.dialogs_legacy import Message

"""



# determine platform and application
import sys, os
import platform as _platform

__verbose__ = False

platform = None
platformVersion = None
application = None
applicationVersion = None

if sys.platform in (    
        'mac',
        'darwin',
        ):
	platform = "mac"
	v = _platform.mac_ver()[0]
	platformVersion = float('.'.join(v.split('.')[:2]))
elif sys.platform in (
        'linux1',
        'linux2',       # Ubuntu = others?
        ):
    platform = "linux"
elif os.name == 'nt':
	platform = "win"
	
# determine application

try:
    # FontLab
    # alternative syntax to cheat on the FL import filtering in RF
    __import__("FL")
    application = "fontlab"
    #applicationVersion = fl.version
except ImportError:
    pass

if application is None:
    try:
        # RoboFont
        import mojo
        application = 'robofont'
        try:
            from AppKit import NSBundle
            b = NSBundle.mainBundle()
            applicationVersion = b.infoDictionary()["CFBundleVersion"]
        except ImportError:
            pass
    except ImportError:
        pass
    
if application is None:
    try:
        # Glyphs
        import GlyphsApp
        application = "glyphs"
    except ImportError:
        pass

if application is None:
    try:
        # fontforge
        # note that in some configurations, fontforge can be imported in other pythons as well
        # so the availability of the fontforge module is no garuantee that we are in fontforge.
        import fontforge
        application = "fontforge"
    except ImportError:
        pass
        
pyVersion = sys.version_info[:3]

# with that out of the way, perhaps we can have a look at where we are
# and which modules we have available. This maps any number of platform / application
# combinations so an independent list of module names. That should make it 
# possible to map multiple things to one module. 

platformApplicationSupport = [
    # 
    # switchboard for platform, application, python version -> dialog implementations
    # platform  applicatiom     python      sub module
    # |         |               |           |
    ('mac',     'fontlab',      (2,3,5),    "dialogs_fontlab_legacy1"),
    # because FontLab 5.01 and earlier on 2.3.5 can run EasyDialogs
    # |         |               |           |
    # because FontLab 5.1 on mac 10.6 should theoretically be able to run cocoa dialogs,
    # but they are very unreliable. So until we know what's going on, FL5.1 on 10.6
    # is going to have to live with DialogKit dialogs. 
    # |         |               |           |
    ('mac',     'fontlab',      None,       "dialogs_fontlab_legacy2"),
    # because FontLab 5.1 on mac, 10.7+ should run cocoa / vanilla
    # |         |               |           |
    ('mac',     None,           None,       "dialogs_mac_vanilla"),
    # perhaps nonelab scripts can run vanilla as well?
    # |         |               |           |
    ('win',     None,           None,       "dialogs_legacy"),
    # older windows stuff might be able to use the legacy dialogs
]

platformModule = None
foundPlatformModule = False
dialogs = {}

if __verbose__:
    print "robofab.interface.all __init__ - finding out where we were."
 
# do we have a support module?
for pl, app, py, platformApplicationModuleName in platformApplicationSupport:
    if __verbose__:
        print "looking at", pl, app, py, platformApplicationModuleName
    if pl is None or pl == platform:
        if app is None or app == application:
            if py is None or py == pyVersion:
                break
    if __verbose__:
        print "nope"

if __verbose__:
    print "searched for", pl, app, py, platformApplicationModuleName
    
# preload the namespace with default functions that do nothing but raise NotImplementedError
from robofab.interface.all.dialogs_default import *

# now import the module we selected. 
if platformApplicationModuleName == "dialogs_fontlab_legacy1":
    try:
        from robofab.interface.all.dialogs_fontlab_legacy1 import *
        foundPlatformModule = True
        if __verbose__:
            print "loaded robofab.interface.all.dialogs_fontlab_legacy1"
        if platform == "mac":
            from robofab.interface.mac.getFileOrFolder import GetFile, GetFileOrFolder
    except ImportError:
        print "can't import", platformApplicationModuleName

elif platformApplicationModuleName == "dialogs_fontlab_legacy2":
    try:
        from robofab.interface.all.dialogs_fontlab_legacy2 import *
        foundPlatformModule = True
        if __verbose__:
            print "loaded robofab.interface.all.dialogs_fontlab_legacy2"
        if platform == "mac":
            #   
            #
            #
            #
            #
            from robofab.interface.all.dialogs_legacy import AskString, TwoChecks, TwoFields, SelectGlyph, FindGlyph, OneList, SearchList, SelectFont, SelectGlyph
    except ImportError:
        print "can't import", platformApplicationModuleName

elif platformApplicationModuleName == "dialogs_mac_vanilla":
    try:
        from robofab.interface.all.dialogs_mac_vanilla import *
        foundPlatformModule = True
        if __verbose__:
            print "loaded robofab.interface.all.dialogs_mac_vanilla"
    except ImportError:
        print "can't import", platformApplicationModuleName

elif platformApplicationModuleName == "dialogs_legacy":
   try:
       from robofab.interface.all.dialogs_legacy import *
       foundPlatformModule = True
       if __verbose__:
           print "loaded robofab.interface.all.dialogs_legacy"
   except ImportError:
       print "can't import", platformApplicationModuleName
    

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

    
def test():
    """ This is a test that prints the available functions and where they're imported from.
        The report can be useful for debugging.

        For instance:

        from robofab.interface.all.dialogs import test
        test()
        
        testing RoboFab Dialogs:
            python version: (2, 7, 1)
            platform: mac
            application: None
            applicationVersion: None
            platformVersion: 10.7
            looking for module: dialogs_mac_vanilla
                did we find it? True

        Available dialogs and source:
            AskString       robofab.interface.all.dialogs_mac_vanilla
            AskYesNoCancel  robofab.interface.all.dialogs_mac_vanilla
            FindGlyph       robofab.interface.all.dialogs_mac_vanilla
            GetFile         robofab.interface.all.dialogs_mac_vanilla
            GetFolder       robofab.interface.all.dialogs_mac_vanilla
            GetFileOrFolder robofab.interface.all.dialogs_mac_vanilla
            Message         robofab.interface.all.dialogs_mac_vanilla
            OneList         robofab.interface.all.dialogs_mac_vanilla
            PutFile         robofab.interface.all.dialogs_mac_vanilla
            SearchList      robofab.interface.all.dialogs_mac_vanilla
            SelectFont      robofab.interface.all.dialogs_mac_vanilla
            SelectGlyph     robofab.interface.all.dialogs_mac_vanilla
            TwoChecks       robofab.interface.all.dialogs_default
            TwoFields       robofab.interface.all.dialogs_default
            ProgressBar     robofab.interface.all.dialogs_mac_vanilla

    """

    print
    print "testing RoboFab Dialogs:"
    print "\tpython version:", pyVersion
    print "\tplatform:", platform
    print "\tapplication:", application
    print "\tapplicationVersion:", applicationVersion
    print "\tplatformVersion:", platformVersion
    print "\tlooking for module:", platformApplicationModuleName
    print "\t\tdid we find it?", foundPlatformModule
    
    print
    print "Available dialogs and source:"
    for name in __all__:
        if name in globals().keys():
            print "\t", name, "\t", globals()[name].__module__
        else:
            print "\t", name, "\t not loaded."

if __name__ == "__main__":
    test()

