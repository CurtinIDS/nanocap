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


if(PLATFORM=='osx'):
    font_size = 11
if(PLATFORM=='win'):
    font_size = 9
if(PLATFORM=='linux'):
    font_size = 11
 

n_DOCKWIDTH = 350
n_DOCKHEIGHT = 500 
SCREENWIDTH = 950
SCREENHEIGHT = 650


BANNERIMAGE = 'NanoCapBanner22514.png'
BANNERIMAGE = 'NanoCapWithLogo22514.png'
BANNERIMAGE = 'NanoCapBannerRight22514w350.png'
BANNERIMAGEALIGN = QtCore.Qt.AlignRight
LOGOIMAGE = 'NanoCapWithLogo22514.png'
SPLASHIMAGE = 'splash19.png'


   
# menubarcol = "rgb(60,60,60)"
# menubarcol = "rgb(200,200,200)"
# toolbarcol = "rgb(180,180,180)"
# menufontcol = "rgb(255,255,255)"
# menufontcol = "rgb(0,0,0)"
# 
# statusbarcol = "rgb(60,60,60)"
# statusbarfontcol = "rgb(255,255,255)"
# menubarcol = "rgb(60,60,60)"
# menubarfontcol = "rgb(255,255,255)"
# menubarsepcol = "rgb(200,200,200)"
# 
# #1
# statusbarcol = "rgb(100,100,100)"
# statusbarfontcol = "rgb(255,255,255)"
# menubarcol = "rgb(100,100,100)"
# menubarcol = '''qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
#                                 stop: 0 rgb(60,60,60), stop: 1 rgb(100,100,100));'''
#                                                         
# menubarfontcol = "rgb(255,255,255)"
# menubarsepcol = "rgb(200,200,200)"
#1


menubarcol = '''qlineargradient(x1: 0, y1: 0.2, x2: 0, y2: 1,
                                stop: 1 rgb(60,60,60), stop: 0 rgb(100,100,100));'''                                
statusbarcol = '''qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 1 rgb(60,60,60), stop: 0 rgb(100,100,100));''' 
                                
dropdownmenubarcol = '''qlineargradient(x1: 0, y1: 0.5, x2: 0, y2: 1,
                                stop: 0 rgb(240,240,240), stop: 1 rgb(230,230,230));'''                               
                                
                          
menubarfontcol = "rgb(255,255,255)"
menubaritemfontcol = "rgb(10,10,10)"
menubaritemselectedfontcol = "rgb(220,220,220)"    
menubaritemselectedcol = "rgb(60,60,60)"
menubarsepcol = "rgb(150,150,150)"
statusbarfontcol = "rgb(235,235,235)"
 
STYLESHEET = '''

            
            
            
            QWidget {
            font-size: '''+str(font_size)+'''pt;
            
            }
            
            QCheckBox {
            font-size: '''+str(font_size)+'''pt;
            }
            
            QTableView { border-style: outset; 
                        border-width: 1px; 
                        border-color: grey;
                        }
                        
            QTableView#frozenTableView { 
                            border: none;
                            background-color: #E0E0E0;
                            }
            
            
            
            
            QCheckBox {
            font-size: '''+str(font_size)+'''pt;
            }
            
            
            QCheckBox {
            font-size: '''+str(font_size)+'''pt;
            }

            QToolBar#Main {
            font-size:: '''+str(font_size)+'''pt;
            background: '''+menubarcol+'''; 
            border-style: ridge;
            spacing: 3px;
            }
            
            QToolButton{
            font: '''+str(font_size)+'''pt;
            color:'''+menubarfontcol+''';
            }
            
            QMenu {
            font: '''+str(font_size+2)+'''pt;
            color:'''+menubarfontcol+''';
            background-color: '''+dropdownmenubarcol+'''; 
            }
                        
            QMenu::item {
            font: '''+str(font_size+2)+'''pt;
            color:'''+menubaritemfontcol+''';
            background-color: transparent; 
            }
            
            
            QMenu::item:selected {
            font: '''+str(font_size+2)+'''pt;
            color:'''+menubaritemselectedfontcol+''';
            background-color: '''+menubaritemselectedcol+'''; 
            }
                        
            QMenu::separator {
                 height: 1px;
                 margin: 8px 15px 8px 15px;
                 background: '''+menubarsepcol+'''; 
             }
            
             QMenu::indicator {
                 width: 23px;
                 height: 23px;
                 background-color: '''+menubarfontcol+'''; 
                 color: '''+menubarfontcol+'''; 
             }
            
            
            QLabel#Header{
                font: bold '''+str(font_size)+'''pt;
            }
            
            QLabel#H1{
                font: bold '''+str(font_size+2)+'''pt;
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
            
            
            QGroupBox#check:title {
                subcontrol-origin: margin; 
                subcontrol-position: top left ; 
                font: bold '''+str(font_size)+'''pt,  ;  
                padding: 2 15px;
            }  
            QGroupBox#check{
            font: bold '''+str(font_size)+'''pt,  ;
            border-width: 2px;  
            
            }
            
            QGroupBox#CenterGroup:title {
                subcontrol-origin: margin; 
                subcontrol-position: top center ; 
                font: bold '''+str(font_size+2)+'''pt,  ;  
                padding: 2 8px;
                background-color: transparent; 
            } 
            
             QGroupBox#CenterGroup{
             margin-top: 18px;
            font: bold '''+str(font_size+2)+'''pt,  ; 
            
            } 
            
            QGroupBox#H1:title {
                subcontrol-origin: margin; 
                subcontrol-position: top center ; 
                font: bold '''+str(font_size+2)+'''pt,  ;  
                padding: 2 8px;
                background-color: transparent; 
            } 
            
             QGroupBox#H1{
             margin-top: 18px;
            font: bold '''+str(font_size+2)+'''pt,  ; 
            
            } 
            
            QGroupBox:title {
                subcontrol-origin: margin; 
                subcontrol-position: top left ; 
                font: bold '''+str(font_size)+'''pt,  ;  
                padding: 2 8px;
                background-color: transparent; 
            } 
            
            
             
            
             QGroupBox{
             margin-top: 18px;
            font: bold '''+str(font_size)+'''pt,  ; 
            
            } 
            
            
            
            QGroupBox::indicator {
                 width: 13px;
                 height: 5px;
                  padding: 2 2px;
             }
            
             
            
            QWidget#NoBorder {
                
                border-width: 0px; 
                border-style: solid;
                
            
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
             

 