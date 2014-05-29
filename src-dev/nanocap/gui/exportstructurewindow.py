'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: May 8, 2014
Copyright Marc Robinson  2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

Simple window to show export options

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



class ExportStructureWindow(BaseWidget):
    export_structure = QtCore.Signal(dict)
    def __init__(self):
                
        BaseWidget.__init__(self,show=False)#,self.main_window,QtCore.Qt.Window)
        

        self.setWindowTitle("Export Structure")
        
        self.setSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Preferred)
        
#         self.contentlayout = QtGui.QGridLayout(self)
#         self.contentlayout.setContentsMargins(5,5,5,5)
#         self.contentlayout.setSpacing(5)
#         self.contentlayout.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
#         self.setLayout(self.contentlayout)

        self.points_holder = BaseWidget(show=True,group=True,title="Points",align=QtCore.Qt.AlignLeft)
        
        
        self.dual_lattice_ck = QtGui.QCheckBox("Dual Lattice")
        self.dual_lattice_ck.setChecked(True)
        self.carbon_lattice_ck = QtGui.QCheckBox("Carbon Lattice")
        self.carbon_lattice_ck.setChecked(True)
        self.con_carbon_lattice_ck = QtGui.QCheckBox("Constrained Carbon Lattice")
        self.con_carbon_lattice_ck.setChecked(True)
        
        self.points_holder.addWidgets([self.dual_lattice_ck,self.carbon_lattice_ck,self.con_carbon_lattice_ck],
                                       align=QtCore.Qt.AlignLeft,stack="V")

        
        
        self.formats_holder = BaseWidget(group=True,show=True,title="File Format(s)",
                                                align = QtCore.Qt.AlignTop)
        #self.formats_holder.FormLayout.setContentsMargins(5,5,5,5)
        self.formats={}
        
        self.formats['xyz'] = QtGui.QCheckBox(".xyz")
        self.formats['xyz'].setChecked(True)
        self.formats_holder.addWidgets(self.formats.values(),align=QtCore.Qt.AlignLeft)
        
        self.info_holder = BaseWidget(group=True,show=True,title="Structure",
                                                align = QtCore.Qt.AlignTop)
        
        self.info_ck = QtGui.QCheckBox("Information File: ")
        self.info_ck.setChecked(True)
        self.info_fname_entry = QtGui.QLineEdit("structure_info.txt")
        self.image_ck = QtGui.QCheckBox("Image")
        self.image_ck.setChecked(True)
        self.video_ck = QtGui.QCheckBox("Video")
        self.info_holder.addWidgets([self.info_ck,self.info_fname_entry],align=QtCore.Qt.AlignLeft)
        self.info_holder.addWidget(self.image_ck,align=QtCore.Qt.AlignLeft)
        self.info_holder.addWidget(self.video_ck,align=QtCore.Qt.AlignLeft)
        
        
        self.output_holder = BaseWidget(group=True,show=True,title="Output",
                                                align = QtCore.Qt.AlignTop)
        

        self.directory_entry = QtGui.QLineEdit("")
        self.directory_browse_bt= QtGui.QPushButton("Browse")  
        self.connect(self.directory_browse_bt,QtCore.SIGNAL("clicked()"),self.browse)
        self.output_holder.addWidgets([QL("Directory:"),self.directory_entry,self.directory_browse_bt],align=QtCore.Qt.AlignLeft)
        #self.output_holder.addWidget(self.directory_browse_bt)
        
        self.export_bt= QtGui.QPushButton("Export")        
        self.connect(self.export_bt,QtCore.SIGNAL("clicked()"),self.export)
        
        self.addWidget(self.points_holder,0,0)
        self.addWidget(self.formats_holder,1,0) 
        self.addWidget(self.info_holder,2,0) 
        self.addWidget(self.output_holder,3,0) 
        self.addWidget(HolderWidget(self.export_bt),6,0) 
        
    def browse(self):
        folder  = browse_to_dir()
        if(folder==None):return
        self.directory_entry.setText(folder)
        
    def export(self):
        dir = self.directory_entry.text().strip()
        if(len(dir)==0):
            printe("No output directory")
            return
        
        dargs={}
        dargs['folder'] = dir
        dargs['save_info'] =self.info_ck.isChecked()
        dargs['info_file'] = self.info_fname_entry.text()
        dargs['save_image'] =self.image_ck.isChecked()
        dargs['save_video'] =self.video_ck.isChecked()
        dargs['save_dual_lattice']=self.dual_lattice_ck.isChecked()
        dargs['save_carbon_lattice']=self.carbon_lattice_ck.isChecked()
        dargs['save_con_carbon_lattice']=self.con_carbon_lattice_ck.isChecked()
        dargs['formats'] = [key for key in self.formats.keys() if self.formats[key].isChecked()]
        
        
        printl("formats",dargs['formats'])
        
        self.export_structure.emit(dargs)
        
    def bringToFront(self):
        self.raise_()
        self.show()  
        
        
    def sizeHint(self):
        return QtCore.QSize(300,200) 
                 