'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Apr 10, 2014
Copyright Marc Robinson  2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

Main Toolbar

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
'''

from nanocap.core.globals import *
import os,sys,math,copy,random,time,threading,types
import numpy
from nanocap.gui.settings import *
from nanocap.gui.common import *
from nanocap.core.util import *

from nanocap.gui import menubar,structurelist
from nanocap.gui.widgets import SpinBox,DoubleSpinBox,HolderWidget,BaseWidget,TableWidget,ColorButton
 

class Toolbar(QtGui.QWidget):   
    def __init__(self, Gui, MainWindow):
        QtGui.QWidget.__init__(self, None)
        self.MainWindow = MainWindow
        self.Gui = Gui
        
        self.containerLayout = QtGui.QVBoxLayout()
        self.containerLayout.setContentsMargins(0, 2, 0, 0)
        self.containerLayout.setSpacing(4)
        self.setLayout(self.containerLayout)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        self.draw()
        
    def sizeHint(self):
        return QtCore.QSize(n_DOCKWIDTH,n_DOCKHEIGHT)
    
    def draw(self):
        self.MainWidget = HolderWidget(align=QtCore.Qt.AlignTop,stack="V",spacing=5)
       
        self.containerLayout.addWidget(self.MainWidget)
        self.structurelist = structurelist.StructureList(self.Gui)
               
        self.MainWidget.addWidget(QL("Structures",name="H1",align=QtCore.Qt.AlignCenter),align=QtCore.Qt.AlignCenter)
        self.MainWidget.addWidget(self.structurelist)
        self.MainWidget.show()