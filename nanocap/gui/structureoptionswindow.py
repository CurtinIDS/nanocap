'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Apr 15, 2014
Copyright Marc Robinson  2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

This window holds the render options
for each structure in the structure list.



-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
'''

from nanocap.core.globals import *
import os,sys,math,copy,random,time,threading,Queue,types
import numpy

from nanocap.gui.settings import *
from nanocap.gui.common import *
from nanocap.core.util import *
from nanocap.gui.widgets import SpinBox,DoubleSpinBox,HolderWidget,BaseWidget,TableWidget,ColorButton

import nanocap.gui.progresswidget as progresswidget
import nanocap.gui.structureinputoptions as structureinputoptions
import nanocap.gui.minimiserinputoptions as minimiserinputoptions 

from nanocap.core import globals,minimisation,triangulation,minimasearch,structurelog

from nanocap.rendering.defaults import *
from nanocap.gui.widgets import BaseWidget
from nanocap.gui.frozencoltablewidget import FrozenTableWidget
from nanocap.gui.tablebuttondelegate import  TableItemDelegate
from nanocap.db import database

class StructureOptionsWindow(BaseWidget):
    def __init__(self,structure):
        self.structure = structure
        self.structure_actors = self.structure.structure_actors
        
        BaseWidget.__init__(self,show=False)#,name="NoBorder")#,self.MainWindow,QtCore.Qt.Window)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)

        self.options_tab = QtGui.QTabWidget()
        self.options_tab.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        self.addWidget(self.options_tab,align=QtCore.Qt.AlignTop)
        
        #self.connect(self.options_tab,QtCore.SIGNAL('currentChanged ( int  )'),self.tab_changed)
        
        self.setup_render_widgets()
        self.setup_calc_widgets()
        self.setup_info_widgets()
        self.setup_store_widget()
#         
        self.connect(self,QtCore.SIGNAL("update_structure()"),self.structure_update)
#         
        self.options_tab.addTab(self.calc_widgets_holder,"Calculations")
        self.options_tab.addTab(self.render_widgets_holder,"Rendering")
        self.options_tab.addTab(self.info_widgets_holder,"Information")
        self.options_tab.addTab(self.store_widgets_holder,"Store")
        
        #self.calc_widgets_holder.show()

    def sizeHint(self):
        return QtCore.QSize(n_DOCKWIDTH,n_DOCKHEIGHT)
        
    def setup_store_widget(self):        
        self.store_widgets_holder = BaseWidget(scroll=True,show=True,align=QtCore.Qt.AlignTop,name="NoBorder")
        self.store_widgets_holder.setSizePolicy(QtGui.QSizePolicy.Preferred,
                                                QtGui.QSizePolicy.Expanding)
        
        self.local_holder = BaseWidget(group=True,title="Local Database",show=True,w=200,h=80,align=QtCore.Qt.AlignTop)
        self.local_holder.setSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Maximum)
        
        self.local_table = FrozenTableWidget(NFrozen=2,
                                             DelegateIcons=[[0,1,'view_1.png'],
                                                            [1,3,'question_mark.png','tick_1.png','add_1.png']]
                                             )
        self.local_table.tableView.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        
        self.local_table.setHeaders(["View","Exists","Lattice"])        
        self.local_table.addRow(["Dual Lattice",])
        self.local_table.addRow(["Carbon Lattice",])
        self.local_table.setMaximumHeight(self.local_table.sizeHint().height())
        
        
        self.local_holder.addWidget(self.local_table,align=QtCore.Qt.AlignTop)
        
        self.local_check_bt = QtGui.QPushButton("Check Database")
        self.connect(self.local_check_bt, QtCore.SIGNAL('clicked()'),self.check_local_database)
        
        
        self.local_holder.addWidget(self.local_check_bt,align=QtCore.Qt.AlignHCenter)
        
        self.connect(self.local_table,QtCore.SIGNAL("delegatePressed(QModelIndex)"),self.local_table_selected)
        
        
        self.store_widgets_holder.addWidget(self.local_holder,align=QtCore.Qt.AlignTop)
        
        
        self.online_holder = BaseWidget(group=True,title="NanoCap Online Database",show=True,w=200,h=80,align=QtCore.Qt.AlignTop)
        self.online_holder.setSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Maximum)
        self.online_table = FrozenTableWidget(NFrozen=2,
                                             DelegateIcons=[[0,1,'view_1.png'],
                                                            [1,3,'question_mark.png','tick_1.png','add_1.png']]
                                             )
        self.online_table.tableView.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        self.online_table.setHeaders(["View","Exists","Lattice"]) 
        self.online_table.addRow(["Dual Lattice",])
        self.online_table.addRow(["Carbon Lattice",])   
        self.online_table.setMaximumHeight(self.local_table.sizeHint().height())    
        #self.connect(self.online_table,QtCore.SIGNAL("delegatePressed(QModelIndex)"),self.online_table_selected)
        
        self.online_holder.addWidget(self.online_table,align=QtCore.Qt.AlignTop)
        self.online_check_bt = QtGui.QPushButton("Check Database")
        self.online_holder.addWidget(self.online_check_bt,align=QtCore.Qt.AlignHCenter)
        
        self.store_widgets_holder.addWidget(self.online_holder,align=QtCore.Qt.AlignTop)
    
    def check_local_database(self):
        exists = self.compare_dual_lattice_to_local_database()
        if exists:
            self.local_table.ButtonDelegates[1].mode[0]  = 1
        else:
            self.local_table.ButtonDelegates[1].mode[0]  = 2
            
        exists = self.compare_carbon_lattice_to_local_database()
        if exists:
            self.local_table.ButtonDelegates[1].mode[1]  = 1
        else:
            self.local_table.ButtonDelegates[1].mode[1]  = 2
        self.local_table.repaint()

        
    def local_table_selected(self,index):
        col,row = index.column(),index.row()
        mode = self.local_table.ButtonDelegates[col].mode[row]
        printl("StructureSelected",row,col,"mode",mode)
        if(row==0):
            if(col==1):
                if(mode==0):
                    exists =  self.compare_dual_lattice_to_local_database()
                    if exists:
                        self.local_table.ButtonDelegates[col].mode[row]  = 1
                    else:
                        self.local_table.ButtonDelegates[col].mode[row]  = 2
                if(mode==2):
                    self.add_dual_lattice_to_local_database()
                
                self.local_table.ButtonDelegates[col].mode[row]-=1 
                printl("mode",self.local_table.ButtonDelegates[col].mode)
        if(row==1):
            if(col==1):
                if(mode==0):
                    exists =  self.compare_carbon_lattice_to_local_database()
                    if exists:
                        self.local_table.ButtonDelegates[col].mode[row]  = 1
                    else:
                        self.local_table.ButtonDelegates[col].mode[row]  = 2
                if(mode==2):
                    self.add_carbon_lattice_to_local_database()
                
                self.local_table.ButtonDelegates[col].mode[row]-=1 
                printl("mode",self.local_table.ButtonDelegates[col].mode)    
        
        self.local_table.repaint()
        
    def add_dual_lattice_to_local_database(self):
        db = database.Database()
        db.add_dual_lattice_structure(self.structure)
        self.local_table.ButtonDelegates[1].mode[0]  = 1
    
    def add_carbon_lattice_to_local_database(self):
        db = database.Database()
        db.add_carbon_lattice_structure(self.structure)
        self.local_table.ButtonDelegates[1].mode[1]  = 1
    
    def compare_carbon_lattice_to_local_database(self):
        db = database.Database()
        db.init()
        exists = db.check_carbon_lattice_duplicates(self.structure)
        printl("exists",exists)
        return exists
    
    def compare_dual_lattice_to_local_database(self):
        db = database.Database()
        db.init()
        exists = db.check_dual_lattice_duplicates(self.structure)
        printl("exists",exists)
        return exists
        
    def setup_render_widgets(self):
        self.render_widgets_holder = BaseWidget(scroll=True,group=False,title="",show=True,align=QtCore.Qt.AlignTop,
                                                name="NoBorder")
                
        self.points_widgets_holder = BaseWidget(group=True,title="Points && Atoms",show=True,align=QtCore.Qt.AlignTop,
                                                name="NoBorder")
        
        if(self.structure.has_child_structures):self.points_widgets_holder.addHeader(self.structure.type.label,
                                                                                     bold=True,frame=False)

        
            
        
        colwidths = [120,30,30,50,30,30]
        self.render_points_table = TableWidget(numpy.sum(colwidths),60)
        self.render_points_table.verticalHeader().hide()
        self.render_points_table.setupHeaders(["Points","Ren","IDs","Rad","Col","Box"],
                                              colwidths)
        
        self.render_points_table.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding,
                                               QtGui.QSizePolicy.Fixed)
        
        if(self.structure.parent_structure!=None):
            header = self.render_points_table.horizontalHeader()
            header.setFixedHeight(0)
            
        #self.render_points_table.setFixedHeight(self.render_points_table)
        
        self.points_widgets_holder.addWidget(self.render_points_table,align=QtCore.Qt.AlignTop)
        
        self.toggle_points_CB = {}
        self.toggle_box_CB = {}
        self.toggle_label_CB = {}
        self.point_colour_BT = {}
        self.point_radius_SB = {}
        
        #if(self.structure.type=="Fullerene"):
            
        for key in POINTKEYS:
            self.toggle_points_CB[key] = QtGui.QCheckBox()
            self.toggle_label_CB[key] = QtGui.QCheckBox()
            self.toggle_box_CB[key] = QtGui.QCheckBox()
            self.point_radius_SB[key] = DoubleSpinBox()
            self.point_radius_SB[key].setValue(RADIUS[key])
            self.point_radius_SB[key].setSingleStep(0.01)
            self.point_radius_SB[key].setFixedWidth(50)
            self.point_colour_BT[key] = ColorButton(COLORS[key],25)
            
            self.render_points_table.insertRow(0)
            self.render_points_table.setItem(0,0,QtGui.QTableWidgetItem(key))
            self.render_points_table.setCellWidget(0,1,HolderWidget(self.toggle_points_CB[key]))
            self.render_points_table.setCellWidget(0,2,HolderWidget(self.toggle_label_CB[key]))
            self.render_points_table.setCellWidget(0,3,HolderWidget(self.point_radius_SB[key]))
            self.render_points_table.setCellWidget(0,4,HolderWidget(self.point_colour_BT[key]))
            self.render_points_table.setCellWidget(0,5,HolderWidget(self.toggle_box_CB[key]))
            
            call = lambda flag,key=key : self.toggle_points(flag,key)
            self.connect(self.toggle_points_CB[key], QtCore.SIGNAL('toggled(bool)'), call)
            self.toggle_points_CB[key].setChecked(True)
            call = lambda flag,key=key : self.toggle_labels(flag,key)  
            self.connect(self.toggle_label_CB[key], QtCore.SIGNAL('toggled(bool)'), call)
            call = lambda rad,key=key : self.structure.structure_actors.set_point_radius(rad,key)
            self.connect(self.point_radius_SB[key], QtCore.SIGNAL('valueChanged(  double )'), call)
            call = lambda r,g,b,key=key: self.structure_actors.set_point_color(r,g,b,key)
            self.connect(self.point_colour_BT[key], QtCore.SIGNAL('colorChanged(int,int,int)'), call)
            call = lambda flag,key=key : self.toggle_box(flag,key)
            self.connect(self.toggle_box_CB[key], QtCore.SIGNAL('toggled(bool)'), call)
  
        
        
        printl(self.structure.type.label, self.render_points_table.sizeHint())
        self.render_widgets_holder.addWidget(self.points_widgets_holder,align=QtCore.Qt.AlignTop)
        
        self.render_points_table.setFixedHeight(self.render_points_table.sizeHint().height())
        
#         if not (self.structure.has_child_structures):  
#             self.render_widgets_holder.update()
#             return
            
        self.general_widgets_holder = BaseWidget(group=True,title="General",show=True,align=QtCore.Qt.AlignTop,
                                                 name="NoBorder")
        
        #self.general_widgets_holder.addHeader("General")
        
        
        
        
        self.render_general_table = TableWidget(260,90)
        self.render_general_table.verticalHeader().hide()
        self.render_general_table.setupHeaders(["Option","Ren","Parameters"],
                                               [100,30,130])
        
        self.general_widgets_holder.addWidget(self.render_general_table,align=QtCore.Qt.AlignTop)
        
        self.toggle_triangles_CB = QtGui.QCheckBox()
        self.render_general_table.insertRow(0)
        self.render_general_table.insertRow(1)
        self.render_general_table.insertRow(2)
        self.render_general_table.setItem(0,0,QtGui.QTableWidgetItem("Triangulation"))
        self.render_general_table.setCellWidget(0,1,HolderWidget(self.toggle_triangles_CB))
        
        self.connect(self.toggle_triangles_CB, QtCore.SIGNAL('toggled(bool)'), self.structure_actors.toggle_triangles)
        
        
        self.toggle_carbon_bonds_CB = QtGui.QCheckBox()
        lb = QtGui.QLabel("Thickness")
        self.cardbonds_thickness_SB = DoubleSpinBox()
        self.cardbonds_thickness_SB.setMinimum(0.0001)
        self.cardbonds_thickness_SB.setValue(BOND_THICKNESS)
        self.cardbonds_thickness_SB.setDecimals(4)
        self.cardbonds_thickness_SB.setSingleStep(0.001)
        self.cardbonds_thickness_SB.setFixedWidth(60)
        
        
        
        self.render_general_table.setItem(1,0,QtGui.QTableWidgetItem("Carbon bonds"))
        self.render_general_table.setCellWidget(1,1,HolderWidget(self.toggle_carbon_bonds_CB))
        self.render_general_table.setCellWidget(1,2,HolderWidget((QL("Thickness"),self.cardbonds_thickness_SB)))
        
        self.connect(self.toggle_carbon_bonds_CB, QtCore.SIGNAL('toggled(bool)'), self.structure_actors.toggle_carbon_bonds)
        self.connect(self.cardbonds_thickness_SB, QtCore.SIGNAL('valueChanged(  double )'), self.structure_actors.set_carbon_bond_thickness)
        
        self.toggle_carbon_rings_CB = QtGui.QCheckBox()
       
        self.render_general_table.setItem(2,0,QtGui.QTableWidgetItem("Carbon rings"))
        self.render_general_table.setCellWidget(2,1,HolderWidget(self.toggle_carbon_rings_CB))
        self.connect(self.toggle_carbon_rings_CB, QtCore.SIGNAL('toggled(bool)'), self.structure_actors.toggle_carbon_rings)

        self.toggle_schlegel_CB = QtGui.QCheckBox()
        
        self.render_widgets_holder.addWidget(self.general_widgets_holder,align=QtCore.Qt.AlignTop)
        
        self.render_general_table.update()
        self.render_widgets_holder.update()
        self.general_widgets_holder.update()
        
        
        #self.render_points_table.updateGeometry()
        
        
        
        
        
        
        
    def toggle_points(self,flag,key):
        printl("toggle points",flag,key)
        self.structure_actors.toggle_points(flag,key,frame="3D")
        #if(self.toggle_schlegel_CB.isChecked()):
        self.structure_actors.toggle_points(flag,key+'_S',frame="Schlegel")
            
        #if not flag:self.structure_actors.toggle_points(flag,key+'_S',frame="Schlegel")
        
    def toggle_labels(self,flag,key):
        printl("toggle labels",flag,key)
        self.structure_actors.toggle_point_labels(flag,key,frame="3D")
        #if(self.toggle_schlegel_CB.isChecked()):
        self.structure_actors.toggle_point_labels(flag,key+'_S',frame="Schlegel")
            
        #if not flag:self.structure_actors.toggle_point_labels(flag,key+'_S',frame="Schlegel")    
    
    def toggle_box(self,flag,key):
        printl("toggle box",flag,key)
        self.structure_actors.toggle_point_box(flag,key,frame="3D")
        #if(self.toggle_schlegel_CB.isChecked()):
        self.structure.structure_actors.toggle_point_box(flag,key+'_S',frame="Schlegel")

    def select_calc_widget(self,row):
        for option in self.calc_options:
            self.calc_holders[option].hide()
            
        self.calc_holders[self.calc_options[row]].show()
        
        
    def setup_calc_widgets(self):    
        self.calc_widgets_holder = BaseWidget(scroll=True,group=False,title="",show=False,align=QtCore.Qt.AlignTop)#,w=100,h=40) 
        self.calc_widgets_holder.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Maximum)
 
        
        self.calc_list = QtGui.QListWidget()
        self.calc_list.setMaximumHeight(80)
        self.calc_list.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Fixed)
        self.calc_widgets_holder.addWidget(self.calc_list,align=QtCore.Qt.AlignTop)
           
        #self.connect(self.calc_list,QtCore.SIGNAL('clicked (QModelIndex)'), self.select_calc_widget) 
        self.connect(self.calc_list,QtCore.SIGNAL('currentRowChanged   (int)'), self.select_calc_widget) 
        
        if(self.structure.type==CAPPEDNANOTUBE or self.structure.type==FULLERENE):
            self.calc_options = ['Input','Dual Lattice','Carbon Lattice','Bonds','Rings','Schlegel']
        else:
            self.calc_options = ['Input','Bonds','Rings','Schlegel']
        
        
        self.calc_holders = {}
        for option in self.calc_options:
            item = QtGui.QListWidgetItem(option)
            self.calc_list.addItem(item)
            self.calc_holders[option] = BaseWidget(group=True,title=option,show=False,align=QtCore.Qt.AlignTop)#,w=n_DOCKWIDTH,h=50)
            self.calc_holders[option].setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Preferred)
            self.calc_widgets_holder.addWidget(self.calc_holders[option],align=QtCore.Qt.AlignTop)

        if(self.structure.type==FULLERENE):
            self.InputWidgets = structureinputoptions.FullereneInputOptions(structure=self.structure,gen_buttons=True)
            #self.InputWidgets.show()
            self.calc_holders['Input'].addWidget(self.InputWidgets,align=QtCore.Qt.AlignHCenter)
        
        if(self.structure.type==CAPPEDNANOTUBE):
            self.InputWidgets = structureinputoptions.CappedNanotubeInputOptions(structure=self.structure,gen_buttons=True)
            #self.InputWidgets.show()
            self.calc_holders['Input'].addWidget(self.InputWidgets,align=QtCore.Qt.AlignHCenter)  
        
        if(self.structure.type==NANOTUBE):
            self.InputWidgets = structureinputoptions.NanotubeInputOptions(structure=self.structure,gen_buttons=True)
            #self.InputWidgets.show()
            self.calc_holders['Input'].addWidget(self.InputWidgets,align=QtCore.Qt.AlignHCenter)      

        
        if(self.structure.type==CAPPEDNANOTUBE or self.structure.type==FULLERENE):
            self.dual_lattice_min_options = minimiserinputoptions.DualLatticeMinimisationOptions(structure=self.structure,buttons=True)
            self.calc_holders['Dual Lattice'].addWidget(self.dual_lattice_min_options,align=QtCore.Qt.AlignHCenter)   
            
            self.calculate_carbon_lattice_BT = QtGui.QPushButton("Triangulate and Construct from Dual")
            self.calc_holders['Carbon Lattice'].addWidgets((self.calculate_carbon_lattice_BT,),align=QtCore.Qt.AlignHCenter)
            self.connect(self.calculate_carbon_lattice_BT, QtCore.SIGNAL('clicked()'), self.construct_carbon_lattice)
            
            self.carbon_lattice_min_options = minimiserinputoptions.CarbonLatticeMinimisationOptions(structure=self.structure,buttons=True)
            self.calc_holders['Carbon Lattice'].addWidget(self.carbon_lattice_min_options,align=QtCore.Qt.AlignHCenter)   
        
        self.schlegel_gamma_SB = DoubleSpinBox()
        self.schlegel_gamma_SB.setValue(SCHLEGEL_G)
        self.schlegel_gamma_SB.setMinimum(0)
        self.schlegel_gamma_SB.setMaximum(5.0)
        self.schlegel_gamma_SB.setDecimals(4)
        self.schlegel_gamma_SB.setSingleStep(0.001)
        self.schlegel_gamma_SB.setFixedWidth(80)
        self.schlegel_cutoff_SB = DoubleSpinBox()
        self.schlegel_cutoff_SB.setValue(SCHLEGEL_R)
        self.schlegel_cutoff_SB.setMinimum(-100)
        self.schlegel_cutoff_SB.setMaximum(100)
        self.schlegel_cutoff_SB.setSingleStep(0.5)
        self.schlegel_cutoff_SB.setFixedWidth(80)
        
        self.calculate_schlegel_BT = QtGui.QPushButton("Calculate")
        
        self.connect(self.calculate_schlegel_BT, QtCore.SIGNAL('clicked()'), self.calculate_schlegel)

        self.calc_holders['Schlegel'].addWidgets((QtGui.QLabel("Gamma"),self.schlegel_gamma_SB,
                                              QtGui.QLabel("Cutoff"),self.schlegel_cutoff_SB),align=QtCore.Qt.AlignHCenter)
        
        self.calc_holders['Schlegel'].addWidget(self.calculate_schlegel_BT,align=QtCore.Qt.AlignHCenter)
        
        self.calculate_bonds_BT = QtGui.QPushButton("Calculate")
        
        self.connect(self.calculate_bonds_BT, QtCore.SIGNAL('clicked()'), self.calculate_bonds)

        self.calc_holders['Bonds'].addWidget(self.calculate_bonds_BT,align=QtCore.Qt.AlignHCenter)
                
        self.calculate_rings_BT = QtGui.QPushButton("Calculate")
        
        self.connect(self.calculate_rings_BT, QtCore.SIGNAL('clicked()'), self.calculate_rings)

        self.calc_holders['Rings'].addWidget(self.calculate_rings_BT,align=QtCore.Qt.AlignHCenter)
        
        for option in self.calc_options:
            self.calc_holders[option].hide()
        
        #raw_input()
        
    def construct_carbon_lattice(self):
        self.structure.construct_carbon_lattice()
        self.structure.render_update()
        
        #self.structure_actors.update_actors()
    def calculate_bonds(self):
        self.structure.calculate_carbon_bonds()
        self.structure.render_update()
        #self.structure_actors.update_actors()
        
    def calculate_rings(self):
        self.structure.calculate_rings()
        #self.structure_actors.update_actors()
        self.structure.render_update()
        
    def calculate_schlegel(self):
        self.structure.calculate_schlegel(self.schlegel_gamma_SB.value(),self.schlegel_cutoff_SB.value())
        #self.structure_actors.update_actors()
        self.structure.render_update()
        
    def structure_update(self):
        
        self.update_info_widgets()
        
    
        
        
    def update_info_widgets(self):
        if(self.structure.parent_structure!=None):
            #we do not want to update child structure info, it should be part
            #of the parent structure's info.
            return
        
        
        self.info_table.setRowCount(0)
        
        fdata = self.structure.format_data()
        
        for table in fdata.keys():
            if(len(fdata[table].values())==0):continue
            self.info_table.insertRow(self.info_table.rowCount())
            item = QtGui.QTableWidgetItem(table)
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            lab = QL(table,font="bold")
            self.info_table.setCellWidget(self.info_table.rowCount()-1,0,HolderWidget(lab))
            self.info_table.setSpan(self.info_table.rowCount()-1,0,1,2);  
            
            for key,d in fdata[table].items():
                #out += self.col2.format(key,d)  
                printl("table,key,val",table,key,d)
                self.info_table.insertRow(self.info_table.rowCount())
                label = key
                item = QtGui.QTableWidgetItem(key)
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                thisdata = QtGui.QTableWidgetItem(str(d))
                thisdata.setTextAlignment(QtCore.Qt.AlignCenter)
                self.info_table.setItem(self.info_table.rowCount()-1,0,item)
                self.info_table.setItem(self.info_table.rowCount()-1,1,thisdata)
           
    def setup_info_widgets(self):
        self.info_widgets_holder = BaseWidget(scroll=True,group=False,title="",show=True,align=QtCore.Qt.AlignTop)    
        
        self.info_table = TableWidget(200,500)
        self.info_table.setupHeaders(["Property","Value"],[100,100])
        self.info_table.verticalHeader().hide()
        
        self.update_info_widgets()
                
        self.info_widgets_holder.addWidget(self.info_table,align=QtCore.Qt.AlignTop)
        
        