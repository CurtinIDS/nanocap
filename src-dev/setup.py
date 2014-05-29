'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Oct 23 2013
Copyright Marc Robinson 2013
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

NanoCap setup script.
Options:

build 
install
sdist
build archive - create tar.gz/bz2
py2app - create .app
py2app archive - create dmg + tar.gz/bz2
py2exe - create .exe
py2exe archive - create .rar


Note to self: 
must create configure scripts for the clibs
and ext modules. Use autoreconf using the 
configure.ac and Makefile.am files.


Copies Docs from ../../docs to docs

Bundles:
    bin
    example scripts
    docs
    
    
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


ARGVEMU = False
PVER = "2.7"
VER = '1.0b10'
NAME = 'NanoCap'
APPNAME = '%s-%s' % (NAME, VER)
BUNDLENAME = '%s.app' % NAME
AUTHOR = 'Marc Robinson'
YEAR = 2014
PACKAGE = 'nanocap'
MAINSCRIPT = [os.path.join(PACKAGE,"main.py")]
WIN_TARGET = ""

INSTALL_REQ = ["numpy >= 1.6.2",
               "scipy >= 0.11.0",
               "docutils >= 0.11"]

WINDOWS_OPTIONS = []
PY2APP_OPTIONS = {}
PY2EXE_OPTIONS = {}
SETUP_REQ = []
DATA_FILES = []
DATA_FILES = ['docs',]

F_EXTS = ['ext/edip/lib/edip',]
C_EXTS = ['clib/lib/clib',]
C_EXTS_BUILD = [('clib','make clean; ./configure; make; make install'),]
F_EXTS_BUILD = [('ext/edip/','make clean; ./configure; make; make install'),]

if(PLATFORM == "win"):
    LIB_EXT = "dll"
    WIN_TARGET = { 'script': MAINSCRIPT,
                   #'icon_resources':[(128,'/NanoCapIcon.ico')],
                    'dest_base':  APPNAME                
                  }
else:
    LIB_EXT = "so" 


def main():
    
    copy_docs()
    
    set_req_windows_dlls()
    
    setup_package_data(['help',])
    
    if any([True for e in ['build','install'] if e in sys.argv]): 
        chmod_build_dir()
        #raw_input()
    if any([True for e in ['py2app','py2exexe','build','install'] if e in sys.argv]):    
        build_extensions()
        #raw_input()
    
    print "find_packages()",find_packages()
    
    if('py2exe' in sys.argv):pre_build_py2exe()
    
    if('py2app' in sys.argv):pre_build_py2app()
    
    if any([True for e in ['py2app','py2exe'] if e in sys.argv]): 
        setup_data_files()
    
    if any([True for e in ['build','install'] if e in sys.argv]): 
        copy_ext_to_build_dir()
        #raw_input()
    
    setup_main()
    
    if('py2exe' in sys.argv):post_build_py2exe()
    
    if('py2app' in sys.argv):post_build_py2app()
    
    if('archive' in CUSTOM_ARGS):archive()

def copy_docs():
    try:shutil.rmtree("docs")
    except:print "old docs not found, copying new docs"
    shutil.copytree(os.path.abspath("../../docs/html/docs"),os.getcwd()+"/docs/html")
    shutil.copy(os.path.abspath("../../docs/tex/Doc.pdf"),os.getcwd()+"/docs/NanoCap.pdf")
    #shutil.move('docstemp',os.path.abspath("../../dev/src-dev/nanocap/help/docs"))


def setup_package_data(folders):
    global PACKAGE_DATA
    PDATA = []
    os.chdir('nanocap')
    for folder in folders:
        for root,dir,files in  os.walk(folder):
            for file in files:
                print root,dir,file
                print os.path.join(root,file)
                PDATA.append(os.path.join(root,file))
    os.chdir('../')          
    PACKAGE_DATA = {PACKAGE: PDATA}


def set_req_windows_dlls():
    global EXTRA_DLLs,REQ_DLLS
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


def pre_build_py2exe():   
    global PY2EXE_OPTIONS,SETUP_REQ,WINDOWS_OPTIONS
    class Py2ExeTarget:
        def __init__(self, **kw):
            self.__dict__.update(kw)
            # for the versioninfo resources
            self.version = VER
            #self.company_name = "No Company"
            self.copyright = "Copyright %s 2012-%d" % (AUTHOR, YEAR)
    
    WINDOWS_OPTIONS=[Py2ExeTarget(
                    script = "nanocap/main.py",
                    icon_resources = [(1, os.path.abspath('../../icons/NanoCapIcon.ico'))],
                    #other_resources = [(24, 1, windows_xml)],
                    dest_base = NAME),]
        
    SETUP_REQ = ["py2exe"]
    PY2EXE_OPTIONS = {"dll_excludes": ["MSVCP90.dll",'w9xpopen.exe'],
                      'includes': ['scipy.sparse.csgraph._validation',
                                   'PySide.QtCore', 'PySide.QtGui', 'PySide.QtWebKit', 'PySide.QtNetwork'],
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
                                  'Carbon'],
                              }

def pre_build_py2app():
    global PY2APP_OPTIONS,SETUP_REQ
    SETUP_REQ = ["py2app"]     
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
       
    PY2APP_OPTIONS =   {'argv_emulation': ARGVEMU,
                 'iconfile': '../../icons/NanoCapIcon.icns',
                 'includes': ['PySide.QtCore', 'PySide.QtGui', 'PySide.QtWebKit', 'PySide.QtNetwork'],#'sip', 'PySide','vtk','numpy','scipy.optimize','scipy.special'],
                 'excludes': ['matplotlib','PyQt4.QtDeclarative','scipy.weave','PyQt4','sympy',"PIL",
                              'Carbon'],
                 'packages': [],
                 'plist':    PLIST 
                 }

def setup_data_files():
    global DATA_FILES
    DATA_FILES = []
    '''
    So we only data files when using py2app so it puts them in /Resources not in the
    zipped site-packages.zip. This way we can access them when an .app.
    
    '''
    
    DATA_FILES = [(os.path.join('example_scripts'),glob.glob(os.path.join("example_scripts")+"/*.py")),
                  (os.path.join('help'),glob.glob(os.path.join("nanocap/help")+"/*"))]
    
    CDATA = []
    for EXT in C_EXTS:
        CDATA.append(os.path.join(PACKAGE,EXT)+"."+LIB_EXT)
    #DATA_FILES.append((os.path.join(PACKAGE,EXT),CDATA))
    DATA_FILES.append((os.path.dirname(EXT),CDATA))
    
    EXTDATA = []
    for EXT in F_EXTS:
        EXTDATA.append(os.path.join(PACKAGE,EXT)+"."+LIB_EXT)
    DATA_FILES.append((os.path.dirname(EXT),EXTDATA))
    print "DATA_FILES",DATA_FILES

def copy_ext_to_build_dir():   
    for EXT in F_EXTS+C_EXTS:
        FULL_PATH = os.path.abspath(os.path.join(PACKAGE,EXT))+"."+LIB_EXT
        BUILD_PATH = os.path.join('build', distutils_dir_name('lib'),os.path.join(PACKAGE,EXT))+"."+LIB_EXT
        LOC = os.path.dirname(FULL_PATH)
        BUILD_LOC= os.path.dirname(BUILD_PATH)
        try:
            os.makedirs(BUILD_LOC)
            print "mkdir",BUILD_LOC
        except:pass
       
        print "copying lib from: ",FULL_PATH
        print "copying lib to: ",BUILD_PATH 
        shutil.copyfile(FULL_PATH,BUILD_PATH)

def setup_main():
    setup(
            windows=WINDOWS_OPTIONS,
            #zipfile = None,
            version=VER,
            description='Application and libraries for the generation of carbon fullerenes, nanotubes and capped nanotubes',
            long_description=open('README.txt').read(),
            author='Marc Robinson',
            author_email='marcrobinson85@gmail.com',
            license='CC-NC Creative Commons Non-Commercial',
            app=MAINSCRIPT,
            name=NAME,
            #package_data=PACKAGE_DATA,
            url='http://sourceforge.net/projects/nanocap/',
            scripts=glob.glob("bin/*"),
            data_files=DATA_FILES,
            options={'py2app': PY2APP_OPTIONS,
                     "py2exe":PY2EXE_OPTIONS},      
            packages  = find_packages(exclude= ["tests","build","dist","NanoCap.egg-info","arch"]),
            package_data= PACKAGE_DATA, 
            include_package_data=True,
            #ext_modules=[Extension('nanocap.clib.clib', [os.path.join(PACKAGE,"clib/clib.c")])],
            setup_requires=SETUP_REQ,
            install_requires=INSTALL_REQ
                
            )

def post_build_py2exe():

    for fname in REQ_DLLS:
        path, name = os.path.split(fname)
        print fname, name
        try:
            shutil.copy(fname, os.path.join(APPNAME, name))
        except:
            print "could not copy",fname

def post_build_py2app():

    if('py2app' in sys.argv):
    
        DIST    = os.path.join(os.getcwd(),'dist')
        BUNDLELOC = os.path.join(DIST, BUNDLENAME, 'Contents')
        
        print "BUNDLELOC",BUNDLELOC
        
        for num,line in enumerate(fileinput.input(BUNDLELOC+'/Resources/__boot__.py', inplace=1)):
          if not ARGVEMU:
              if num == 0 :
                  print "import sys,os \nsys.path = [os.path.join(os.environ['RESOURCEPATH'], 'lib', 'python"+PVER+"', 'lib-dynload')] + [os.environ['RESOURCEPATH'],] + sys.path \n"
              print line,
          else:    
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




    
def archive():
    if('build' in sys.argv):
        FOLDERS = ["licenses","nanocap","INSTALL.txt","README.txt","setup.py","docs"]#,os.path.abspath("../../user_scripts")]
        print "archiving source ..."
        os.system("tar -cf "+str(APPNAME)+".tar "+" ".join(FOLDERS))
        #os.system("tar -rf "+str(APPNAME)+".tar "+" -C "+os.path.abspath("../../")+" user_scripts")
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
        DMGFILES = ["licenses","README.txt","INSTALL.txt", "docs"]
        for DF in DMGFILES:
            os.system("cp -rf ../"+DF+" "+APPNAME+"/")
        #os.system("cp -rf ../README "+APPNAME+"/")
        #os.system("cp -rf ../INSTALL.txt "+APPNAME+"/")
        os.system("cp -rf "+str(BUNDLENAME)+" "+APPNAME+"/")
        
        os.system("rm -rf "+APPNAME+".dmg*")
        os.system("hdiutil create "+APPNAME+".dmg -srcfolder "+APPNAME+"/")# .join(FOLDERS))

        print "archiving .dmg ..."
        os.system("tar -zcf "+str(APPNAME)+".dmg.tar.gz "+APPNAME+".dmg")
        os.system("tar -jcf "+str(APPNAME)+".dmg.tar.bz2 "+APPNAME+".dmg")
        os.system("rm -rf dmg-tmp")
        os.chdir("../")
      
        
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

def build_extensions():
    print "building extensions..."
    WD = os.path.dirname(os.path.abspath(__file__))
    for CLOC, BUILD_COMMAND in C_EXTS_BUILD:
        FULL_PATH = os.path.abspath(os.path.join(PACKAGE,CLOC))
        #LOC = os.path.dirname(FULL_PATH)
        os.chdir(FULL_PATH)
        print CLOC,FULL_PATH,os.getcwd()
        #raw_input()
        os.system(BUILD_COMMAND) 
        os.chdir(WD)
        
    for CLOC, BUILD_COMMAND in F_EXTS_BUILD:
        FULL_PATH = os.path.abspath(os.path.join(PACKAGE,CLOC))
        #LOC = os.path.dirname(FULL_PATH)
        os.chdir(FULL_PATH)
        print CLOC,FULL_PATH,os.getcwd()
        #raw_input()
        os.system(BUILD_COMMAND) 
        os.chdir(WD) 

def chmod_build_dir():
    print "chmod","chmod -R 775 {}".format('build'),os.getcwd()
#if any([True for e in ['build','install'] if e in sys.argv]): 
    #print "chmod -R 775 {}".format(os.path.join('build', distutils_dir_name('lib')))
    #os.system("chmod -R 775 {}".format(os.path.join('build', distutils_dir_name('lib'))))
    os.system("chmod -R 775 {}".format('build'))                
    
    
def set_windows_xml():

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
               

if __name__=="__main__":
    main()

  