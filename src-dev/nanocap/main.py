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

    #if(PLATFORM=="win"):app.setStyle(QtGui.QStyleFactory.create("cleanlooks"))
    strdir = QtGui.QApplication.applicationDirPath()
    MainAppWindow = MainWindow()
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

