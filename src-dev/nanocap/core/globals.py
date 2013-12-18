'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Aug 1 2013
Copyright Marc Robinson 2013
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

Generic globals, sets up the ext and clib
dirs
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
'''

import os,numpy,sys,inspect,platform
import ctypes

#import PySide
#from PySide import QtGui, QtCore, QtOpenGL
#QT = PySide

try:
    import PySide
    from PySide import QtGui, QtCore, QtOpenGL
    QT = PySide
    print "Using PySide version", PySide.__version__   
except:
    print "Could not load PySide, trying PyQt4"    
    try:
        import PyQt4
        from PyQt4 import QtGui, QtCore, QtOpenGL
        QT = PyQt4
        print "Using PyQt4 version", PySide.__version__   
    except:
        print "PyQt or PySide not found"    
        
ps = platform.system()
if(ps=="Darwin"):PLATFORM = "osx"
if(ps=="Windows"):PLATFORM = "win"
if(ps=="Linux"):PLATFORM = "linux"        
    
#os.system("export OMP_NUM_THREADS=4")
if(PLATFORM!='win'):os.environ["OMP_NUM_THREADS"] = "4"

NPF = numpy.float64
NPF32 = numpy.float32
NPI = numpy.int32
use_clib= True
DEBUG   = False
VERBOSE = True
IconDir = ":Icons/"
IconDir = ":"
  

menubarcol = "rgb(60,60,60)"
toolbarcol = "rgb(180,180,180)"
menufontcol = "rgb(255,255,255)"
if(PLATFORM=='osx'):
    font_size = 11
if(PLATFORM=='win'):
    font_size = 9
if(PLATFORM=='linux'):
    font_size = 11
    
    


styleSheetString = " \
            QWidget {font: "+str(font_size)+"pt;}\
            QMenuBar {background-color: "+menubarcol+";color:"+menufontcol+";border-style: ridge;}\
            QMenu::item {background-color: "+menubarcol+";  color:"+menufontcol+"; padding: 2px 25px 2px 25px;}\
            QMenu::item:selected { border-color: "+menufontcol+"; background: rgb(100, 100, 100); }\
            QStatusBar {background: "+menubarcol+"; color:"+menufontcol+";}\
            QStatusBar QLabel { color:"+menufontcol+";}\
            QTabBar {font-weight: bold ;}\
            QToolBar {spacing: 3px; }\
            QGroupBox:title {subcontrol-origin: margin; subcontrol-position: top center ; font: "+str(font_size)+"pt,  ;  \
            padding: 2 3px;} \
            QGroupBox {background-color: rgba(50, 50, 50,30); font: "+str(font_size)+"pt ;font:  bold;  border-width: 1px; border-style: None    ; \
            border-radius: 5px; border-color: "+menubarcol+";padding: 7px; margin-top: 2.5ex; margin-bottom: 1ex; }" \
            

#for now we will hold these has globals




                    
                     
                     
