'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: May 8, 2014
Copyright Marc Robinson  2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

Simple preferences window


-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
'''



from nanocap.core.globals import *
import os,sys,math,copy,random,time,threading,Queue,types
import numpy
from nanocap.core.util import *
from nanocap.core import globals,minimisation,triangulation,minimasearch,structurelog

from nanocap.gui.settings import *
from nanocap.gui.common import *
from nanocap.gui.widgets import SpinBox,DoubleSpinBox,HolderWidget,BaseWidget,Frame
import nanocap.gui.structuretable as structuretable
import nanocap.gui.progresswidget as progresswidget
import nanocap.gui.structureinputoptions as structureinputoptions
import nanocap.gui.minimiserinputoptions as minimiserinputoptions 

from nanocap.structures import fullerene
from nanocap.structures import cappednanotube



class PreferencesWindow(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)

        self.setWindowTitle("Preferences")
        
        self.setSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Preferred)
        
        self.contentlayout = QtGui.QGridLayout(self)
        self.contentlayout.setContentsMargins(5,5,5,5)
        self.contentlayout.setSpacing(5)
        #self.contentlayout.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        self.contentlayout.setAlignment(QtCore.Qt.AlignLeft)
        self.setLayout(self.contentlayout)
        
        
        self.options_list = QtGui.QListWidget()
        self.options_list.addItem("User")
        self.options_list.addItem("Database")
        self.options_list.setFixedWidth(140)
        self.connect(self.options_list,QtCore.SIGNAL('clicked (QModelIndex)'), self.option_changed) 
        
        self.options_holder = BaseWidget(w=300,h=400,align = QtCore.Qt.AlignTop,spacing=5,margins=[5,5,5,5])
        
        self.contentlayout.addWidget(self.options_list,0,0)
        self.contentlayout.addWidget(self.options_holder,0,1)
        
        self.options = {}
        self.options["User"] = BaseWidget(self,group=False,show=True,align = QtCore.Qt.AlignTop)
        #self.points_holder.FormLayout.setContentsMargins(5,5,5,5)
        
        self.user_name_entry = QtGui.QLineEdit(CONFIG.opts["User"])
        self.options["User"].addWidgets([QL("User name:"),self.user_name_entry])
        self.user_home_entry = QtGui.QLineEdit(CONFIG.opts["Home"])
        self.options["User"].addWidgets([QL("User home directory:"),self.user_home_entry])
        self.user_email_entry = QtGui.QLineEdit(CONFIG.opts["Email"])
        self.options["User"].addWidgets([QL("User email:"),self.user_email_entry])
        
        self.options["Database"]= BaseWidget(self,group=False,show=False,align = QtCore.Qt.AlignTop)
        
        self.database_entry = QtGui.QLineEdit(CONFIG.opts["LocalDatabase"])
        self.options["Database"].addWidgets([QL("Local Database:"),self.database_entry])
        
        self.save_bt = QtGui.QPushButton("Save")
        self.cancel_bt = QtGui.QPushButton("Cancel")
        
        self.options_holder.addWidget(self.options["User"],align = QtCore.Qt.AlignTop)
        self.options_holder.addWidget(self.options["Database"],align = QtCore.Qt.AlignTop)
        
        #self.contentlayout.addWidget(self.save_bt,1,1)
        
        self.contentlayout.addWidget(Frame(),1,0,1,3)
        self.contentlayout.addWidget(HolderWidget([self.save_bt,self.cancel_bt]),3,1,1,2,QtCore.Qt.AlignRight)
        
        self.connect(self.save_bt,QtCore.SIGNAL("clicked()"),self.save)
        self.connect(self.cancel_bt,QtCore.SIGNAL("clicked()"),self.hide)
        
        #for form in self.options.values():form.hide()
        for form in self.options.values():form.hide()
        
    def option_changed(self,index):
        option = self.options_list.currentItem().text()
        for form in self.options.values():form.hide()
        
        self.options[option].show()
    
    def save(self):
        CONFIG.opts["Email"]=self.user_email_entry.text()
        CONFIG.opts["User"]=self.user_name_entry.text()
        CONFIG.opts["Home"]=self.user_home_entry.text()
        CONFIG.opts["LocalDatabase"]=self.database_entry.text()
        
    def sizeHint(self):
        return QtCore.QSize(500,400) 
            
    def bringToFront(self):
        self.raise_()
        self.show()           