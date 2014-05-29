'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: May 12, 2014
Copyright Marc Robinson  2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

Window to hold the loading from file
options


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
from nanocap.structures import nanotube
from nanocap.gui.widgets import BaseWidget,HolderWidget

from nanocap.core import globals,minimisation,triangulation,minimasearch,structurelog

class LoadFromFileWindow(BaseWidget):
    load_structure = QtCore.Signal()
    def __init__(self):
                
        BaseWidget.__init__(self)#,self.main_window,QtCore.Qt.Window)
        

        self.setWindowTitle("Load Structure From File")
        
        self.setSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Preferred)
        
#         self.contentlayout = QtGui.QGridLayout(self)
#         self.contentlayout.setContentsMargins(5,5,5,5)
#         self.contentlayout.setSpacing(5)
#         self.contentlayout.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
#         self.setLayout(self.contentlayout)

        self.type_holder = BaseWidget(show=True,group=True,title="Type",align=QtCore.Qt.AlignLeft)
        self.addWidget(self.type_holder,0,0)
        
        self.type_group = QtGui.QButtonGroup()
        self.type_group.setExclusive(True)
        self.type_radio_bts = {}
        for type in ['Fullerene','Nanotube','CappedNanotube']:
            self.type_radio_bts[type] = QtGui.QRadioButton(type)
            self.type_group.addButton(self.type_radio_bts[type])
            
        self.type_holder.addWidgets(self.type_radio_bts.values())    
        
        
        
        self.dual_lattice_holder = BaseWidget(show=True,group=True,title="Dual Lattice",align=QtCore.Qt.AlignLeft)
        self.addWidget(self.dual_lattice_holder,1,0)
        
        self.dual_lattice_holder.central_widget.setCheckable(True)
        self.dual_lattice_holder.central_widget.setChecked(False)
        self.dual_lattice_holder.central_widget.setObjectName("check")
        
        self.dual_lattice_file_entry = QtGui.QLineEdit()
        self.dual_lattice_format_cb = QtGui.QComboBox()
        self.dual_lattice_format_cb.addItem("xyz")
        self.dual_lattice_file_browse_bt = QtGui.QPushButton("Browse")
        self.connect(self.dual_lattice_file_browse_bt,QtCore.SIGNAL("clicked()"),self.browse_to_dual_lattice)
        
        self.dual_lattice_holder.addWidgets((QL("Filename:"),self.dual_lattice_file_entry,QL("Format:"),self.dual_lattice_format_cb))    
        self.dual_lattice_holder.addWidget(self.dual_lattice_file_browse_bt)
        
        self.carbon_lattice_holder = BaseWidget(show=True,group=True,title="Carbon Lattice",align=QtCore.Qt.AlignLeft)
        self.addWidget(self.carbon_lattice_holder,2,0)
        
        self.carbon_lattice_holder.central_widget.setCheckable(True)
        self.carbon_lattice_holder.central_widget.setChecked(False)
        self.carbon_lattice_holder.central_widget.setObjectName("check")
        
        self.carbon_lattice_file_entry = QtGui.QLineEdit()
        self.carbon_lattice_format_cb = QtGui.QComboBox()
        self.carbon_lattice_format_cb.addItem("xyz")
        self.carbon_lattice_file_browse_bt = QtGui.QPushButton("Browse")
        self.connect(self.carbon_lattice_file_browse_bt,QtCore.SIGNAL("clicked()"),self.browse_to_carbon_lattice)
        
        self.carbon_lattice_holder.addWidgets((QL("Filename:"),self.carbon_lattice_file_entry,QL("Format:"),self.carbon_lattice_format_cb))    
        self.carbon_lattice_holder.addWidget(self.carbon_lattice_file_browse_bt)
    
        self.button_holder = BaseWidget(show=True,group=False)
        self.addWidget(self.button_holder,3,0)
        
        self.load_bt = QtGui.QPushButton("Load")
        self.connect(self.load_bt,QtCore.SIGNAL("clicked()"),self.load)
        self.button_holder.addWidget(self.load_bt)
    
    def load(self):
        structure=None
        for key,button in self.type_radio_bts.items():
            if button.isChecked():
                if(key=="Fullerene"):
                    structure = fullerene.Fullerene()
                if(key=="Nanotube"):
                    structure = nanotube.Nanotube()
                if(key=="CappedNanotube"):    
                    structure = cappednanotube.CappedNanotube()
        if(structure==None):return
        
        file=None
        if(self.dual_lattice_holder.central_widget.isChecked()):
            format = self.dual_lattice_format_cb.currentText()
            file = self.dual_lattice_file_entry.text()
            structure.load_dual_lattice_from_file(file,format)
        
        if(self.carbon_lattice_holder.central_widget.isChecked()):
            format = self.carbon_lattice_format_cb.currentText()
            file = self.carbon_lattice_file_entry.text()
            structure.load_carbon_lattice_from_file(file,format)
        
        if(file==None):return
        
        self.structure = structure
        self.load_structure.emit()
    
    def bringToFront(self):
        self.raise_()
        self.show()  
                
    def browse_to_carbon_lattice(self):
        f = browse_to_file()
        self.carbon_lattice_file_entry.setText(f)
        
    def browse_to_dual_lattice(self):
        f = browse_to_file()
        self.dual_lattice_file_entry.setText(f)
        
    def sizeHint(self):
        return QtCore.QSize(400,200) 
        
        
        