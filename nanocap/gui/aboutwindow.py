'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: May 13, 2014
Copyright Marc Robinson  2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-




-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
'''


from nanocap.core.globals import *
import os,sys,math,copy,random,time,threading,Queue,types
import numpy

from nanocap.gui.settings import *
from nanocap.gui.common import *
from nanocap.core.util import *
import nanocap.gui.structuretable as structuretable
import nanocap.gui.progresswidget as progresswidget
import nanocap.gui.structureinputoptions as structureinputoptions
import nanocap.gui.minimiserinputoptions as minimiserinputoptions 


from nanocap.structures import fullerene
from nanocap.structures import cappednanotube
from nanocap.gui.widgets import BaseWidget,HolderWidget

from nanocap.core import globals,minimisation,triangulation,minimasearch,structurelog

class AboutWindow(BaseWidget):
    export_structure = QtCore.Signal(dict)
    def __init__(self,parent=None):
        
        if(parent!=None):
            BaseWidget.__init__(self,parent=parent,popup=True,align=QtCore.Qt.AlignCenter,show=False)
        else:
            BaseWidget.__init__(self,align=None,show=False)        
        #QtGui.QWidget.__init__(self)#,self.main_window,QtCore.Qt.Window)
        
        self.setWindowTitle("About NanoCap")
        
#         self.setSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Preferred)
#         
#         self.contentlayout = QtGui.QGridLayout(self)
#         self.contentlayout.setContentsMargins(5,5,5,5)
#         self.contentlayout.setSpacing(5)
#         self.contentlayout.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
#         self.setLayout(self.contentlayout)
        
        

        self.infoholder = BaseWidget(show=True,group=False,align=QtCore.Qt.AlignCenter)
        
        
        for key,line in NANOCAP_META.items():
            if key=="url":
                lab = '<qt> <a href = "'+line+'">'+line+'</a></qt>'
            else:lab=line
            self.infoholder.addWidget(QL(lab,align=QtCore.Qt.AlignCenter),align=QtCore.Qt.AlignCenter)
        
        
        self.iconWidget = QtGui.QLabel()
        self.iconWidget.setStyleSheet("QWidget {background-color: white}")
        self.icon = QtGui.QPixmap(str(IconDir) + LOGOIMAGE)
        #self.icon = self.icon.scaledToWidth(self.width())
        self.iconWidget.setPixmap(self.icon)
        self.iconWidget.setAlignment(QtCore.Qt.AlignCenter)
        #self.iconWidget.setGeometry(0, 0, self.width(), 55)
        
        
        self.addWidget(self.iconWidget,align=QtCore.Qt.AlignTop)
        self.addWidget(self.infoholder,align=QtCore.Qt.AlignBottom)
        self.hide()
        
    def bringToFront(self):
        self.raise_()
        self.show()  
        
        
    def sizeHint(self):
        return QtCore.QSize(300,50) 