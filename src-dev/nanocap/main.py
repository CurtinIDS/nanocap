'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Apr 10, 2014
Copyright Marc Robinson 2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

main GUI script

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
'''
from nanocap.gui.settings import *
from nanocap.gui.mainwindow import MainWindow
from nanocap.gui.gui import GUI
            

def start():
    app = QtGui.QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    #if(PLATFORM=="win"):app.setStyle(QtGui.QStyleFactory.create("cleanlooks"))
    strdir = QtGui.QApplication.applicationDirPath()
    
    splash_pix = QtGui.QPixmap(str(IconDir) + SPLASHIMAGE)
    splash = QtGui.QSplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pix.mask())
    splash.show()
    app.processEvents()
    
    MainAppWindow = MainWindow()
    
    splash.finish(MainAppWindow)

    #ngui = GUI(MainAppWindow)
    #MainAppWindow.setGUI(ngui) 
    #MainAppWindow.show()
    
    try:
        sys.exit(app.exec_())
    except SystemExit as e:
        if e.code != 0:
            raise()
        os._exit(0)
               
if __name__=="__main__":
    global root
    start()

