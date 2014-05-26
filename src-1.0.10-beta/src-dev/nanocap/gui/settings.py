'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Apr 10, 2014
Copyright Marc Robinson  2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

settings for GUI appearance etc

Qt stylesheets
Qt import control (PySide)

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
'''

from nanocap.core.globals import *


try:
    import PySide
    from PySide import QtGui, QtCore, QtOpenGL,QtWebKit
    QT = PySide
    print "Using PySide version", PySide.__version__   
except:
    print "Could not load PySide, trying PyQt4"    
    try:
        import PyQt4
        from PyQt4 import QtGui, QtCore, QtOpenGL,QtWebKit
        QT = PyQt4
        print "Using PyQt4 version", PySide.__version__   
    except:
        print "PyQt or PySide not found"    

IconDir = ":Icons/"
IconDir = ":"
   
menubarcol = "rgb(60,60,60)"
menubarcol = "rgb(200,200,200)"
toolbarcol = "rgb(180,180,180)"
menufontcol = "rgb(255,255,255)"
menufontcol = "rgb(0,0,0)"

statusbarcol = "rgb(60,60,60)"
statusbarfontcol = "rgb(255,255,255)"

if(PLATFORM=='osx'):
    font_size = 11
if(PLATFORM=='win'):
    font_size = 9
if(PLATFORM=='linux'):
    font_size = 11
 

n_DOCKWIDTH = 350
n_DOCKHEIGHT = 500 
SCREENWIDTH = 900
SCREENHEIGHT = 600


BANNERIMAGE = 'NanoCapBanner22514.png'
BANNERIMAGE = 'NanoCapWithLogo22514.png'
BANNERIMAGE = 'NanoCapBannerRight22514w350.png'
BANNERIMAGEALIGN = QtCore.Qt.AlignRight
LOGOIMAGE = 'NanoCapWithLogo22514.png'
 
STYLESHEET = '''
            QWidget {
            font-size: '''+str(font_size)+'''pt;
            }
            
            QCheckBox {
            font-size: '''+str(font_size)+'''pt;
            }
                
                    
            QMenuBar {
            font: '''+str(font_size+2)+'''pt;
            color:'''+menufontcol+''';
            border-style: ridge;
            }
            
            QMenu#edit_menu {
            font: '''+str(font_size+2)+'''pt;
            color:'''+menufontcol+''';
            }
            QMenu#help_menu {
            font: '''+str(font_size+2)+'''pt;
            color:'''+menufontcol+''';
            }
            QMenu#about_menu {
            font: '''+str(font_size+2)+'''pt;
            color:'''+menufontcol+''';
            }
            
            QMenu#file_menu {
            font: '''+str(font_size+2)+'''pt;
            color:'''+menufontcol+''';
            }
            
            QMenu#view_menu {
            font: '''+str(font_size+2)+'''pt;
            color:'''+menufontcol+''';
            }
                        
            QMenu::item {
            font: '''+str(font_size+2)+'''pt;
            color:'''+menufontcol+''';
            }
            
            QStatusBar {
            background: '''+statusbarcol+'''; 
            color:'''+statusbarfontcol+''';
            }
            
            QStatusBar QLabel {
            color:'''+statusbarfontcol+''';
            }
             
            QTabBar {
            font-weight: bold ;
            }
            
            QToolBar {
            spacing: 3px;
             }
             
             QGroupBox:{
            font: '''+str(font_size)+'''pt,  ;  
            } 
            
            QGroupBox:title {
            subcontrol-origin: margin; 
            subcontrol-position: top left ; 
            font: '''+str(font_size)+'''pt,  ;  
            padding: 2 8px;
            } 
            
             
             
             
             '''
             
             
             #QGroupBox {font: "+str(font_size)+"pt ;font:  bold;}"# 
#              QStatusBar {background: "+menubarcol+"; color:"+menufontcol+";}\
#             QStatusBar QLabel { color:"+menufontcol+";}\
#             QGroupBox:title {subcontrol-origin: margin; subcontrol-position: top center ; font: "+str(font_size)+"pt,  ;  \
#             padding: 2 3px;} \
#             QGroupBox {background-color: rgba(50, 50, 50,30); font: "+str(font_size)+"pt ;font:  bold;  border-width: 1px; border-style: None    ; \
#             border-radius: 5px; border-color: "+menubarcol+";padding: 7px; margin-top: 2.5ex; margin-bottom: 1ex; }" \
#              

#           QMenuBar {background-color: "+menubarcol+";color:"+menufontcol+";border-style: ridge;}\
#            QMenu::item {background-color: "+menubarcol+";  color:"+menufontcol+"; padding: 2px 25px 2px 25px;}\
#            QMenu::item:selected { border-color: "+menufontcol+"; background: rgb(100, 100, 100); }\
             

 