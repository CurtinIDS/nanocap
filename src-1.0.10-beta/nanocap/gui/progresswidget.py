'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Apr 14, 2014
Copyright Marc Robinson  2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

progress bar and associated info


-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
'''

from nanocap.core.globals import *
import os,sys,math,copy,random,time,threading,Queue,types
import numpy

from nanocap.gui.settings import *
from nanocap.gui.common import *
from nanocap.core.util import *
from nanocap.gui.widgets import SpinBox,DoubleSpinBox,HolderWidget,BaseWidget

class ProgressWidget(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        
        self.containerLayout = QtGui.QVBoxLayout()
        self.setLayout(self.containerLayout)
        
        self.infoLabel = QL("")
        
        self.searchProgressbar = QtGui.QProgressBar()
        self.searchProgressbar.setMinimum(0)
        
        self.containerLayout.addWidget(self.infoLabel)
        
        self.stopBT = QtGui.QPushButton("Stop")
        
        row = BaseWidget()
        row.addWidgets((self.searchProgressbar,self.stopBT ))
        self.containerLayout.addWidget(row)
        
    def reset(self,nmax):
        self.searchProgressbar.setMaximum(nmax)
        self.searchProgressbar.setValue(0)
        
    def updateProgress(self,N,info=""):
        self.infoLabel.setText("Structures found: {:^10} Status: {}".format(N,info))
        self.searchProgressbar.setValue(N)
        
        
