'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Apr 14, 2014
Copyright Marc Robinson  2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-




-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
'''
from nanocap.gui.settings import *
from nanocap.core.globals import *
from nanocap.core.util import *
from nanocap.gui.widgets import BaseWidget


class BottomDock(QtGui.QDockWidget):    
    def __init__(self):#Gui, MainWindow, width, height, title):
        QtGui.QDockWidget.__init__(self, None)
        self.setTitleBarWidget(QtGui.QWidget())
        self.container = BaseWidget()
        #self.setTitleBarWidget(QtGui.QWidget())
        self.container.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Maximum)
        #self.container.setMinimumHeight(200)
        self.setWidget(self.container)
        
    
    def sizeHint(self):
        return QtCore.QSize(20,700)
        

                