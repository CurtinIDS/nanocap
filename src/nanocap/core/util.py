'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Nov 17 2011
Copyright Marc Robinson 2013
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

util functions

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
'''

from nanocap.core.globals import *
from nanocap.core import globals
import sys,os,random,math,time,inspect
from collections import defaultdict

import numpy

from nanocap.core.globals import QT
QtGui, QtCore, QtOpenGL = QT.QtGui, QT.QtCore, QT.QtOpenGL

#clib = ctypes.cdll.LoadLibrary(ROOTDIR+"/clib/clib.so") 

from nanocap.clib import clib_interface
clib = clib_interface.clib

uniqueMask = numpy.zeros(9999,int)
uniqueInputMask = numpy.zeros(9999,int)
outputWidget = None

def module_path():
    if hasattr(sys, "frozen"):
        return os.path.dirname(unicode(sys.executable, sys.getfilesystemencoding( )))
    return os.path.dirname(unicode(__file__, sys.getfilesystemencoding( )))

def waitGUIlock():
    time.sleep(0.1)
    while(globals.GUIlock):
        printl("awaiting globals.GUIlock=False",globals.GUIlock)
        time.sleep(0.1)
    printl("ending globals.GUIlock=False",globals.GUIlock)    

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


def get_centered_string(fmt,length,args):
    args = map(str,args)
    slength=0
    for arg in args:slength+=len(arg)+1
    
    if(length<=(slength+2)):
        return " ".join(args)
    
    pad = int((length-slength)/2.0)
    
    #print fmt,pad,args
    out = fmt*pad +" "+" ".join(args) + " "+fmt*pad
    d = len(out) - length
    if(d>0):
        out = out[0:length]
    if(d<0):
        out += fmt*(-1*d)
        
    return out+"\n"
    

def check_undefined(key,dict):
    try:return dict[key]
    except:return "UNDEF"

def count_entries(seq):
    d = defaultdict(lambda: 0)
    for y in seq: d[y] += 1
    return d



def gauss(x,p):
     A, mu, sigma,A1, mu1, sigma1 = p
     return A*numpy.exp(-(x-mu)**2/(2*sigma**2)) + A1*numpy.exp(-(x-mu1)**2/(2*sigma1**2))

def residualgauss(p,y,x):
    err = y-gauss(x,p)
    return err

def printh(*args):
    global outputWidget
    try:
        frm = inspect.stack()[1]
        mod = inspect.getmodule(frm[0])
        line = inspect.getsourcelines(frm[0])[1]
        string= mod.__name__+" (line "+str(line)+") : "
    except:
        string=""
     #print "*FRM",frm
    

    maxlength = 80
    hlength = 0 
    for arg in args:hlength+=len(str(arg))
    hlength+=(len(args)-1)
    
    pre = "-"*int((maxlength-hlength)/2)
    post = "-"*(maxlength-len(pre)-hlength)
    if(len(args)>0):string+=pre+" "
    else:string+=pre+"-"
    
    for arg in args:
        string+=str(arg)+" "  
    string+=post    
       
    print string
    
#    try:
#        outputWidget.append(string)
#        cursor = outputWidget.textCursor()
#        cursor.movePosition(QtGui.QTextCursor.End)
#        outputWidget.setTextCursor(cursor)
#    except:
#        pass

def printl(*args):
    if(VERBOSE):
        
        try:
            frm = inspect.stack()[1]
            mod = inspect.getmodule(frm[0])
            line = inspect.getsourcelines(frm[0])[1]
            string= mod.__name__+" (line "+str(line)+") : "
        except:
            string=""
   
        for arg in args:
            string+=str(arg)+" "    
     
        print string
#        try:
#            global outputWidget
#            outputWidget.append(string)
#            cursor = outputWidget.textCursor()
#            cursor.movePosition(QtGui.QTextCursor.End)
#            outputWidget.setTextCursor(cursor)
#        except:
#            pass
def printd(*args):
    if(DEBUG):
        try:
            frm = inspect.stack()[1]
            mod = inspect.getmodule(frm[0])
            line = inspect.getsourcelines(frm[0])[1]
            string= mod.__name__+" (line "+str(line)+") : "
        except:
            string="" 

def encodeImages(inputfolder,outputfolder,framerate=25,fileID="image",ffmpeg = "ffmpeg",
                 outfile="output.mpg",imgformat=".jpg",fformat="%04d"):  
    olddir = os.getcwd()   
    os.chdir(inputfolder)
    output = outputfolder+"/"+outfile
    systemcall = str(ffmpeg)+" -r " + str(framerate) + " -y -i " + str(fileID)
    systemcall += fformat+imgformat
    systemcall += " -r "+str(framerate)+" -sameq "
    systemcall += str(output)
    printl(systemcall)
    os.system(systemcall)  
    os.chdir(olddir)    
      
def getUniqueID():
    global uniqueMask
    id = 1
    while(1): 
        if(uniqueMask[id]==0):
            uniqueMask[id] = 1
            break  
        id +=1
    return id    

def getUniqueInputID():
    global uniqueInputMask
    id = 1
    while(1): 
        if(uniqueInputMask[id]==0):
            uniqueInputMask[id] = 1
            break  
        id +=1
    return id 
        
def get_unique_entries(seq, idfun=None):  
    # order preserving 
    if idfun is None: 
        def idfun(x): return x 
    seen = {} 
    result = [] 
    for item in seq: 
        marker = idfun(item) 
        if marker in seen: continue 
        seen[marker] = 1 
        result.append(item) 
    return result    
 
def randvec(v):
    #numpy.random.seed(int(time.time()))
    vtemp = numpy.random.randn(v.size)
    return vtemp.reshape(v.shape)

def normalise(vec):
    vec = vec/magnitude(vec)
    return vec

def magnitude(vector):
    mag = math.sqrt(numpy.dot(vector,vector))    
    return mag    