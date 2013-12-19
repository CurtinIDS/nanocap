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

try:
    import PySide
except:pass 
try:
    import py2exe
except:pass    
    
    
def get_sys_exec_root_or_drive():
    path = sys.executable
    while os.path.split(path)[1]:
        path = os.path.split(path)[0]
    return path

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
VER = '1.0.2-alpha'
NAME = 'NanoCap'
APPNAME = '%s-%s' % (NAME, VER)
BUNDLENAME = '%s.app' % NAME
AUTHOR = 'Marc Robinson'
YEAR = 2013
PACKAGE = 'nanocap'
MAINSCRIPT = [os.path.join(PACKAGE,"main.py")]
WIN_TARGET = ""

NON_C_EXTS = ['ext/edip/edip',]
C_EXTS = ['clib/clib',]
EXTENSION_MAKEFILES = ['ext/edip/Makefile.pythonlib',]
C_MAKEFILES = ['clib/Makefile',]

#print "ICN",os.path.abspath('../../icons/NanoCapIcon.ico')

if(PLATFORM == "win"):
    LIB_EXT = "dll"
    WIN_TARGET = { 
                    'script': MAINSCRIPT,
                   #'icon_resources':[(128,'/NanoCapIcon.ico')],
                    'dest_base':  APPNAME                
                  }
else:
    LIB_EXT = "so"


EXTRA_DLLs = ['lib/site-packages/scipy/optimize/minpack2.pyd',
                    'lib/site-packages/numpy/fft/fftpack_lite.pyd',
                    'lib/site-packages/Pythonwin/mfc90.dll']
REQ_DLLS = []
for DLL in EXTRA_DLLs:
    REQ_DLLS.append(os.path.join(sys.prefix, DLL))

REQ_DLLS.append(os.path.join(get_sys_exec_root_or_drive(),"MinGW32-xy","bin","libgcc_s_dw2-1.dll"))
REQ_DLLS.append(os.path.join(get_sys_exec_root_or_drive(),"MinGW32-xy","bin","libgfortran-3.dll"))
REQ_DLLS.append(os.path.join(get_sys_exec_root_or_drive(),"MinGW32-xy","bin","libgmp-10.dll"))
REQ_DLLS.append(os.path.join(get_sys_exec_root_or_drive(),"MinGW32-xy","bin","libgomp-1.dll"))
REQ_DLLS.append(os.path.join(get_sys_exec_root_or_drive(),"MinGW32-xy","bin","libpthread-2.dll"))
REQ_DLLS.append(os.path.join(get_sys_exec_root_or_drive(),"MinGW32-xy","bin","libstdc++-6.dll"))


windows_xml = """
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <assemblyIdentity
    version="""+str(VER)+"""
    processorArchitecture="x86"
    name="""+str(NAME)+"""
    type="win32"
  />
  <description>"""+str(NAME)+"""</description>
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
      <requestedPrivileges>
        <requestedExecutionLevel
            level="asInvoker"
            uiAccess="false">
        </requestedExecutionLevel>
      </requestedPrivileges>
    </security>
  </trustInfo>

</assembly>
"""


class Py2ExeTarget:
    def __init__(self, **kw):
        self.__dict__.update(kw)
        # for the versioninfo resources
        self.version = VER
        #self.company_name = "No Company"
        self.copyright = "Copyright %s 2012-%d" % (AUTHOR, YEAR)
        #self.name = "py2exe sample files"

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
             CFBundleIconFile='../../icons/NanoCapIcon.icns',
             LSPrefersPPC=True
             )



if any([True for e in ['py2app','py2exexe','build','install'] if e in sys.argv]):
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

PY2EXE_OPTIONS = {"dll_excludes": ["MSVCP90.dll",'w9xpopen.exe'],
                  'includes': ['scipy.sparse.csgraph._validation'],
                  "optimize": 2,
                  "compressed":True,
                  "dist_dir":APPNAME,
                  #"bundle_files": 1,
                  #"skip_archive":True,
                  #"packages":['clib','nanocap/ext'],
                  'excludes': ['matplotlib','PyQt4.QtDeclarative',
                               'scipy.weave','PyQt4','sympy',"PIL","TkInter","tcl",
                               'Tkinter', '_tkinter', 'Tkconstants', 'tcl',
                                '_imagingtk', 'PIL._imagingtk', 'ImageTk',
                                'PIL.ImageTk', 'FixTk''_gtkagg', '_tkagg',
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
                          }


PY2APP_OPTIONS =   {'argv_emulation': True,
             'iconfile': '../../icons/NanoCapIcon.icns',
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
                  
elif('py2exe' in sys.argv): 
    REQ = ["py2exe"]
    DATA_FILES = []
#    for EXT in NON_C_EXTS+C_EXTS:
#        DATA_FILES.append(os.path.join(PACKAGE,EXT))
    CDATA = []
    for EXT in C_EXTS:
        CDATA.append(os.path.join(PACKAGE,EXT)+"."+LIB_EXT)
    DATA_FILES.append(('clib',CDATA))
    
    
    for EXT in NON_C_EXTS:
        EXTDATA = []
        EXTDATA.append(os.path.join(PACKAGE,EXT)+"."+LIB_EXT)
        DATA_FILES.append((os.path.dirname(EXT),EXTDATA))
    
   # DATA_FILES = [("clib",['nanocap/clib/clib.dll']),
    #              ("ext/edip",['nanocap/ext/edip/edip.dll'])]
    #DATA_FILES = []
else: 
    REQ = []
    DATA_FILES = []

print "DATA_FILES",DATA_FILES

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
        windows=[Py2ExeTarget(
            script = "nanocap/main.py",
            icon_resources = [(1, os.path.abspath('../../icons/NanoCapIcon.ico'))],
            #other_resources = [(24, 1, windows_xml)],
            dest_base = NAME),],
        #zipfile = None,
        version=VER,
        description='application for the generation of carbon fullerenes and capped nanotubes',
        author='Marc Robinson',
        author_email='marcrobinson85@gmail.com',
        license='CC-NC Creative Commons Non-Commercial',
        app=MAINSCRIPT,
        name=NAME,
        #package_data=PACKAGE_DATA,
        
        data_files=DATA_FILES,
        options={'py2app': PY2APP_OPTIONS,
                 "py2exe":PY2EXE_OPTIONS},      
        packages  = find_packages(exclude= ["tests","build","dist","NanoCap.egg-info","arch"]),
        #ext_modules=[Extension('nanocap.clib.clib', [os.path.join(PACKAGE,"clib/clib.c")])],
        setup_requires=REQ
        )

if('py2exe' in sys.argv):
    for fname in REQ_DLLS:
        path, name = os.path.split(fname)
        print fname, name
        try:
            shutil.copy(fname, os.path.join(APPNAME, name))
        except:
            print "could not copy",fname

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
    
    if('py2exe' in sys.argv):    
        rar = os.path.join(get_sys_exec_root_or_drive(),"\"Program Files\"","WinRAR","Rar.exe")
        os.system(rar+" a -r "+APPNAME+"-win.rar "+APPNAME)
    
    if('py2app' in sys.argv):
        
        os.chdir("dist")
        print "archiving .app ...",os.getcwd(),BUNDLENAME
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
        