'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Apr 10, 2014
Copyright Marc Robinson  2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

GUI mainwindow

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
'''
from nanocap.gui.settings import *
from nanocap.gui import gui
from nanocap.core import globals

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
#         self.setMinimumWidth(SCREENWIDTH)
#         self.setMinimumHeight(SCREENHEIGHT)
        self.setStyleSheet(STYLESHEET)
        self.setSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Preferred)

        self.gui = gui.GUI(self)
        
        self.show()
        self.raise_()
#     def setGUI(self,gui):
#         self.gui = gui
    def sizeHint(self):
        return QtCore.QSize(SCREENWIDTH,SCREENHEIGHT)
        
    def closeEvent(self, event=None):  
#         if(globals.DEBUG):
#             self.gui.threadManager.stop()
#             QtGui.QApplication.quit()  
        
        mb = QtGui.QMessageBox(QtGui.QMessageBox.Question,"...",
                               "Are you sure to exit NanoCap?" )
        mb.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        mb.setIconPixmap(QtGui.QPixmap(str(IconDir) +"nanocap_symbol_64x64.png"))
        reply = mb.exec_()       
        if reply == QtGui.QMessageBox.Yes:
            if(event!=None):event.accept()
            self.gui.threadManager.stop()
            QtGui.QApplication.quit()

        else:
            if(event!=None):event.ignore()
            
        return
