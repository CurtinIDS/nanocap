'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Aug 2 2013
Copyright Marc Robinson 2013
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

Qt Dock 

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
'''

from nanocap.core.globals import *
import nanocap.core.globals as globals
import os,sys,math,copy,random
from nanocap.core.globals import QT
QtGui, QtCore = QT.QtGui, QT.QtCore

import numpy

import nanocap.gui.forms as forms
import nanocap.core.processes as processes
import nanocap.gui.toolbaradvanced as toolbaradvanced
import nanocap.gui.toolbarbasic as toolbarbasic
from nanocap.core.util import *

class dock(QtGui.QDockWidget):    
    def __init__(self, Gui, MainWindow, width, height, title):
        QtGui.QDockWidget.__init__(self, None)
        self.MainWindow = MainWindow
        self.Gui = Gui
        self.Processor = self.Gui.processor
        self.ThreadManager = self.Gui.threadManager
        self.VTKFrame = self.Gui.vtkframe
        self.ObjectActors = self.Gui.objectActors
        #self.container = forms.GenericForm(isScrollView=True,width=width)
        self.setTitleBarWidget(QtGui.QWidget())
        
        self.container = QtGui.QWidget()
        self.containerLayout = QtGui.QVBoxLayout()
        self.container.setLayout(self.containerLayout)
        self.containerLayout.setContentsMargins(0, 0, 0, 0)
        self.containerLayout.setSpacing(0)
        
        #self.container.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)
        self.setWidget(self.container)
        
        #self.mode = "Basic"
        
        self.setMinimumWidth(width)

    def draw(self):
        self.toolbars =  {}
        self.toolbars["Basic"] = toolbarbasic.toolbarBasic(self.Gui, self.MainWindow)
        self.toolbars["Advanced"] = toolbaradvanced.toolbarAdvanced(self.Gui, self.MainWindow)

        self.tabWidget = QtGui.QTabWidget()
        self.connect(self.tabWidget, QtCore.SIGNAL('currentChanged(int)'), self.changeMode) 
        
        self.tabWidget.addTab(self.toolbars["Basic"], "Basic")
        self.tabWidget.addTab(self.toolbars["Advanced"], "Advanced")
        
        self.containerLayout.addWidget(self.tabWidget)
        
        self.toolbars["Basic"].draw()
        self.toolbars["Advanced"].draw()
        
        
        self.iconWidget = QtGui.QLabel()
        
        self.iconWidget.setStyleSheet("QWidget {background-color: white}")
        self.icon = QtGui.QPixmap(str(IconDir) + 'Logo6BlackGrey.png')
        #self.icon = self.icon.scaledToWidth(self.width())
        self.iconWidget.setPixmap(self.icon)
        self.iconWidget.setGeometry(0, 0, self.width(), 55)
        
        self.containerLayout.addWidget(self.iconWidget)
        self.containerLayout.setAlignment(self.iconWidget, QtCore.Qt.AlignRight)
        
#        self.iconWidget2 = QtGui.QLabel()
#        
#        self.iconWidget2.setStyleSheet("QWidget {background-color: white}")
#        self.icon2 = QtGui.QPixmap(str(IconDir) + 'Logo1BlackGrey.png')
#        #self.icon = self.icon.scaledToWidth(self.width())
#        self.iconWidget2.setPixmap(self.icon2)
#        self.iconWidget2.setGeometry(0, 0, self.width(), 55)
#        
#        self.containerLayout.addWidget(self.iconWidget2)
#        self.containerLayout.setAlignment(self.iconWidget2, QtCore.Qt.AlignRight)
        
    def currentToolbar(self):
        printl(globals.Mode)
        return self.toolbars[globals.Mode]

    
    def changeMode(self,val):
        globals.Mode = str(self.tabWidget.tabText(val))
        self.toolbars[globals.Mode].selected()
        
        
        
        
        