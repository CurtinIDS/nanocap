'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Apr 29, 2014
Copyright Marc Robinson  2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

simple window to load a single
structure


-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
'''

from nanocap.core.globals import *
import os,sys,math,copy,random,time,threading,Queue,types
import numpy

from nanocap.gui.settings import *
from nanocap.gui.common import *
from nanocap.core.util import *
from nanocap.gui.widgets import SpinBox,DoubleSpinBox,HolderWidget,BaseWidget

import nanocap.gui.structuretable as structuretable
import nanocap.gui.progresswidget as progresswidget

from nanocap.structures import fullerene
from nanocap.structures import cappednanotube
from nanocap.structures import nanotube

from nanocap.core import globals,minimisation,triangulation,minimasearch,structurelog

class SingleStructureGenWindow(BaseWidget):
    def __init__(self,Gui,MainWindow):
        self.Gui = Gui
        self.MainWindow = MainWindow
        
        BaseWidget.__init__(self,self.MainWindow,w=200,h=0,show=False,stack="V",popup=True,
                            align=None)
        #QtGui.QWidget.__init__(self)#,self.MainWindow)
        
        self.setWindowTitle("Add Single Structure")
        
        self.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Preferred)
        
#         self.contentlayout = QtGui.QVBoxLayout(self)
#         self.contentlayout.setContentsMargins(0,0,0,0)
#         self.contentlayout.setSpacing(0)
#         #self.contentlayout.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
#         self.setLayout(self.contentlayout)
        
        for TYPE in STRUCTURE_TYPES:
            if(TYPE == FULLERENE) or (TYPE == CAPPEDNANOTUBE) or (TYPE == NANOTUBE):
                call = lambda type=TYPE : self.add_structure(type)
                bt = QtGui.QPushButton(TYPE.label)
                self.connect(bt, QtCore.SIGNAL('clicked()'), call)
                self.layout.addWidget(bt)
        
        self.show()
                
    def bringToFront(self):
        self.raise_()
        self.show()
                    
    def add_structure(self,type):
        if(type == FULLERENE):
            struct = fullerene.Fullerene()
        if(type == CAPPEDNANOTUBE):
            struct = cappednanotube.CappedNanotube()
        if(type == NANOTUBE):
            struct = nanotube.Nanotube()
                
        self.MainWindow.activateWindow()   
        self.MainWindow.gui.dock.toolbar.structurelist.addStructure(struct) 
        
        self.hide()
        
        
