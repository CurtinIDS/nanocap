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
import os,sys,sysconfig
from plistlib import Plist
import PySide

def distutils_dir_name(dname):
    """Returns the name of a distutils build directory"""
    f = "{dirname}.{platform}-{version[0]}.{version[1]}"
    return f.format(dirname=dname,
                    platform=sysconfig.get_platform(),
                    version=sys.version_info)
    
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

NON_C_EXTS = [os.path.join(PACKAGE,'ext','edip','edip.so'),]
EXTENSION_MAKEFILES = [os.path.join(PACKAGE,'ext','edip','Makefile.pythonlib'),]

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
    for MAKEFILE in EXTENSION_MAKEFILES:
        print "building ",MAKEFILE,os.path.dirname(os.path.abspath(MAKEFILE))
        os.chdir(os.path.dirname(os.path.abspath(MAKEFILE)))
        print os.getcwd()
        os.system('make -f '+os.path.basename(os.path.abspath(MAKEFILE)))
        os.chdir(WD)
        print os.getcwd()
           #   '../src/icons']

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

    for EXT in NON_C_EXTS:
        try:
            print "mkdir",os.path.dirname(os.path.join('build', distutils_dir_name('lib'),EXT))
            os.makedirs(os.path.dirname(os.path.join('build', distutils_dir_name('lib'),EXT)))
        except:pass    
        BD = os.path.join('build', distutils_dir_name('lib'),EXT)
        print ("cp %s %s") % (EXT,BD)
        os.system(("cp %s %s") % (EXT,BD))

setup(
        version=VER,
        description='application for the generation of carbon fullerenes and capped nanotubes',
        author='Marc Robinson',
        author_email='marcrobinson85@gmail.com',
        license='CC-NC Creative Commons Non-Commercial',
        app=MAINSCRIPT,
        name=NAME,
        data_files=DATA_FILES,
        options={'py2app': PY2APP_OPTIONS},
        packages  = find_packages(exclude= ["tests","build","dist","NanoCap.egg-info","arch"]),
        ext_modules=[Extension('nanocap.clib.clib', [os.path.join(PACKAGE,"clib/clib.c")])],
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
        FOLDERS = ["docs","nanocap","INSTALL","README","setup.py","../../user_scripts"]
        print "archiving source ..."
        os.system("tar -zcf "+str(APPNAME)+".tar.gz "+" ".join(FOLDERS))
        os.system("tar -jcf "+str(APPNAME)+".tar.bz2 "+" ".join(FOLDERS))
    
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
        