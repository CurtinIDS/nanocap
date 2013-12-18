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

try:
    from nanocap.core.globals import QT
    QtGui, QtCore, QtOpenGL = QT.QtGui, QT.QtCore, QT.QtOpenGL
except:pass
#clib = ctypes.cdll.LoadLibrary(ROOTDIR+"/clib/clib.so") 

#from nanocap.clib import clib_interface
#clib = clib_interface.clib

uniqueMask = numpy.zeros(9999,int)
uniqueInputMask = numpy.zeros(9999,int)
outputWidget = None

def get_root():
    frozen = getattr(sys, 'frozen', '')
    
    if not frozen:
        # not frozen: in regular python interpreter
        main = os.path.abspath(unicode(__file__, sys.getfilesystemencoding( ))+"/../")
        approot = os.path.dirname(main)
    
    elif frozen in ('dll', 'console_exe', 'windows_exe'):
        # py2exe:
        approot = os.path.dirname(unicode(sys.executable, sys.getfilesystemencoding( )))
    
    elif frozen in ('macosx_app',):
        # py2app:
        # Notes on how to find stuff on MAC, by an expert (Bob Ippolito):
        # http://mail.python.org/pipermail/pythonmac-sig/2004-November/012121.html
        approot = os.environ['RESOURCEPATH']
        
    return approot


def unit_normal(a, b, c):
    x = numpy.linalg.det([[1,a[1],a[2]],
         [1,b[1],b[2]],
         [1,c[1],c[2]]])
    y = numpy.linalg.det([[a[0],1,a[2]],
         [b[0],1,b[2]],
         [c[0],1,c[2]]])
    z = numpy.linalg.det([[a[0],a[1],1],
         [b[0],b[1],1],
         [c[0],c[1],1]])
    mag = (x**2 + y**2 + z**2)**.5
    return (x/mag, y/mag, z/mag)


def write_xyz(filename,pointSet,constrained=False):
    f = open(filename,"w")
    f.write(str(pointSet.npoints)+"\n")
    f.write("\n")
    for i in range(0,pointSet.npoints):
        if not constrained:f.write("C "+str(pointSet.pos[i*3])+" "+str(pointSet.pos[i*3+1])+" "+str(pointSet.pos[i*3+2])+"\n")
        else:f.write("C "+str(pointSet.constrained_pos[i*3])+" "+str(pointSet.constrained_pos[i*3+1])+" "+str(pointSet.constrained_pos[i*3+2])+"\n")
    f.close()
    

def get_relative_path(filename):
    frozen = getattr(sys, 'frozen', '')
    
    if not frozen:
        # not frozen: in regular python interpreter
        approot = os.path.dirname(unicode(__file__, sys.getfilesystemencoding( )))
    
    elif frozen in ('dll', 'console_exe', 'windows_exe'):
        # py2exe:
        approot = os.path.dirname(unicode(sys.executable, sys.getfilesystemencoding( )))
    
    elif frozen in ('macosx_app',):
        # py2app:
        # Notes on how to find stuff on MAC, by an expert (Bob Ippolito):
        # http://mail.python.org/pipermail/pythonmac-sig/2004-November/012121.html
        approot = os.environ['RESOURCEPATH']
        
    return os.path.join(approot,filename)

def path_from_file(filename,path_from_exe=""):
    if hasattr(sys, "frozen"):
        exe = os.path.dirname(unicode(sys.executable, sys.getfilesystemencoding( )))
        print "exe",exe
        return os.path.abspath(exe+path_from_exe)
    #print os.path.dirname(unicode(__file__, sys.getfilesystemencoding( )))
    return os.path.dirname(unicode(filename, sys.getfilesystemencoding( )))
    

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