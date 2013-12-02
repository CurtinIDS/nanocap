'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Oct 23 2013
Copyright Marc Robinson 2013
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

Intface for clib, to ensure consistent
imports
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
'''

from nanocap.core.globals import *
import ctypes,os,sys

def my_path(path_from_exe=""):
    if hasattr(sys, "frozen"):
        exe = os.path.dirname(unicode(sys.executable, sys.getfilesystemencoding( )))
        return os.path.abspath(exe+path_from_exe)
    return os.path.dirname(unicode(__file__, sys.getfilesystemencoding( )))

if(PLATFORM=="win"):lib="clib.dll"
else:  lib="clib.so"
clib = ctypes.cdll.LoadLibrary(my_path(path_from_exe="/../Resources/clib")+"/"+lib) 
