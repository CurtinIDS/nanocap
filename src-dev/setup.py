'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Oct 23 2013
Copyright Marc Robinson 2013
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

NanoCap setup script.
Options:

build 
install
build archive - create tar.gz/bz2
py2app - create .app
py2app archive - create dmg + tar.gz/bz2

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
'''

from setuptools import setup,Extension,find_packages
import fileinput
import glob 
import os,sys,sysconfig,shutil,platform
from plistlib import Plist
import PySide


def distutils_dir_name(dname):
    """Returns the name of a distutils build directory
       If no extensions then will be seen as pure python
       module and will not have platform dependent build folder"""
    return dname
#    f = "{dirname}.{platform}-{version[0]}.{version[1]}"
#    print "distutils dir", f.format(dirname=dname,
#                    platform=sysconfig.get_platform(),
#                    version=sys.version_info)
#    raw_input()
#    return f.format(dirname=dname,
#                    platform=sysconfig.get_platform(),
#                    version=sys.version_info)
                
                    
ps = platform.system()
if(ps=="Darwin"):PLATFORM = "osx"
if(ps=="Windows"):PLATFORM = "win"
if(ps=="Linux"):PLATFORM = "linux"
    
SETUP_TOOLS_ARGS = []
CUSTOM_ARGS = []
for arg in sys.argv:
    if arg == "archive":CUSTOM_ARGS.append(arg)
    else:SETUP_TOOLS_ARGS.append(arg)
sys.argv = SETUP_TOOLS_ARGS        

PVER = "2.7"
VER = '1.0-alpha'
NAME = 'NanoCap'
APPNAME = '%s-%s' % (NAME, VER)
BUNDLENAME = '%s.app' % NAME
AUTHOR = 'Marc Robinson'
YEAR = 2013
PACKAGE = 'nanocap'
MAINSCRIPT = [os.path.join(PACKAGE,"main.py")]


NON_C_EXTS = ['ext/edip/edip',]
C_EXTS = ['clib/clib',]
EXTENSION_MAKEFILES = ['ext/edip/Makefile.pythonlib',]
C_MAKEFILES = ['clib/Makefile',]

if(PLATFORM == "win"):
    LIB_EXT = "dll"
else:
    LIB_EXT = "so"

#PACKAGE_DATA = {PACKAGE: NON_C_EXTS + C_EXTS}
#
#print "PACKAGE_DATA",PACKAGE_DATA
#raw_input()

PLIST = dict(CFBundleName = NAME,
             CFBundleShortVersionString = VER,
             CFBundleGetInfoString = NAME + " " + VER,
             CFBundleExecutable = NAME + " " + VER,
             CFBundleIdentifier = "org.drmrapps.%s" % NAME,
             CFBundleDevelopmentRegion = 'English',
             NSHumanReadableCopyright = u"Copyright %s 2012-%d" % (AUTHOR, YEAR),
             CFBundleIconFile='../icons/NanoCapIcon.icns',
             LSPrefersPPC=True
             )



if any([True for e in ['py2app','build','install'] if e in sys.argv]):
    WD = os.path.dirname(os.path.abspath(__file__))
    for MAKEFILE in EXTENSION_MAKEFILES+C_MAKEFILES:
        FULL_PATH = os.path.abspath(os.path.join(PACKAGE,MAKEFILE))
        LOC = os.path.dirname(FULL_PATH)
        print "building ",LOC,FULL_PATH,PLATFORM
        os.chdir(LOC)
        print os.getcwd()
        os.system('make -f '+os.path.basename(FULL_PATH)+' '+PLATFORM)
        os.chdir(WD)
        print os.getcwd()


PY2APP_OPTIONS =   {'argv_emulation': True,
             'iconfile': '../icons/NanoCapIcon.icns',
             'includes': [],#'sip', 'PySide','vtk','numpy','scipy.optimize','scipy.special'],
             'excludes': ['matplotlib','PyQt4.QtDeclarative','scipy.weave','PyQt4','sympy',"PIL",
                          'Carbon',
                          'PyQt4.QtDesigner',
                          'PyQt4.QtHelp',
                          'PyQt4.QtNetwork',
                          'PyQt4.QtMultimedia',
                          'PyQt4.QtScript',
                          'PyQt4.QtScriptTools',
                          'PyQt4.QtSql',
                          'PyQt4.QtTest',
                          'PyQt4.QtWebKit',
                          'PyQt4.QtXml',
                          'PyQt4.QtXmlPatterns'],
             'packages': [],
             'plist':    PLIST 
             }

print "find_packages()",find_packages()

if('py2app' in sys.argv): 
    REQ = ["py2app"]
    DATA_FILES = ['nanocap/clib', 
                  'nanocap/ext'] 
else: 
    REQ = []
    DATA_FILES = []

if any([True for e in ['build','install'] if e in sys.argv]):    
    for EXT in NON_C_EXTS+C_EXTS:
        FULL_PATH = os.path.abspath(os.path.join(PACKAGE,EXT))+"."+LIB_EXT
        BUILD_PATH = os.path.join('build', distutils_dir_name('lib'),os.path.join(PACKAGE,EXT))+"."+LIB_EXT
        LOC = os.path.dirname(FULL_PATH)
        BUILD_LOC= os.path.dirname(BUILD_PATH)
        try:
            print "mkdir",BUILD_LOC
            os.makedirs(BUILD_LOC)
        except:pass
        print "BUILD_PATH",BUILD_PATH
        print "FULL_PATH",FULL_PATH
        shutil.copyfile(FULL_PATH,BUILD_PATH)


setup(
        version=VER,
        description='application for the generation of carbon fullerenes and capped nanotubes',
        author='Marc Robinson',
        author_email='marcrobinson85@gmail.com',
        license='CC-NC Creative Commons Non-Commercial',
        app=MAINSCRIPT,
        name=NAME,
        #package_data=PACKAGE_DATA,
        data_files=DATA_FILES,
        options={'py2app': PY2APP_OPTIONS},
        packages  = find_packages(exclude= ["tests","build","dist","NanoCap.egg-info","arch"]),
        #ext_modules=[Extension('nanocap.clib.clib', [os.path.join(PACKAGE,"clib/clib.c")])],
        setup_requires=REQ
        )


if('py2app' in sys.argv):

    DIST    = os.path.join(os.getcwd(),'dist')
    BUNDLELOC = os.path.join(DIST, BUNDLENAME, 'Contents')
    
    print "BUNDLELOC",BUNDLELOC
    
    for num,line in enumerate(fileinput.input(BUNDLELOC+'/Resources/__boot__.py', inplace=1)):
      if num == 29 :
          print "sys.path = [os.path.join(os.environ['RESOURCEPATH'], 'lib', 'python"+PVER+"', 'lib-dynload')] + [os.environ['RESOURCEPATH'],] + sys.path \n"
      print line,
    
    
    
    FRAMEWORKS = ["libvtkInfovis.5.8.0.dylib",
                  "libvtkInfovisPythonD.5.8.0.dylib",
                  "libvtklibxml2.5.8.0.dylib",]
    #              "libvtkCharts.5.8.0.dylib",
    #              "libvtkChartsPythonD.5.8.0.dylib",
    #              "libvtkDICOMParser.5.8.0.dylib",
    #              "libvtkGeovis.5.8.0.dylib",
    #              "libvtkGeovisPythonD.5.8.0.dylib",
    #              "libvtkHybrid.5.8.0.dylib",
    #              "libvtkHybridPythonD.5.8.0.dylib"]
    
    PYMODS = ["scipy/weave",
                "scipy/interpolate",
                "scipy/io",
                "scipy/maxentropy",
                "scipy/ndimage",
                "scipy/odr",
                "scipy/signal",
                "scipy/spatial",
                "scipy/stats"]
    
    
    
    print "FRAMEWORKS",os.path.join(BUNDLELOC,"Frameworks")
    print "LIB",os.path.join(BUNDLELOC,"Resources","lib","python"+PVER)
    for F in FRAMEWORKS: os.system("rm -rf "+os.path.join(BUNDLELOC,"Frameworks",F))
    for P in PYMODS: os.system("rm -rf "+os.path.join(BUNDLELOC,"Resources","lib","python"+PVER,P))


if('archive' in CUSTOM_ARGS):
    if('build' in sys.argv):
        FOLDERS = ["docs","nanocap","INSTALL","README","setup.py"]#,os.path.abspath("../../user_scripts")]
        print "archiving source ..."
        os.system("tar -cf "+str(APPNAME)+".tar "+" ".join(FOLDERS))
        os.system("tar -rf "+str(APPNAME)+".tar "+" -C "+os.path.abspath("../../")+" user_scripts")
        os.system("gzip < "+str(APPNAME)+".tar > "+str(APPNAME)+".tar.gz")
        os.system("bzip2 "+str(APPNAME)+".tar")
        #os.system("tar -zcf "+str(APPNAME)+".tar.gz "+" ".join(FOLDERS))
        #os.system("tar -jcf "+str(APPNAME)+".tar.bz2 "+" ".join(FOLDERS))
    
    if('py2app' in sys.argv):
        
        os.chdir("dist")
        print "archiving .app ...",os.getcwd(),BUNDLENAME+".app"
        os.system("tar -zcf "+str(APPNAME)+".app.tar.gz "+BUNDLENAME)
        os.system("tar -jcf "+str(APPNAME)+".app.tar.bz2 "+BUNDLENAME)
        
        print "creating dmg ..."
        os.system("rm -rf "+APPNAME)
        os.makedirs(APPNAME)
        DMGFILES = ["docs","README","INSTALL"]
        for DF in DMGFILES:
            os.system("cp -rf ../"+DF+" "+APPNAME+"/")
        #os.system("cp -rf ../README "+APPNAME+"/")
        #os.system("cp -rf ../INSTALL "+APPNAME+"/")
        os.system("cp -rf "+str(BUNDLENAME)+" "+APPNAME+"/")
        
        os.system("rm -rf "+APPNAME+".dmg*")
        os.system("hdiutil create "+APPNAME+".dmg -srcfolder "+APPNAME+"/")# .join(FOLDERS))

        print "archiving .dmg ..."
        os.system("tar -zcf "+str(APPNAME)+".dmg.tar.gz "+APPNAME+".dmg")
        os.system("tar -jcf "+str(APPNAME)+".dmg.tar.bz2 "+APPNAME+".dmg")
        os.system("rm -rf dmg-tmp")
        os.chdir("../")
        