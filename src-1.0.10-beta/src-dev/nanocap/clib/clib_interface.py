'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Oct 23 2013
Copyright Marc Robinson 2013
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

Intface for clib, to ensure consistent
imports
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
'''
from nanocap.core.util import *
from nanocap.core.globals import *
import ctypes,os,sys

#def my_path(path_from_exe=""):
#    if hasattr(sys, "frozen"):
#        exe = os.path.dirname(unicode(sys.executable, sys.getfilesystemencoding( )))
#        return os.path.abspath(exe+path_from_exe)
#    return os.path.dirname(unicode(__file__, sys.getfilesystemencoding( )))

if(PLATFORM=="win"):lib="clib.dll"
else:  lib="clib.so"

#relative_lib = os.path.join(os.path.dirname(get_relative_path(__file__)),lib)

relative_lib = os.path.join(get_root(),"clib","lib",lib)

print "relative_lib",relative_lib
#
#
#if(PLATFORM == "win"):path_relative_to_exe = "/clib"
#elif(PLATFORM == "osx"):path_relative_to_exe = "/../Resources/clib"
#else:path_relative_to_exe = ""
#
#print path_from_file(__file__,path_relative_to_exe)+"/"+lib
#
##clib = ctypes.cdll.LoadLibrary(path_from_file(__file__,path_relative_to_exe)+"/"+lib) 
#
#print os.path.join(get_relative_path(__file__),lib)
#
#print __file__

clib = ctypes.cdll.LoadLibrary(relative_lib)


def scale_points_to_rad(npoints,pos,reqrad,length=None):
    if(length!=None):
       # length = self.processor.nanotube.tubeThomsonPointsCOM[2]*2 
        scale_points_to_cylinder(npoints,pos,reqrad,length)
    else:
        scale_points_to_sphere(npoints,pos,reqrad)
    
def scale_points_to_sphere(npoints,pos,reqrad):                
    clib.scale_rad(ctypes.c_int(npoints),
                   pos.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                   ctypes.c_double(reqrad),
                   ctypes.c_int(0),
                   ctypes.c_double(0.0))  

def scale_points_to_cylinder(npoints,pos,reqrad,length):                
    clib.scale_rad(ctypes.c_int(npoints),
                   pos.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                   ctypes.c_double(reqrad),
                   ctypes.c_int(1),
                   ctypes.c_double(length))  