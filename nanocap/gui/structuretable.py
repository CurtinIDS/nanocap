'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Apr 14, 2014
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
from nanocap.gui.widgets import SpinBox,DoubleSpinBox,HolderWidget,BaseWidget,TableWidget,ColorButton
from nanocap.gui.frozencoltablewidget import FrozenTableWidget
from nanocap.gui.tablebuttondelegate import  TableItemDelegate

class StructureTable(QtGui.QWidget):
    def __init__(self,StructureLog):
        self.StructureLog = StructureLog
        QtGui.QWidget.__init__(self)

        self.setWindowTitle("Generated Structures "+str(self.StructureLog.type))
        self.setSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Preferred)
        
        self.general_table = FrozenTableWidget(NFrozen=1,
                                             DelegateIcons=[[0,1,'view_1.png'],
                                                            ]
                                             )

        self.dual_lattice_table = FrozenTableWidget(NFrozen=2,
                                             DelegateIcons=[[0,3,'question_mark.png','tick_1.png','add_1.png'],
                                                            [1,3,'question_mark.png','tick_1.png','add_1.png']]
                                             )
        self.carbon_lattice_table = FrozenTableWidget(NFrozen=2,
                                             DelegateIcons=[[0,3,'question_mark.png','tick_1.png','add_1.png'],
                                                            [1,3,'question_mark.png','tick_1.png','add_1.png']]
                                             )
        
        self.rings_table = FrozenTableWidget(NFrozen=0,
                                             DelegateIcons=[]
                                             )
        
        '''
        local column, modes:  0=unchecked, 1=exists, 2=doesnotexist
        
        '''
        
        self.general_table.setHeaders(["View"])#+self.StructureLog.general_headers)        
        self.dual_lattice_table.setHeaders(["Local","Web"]+self.StructureLog.dual_lattice_headers)
        self.carbon_lattice_table.setHeaders(["Local","Web"]+self.StructureLog.carbon_lattice_headers)
        self.rings_table.setHeaders(self.StructureLog.rings_headers)        
               
        self.contentlayout = QtGui.QGridLayout(self)
        self.contentlayout.setContentsMargins(5,5,5,5)
        self.contentlayout.setSpacing(0)
        self.contentlayout.setAlignment(QtCore.Qt.AlignHCenter)
        self.setLayout(self.contentlayout)
        

        self.splitter = QtGui.QSplitter()
        self.splitter.addWidget(HolderWidget([QL("General",header=True,align=QtCore.Qt.AlignCenter),self.general_table],stack="V"))
        self.splitter.addWidget(HolderWidget([QL("Dual Lattice",header=True,align=QtCore.Qt.AlignCenter),self.dual_lattice_table],stack="V"))
        self.splitter.addWidget(HolderWidget([QL("Carbon Lattice",header=True,align=QtCore.Qt.AlignCenter),self.carbon_lattice_table],stack="V"))
        self.splitter.addWidget(HolderWidget([QL("Rings",header=True,align=QtCore.Qt.AlignCenter),self.rings_table],stack="V"))
        self.splitter.setHandleWidth(1)
        self.contentlayout.addWidget(self.splitter,0,0)
        
        self.general_table.setMinimumWidth(self.general_table.sizeHint().width())       

        self.general_table.link_table(self.dual_lattice_table)
        self.dual_lattice_table.link_table(self.carbon_lattice_table)
        self.carbon_lattice_table.link_table(self.rings_table)
        
        self.connect(self.general_table,QtCore.SIGNAL("delegatePressed(QModelIndex)"),self.viewStructure)
        self.connect(self.dual_lattice_table,QtCore.SIGNAL("delegatePressed(QModelIndex)"),self.dualLatticeSelected)
        self.connect(self.carbon_lattice_table,QtCore.SIGNAL("delegatePressed(QModelIndex)"),self.carbonLatticeSelected)
            
    def reset_db_buttons(self):
        self.dual_lattice_table.set_all_delegates_to_mode(0)
        self.carbon_lattice_table.set_all_delegates_to_mode(0)
    
    def viewStructure(self,index):
        col,row = index.column(),index.row()
        self.emit(QtCore.SIGNAL("viewStructure(int)"),row)
    
    def carbonLatticeSelected(self,index):
        col,row = index.column(),index.row()
        mode = self.carbon_lattice_table.ButtonDelegates[col].mode[row]
        printl("StructureSelected",row,col,self.dual_lattice_table.ButtonDelegates[col].mode[row])

        if(mode==0):
            exists = self.compare_carbon_lattice_at_row_local_database(row)
            if exists:
                self.carbon_lattice_table.ButtonDelegates[0].mode[row]  = 1
            else:
                self.carbon_lattice_table.ButtonDelegates[0].mode[row]  = 2
            self.carbon_lattice_table.ButtonDelegates[0].mode[row]-=1    
        if(mode==1):
            self.carbon_lattice_table.ButtonDelegates[0].mode[row]-=1
        if(mode==2):
            #check if mode of dual lattice at this position is 1
            if(self.dual_lattice_table.ButtonDelegates[0].mode[row]==1):
                self.add_carbon_lattice_at_row_local_database(row)
            self.carbon_lattice_table.ButtonDelegates[0].mode[row]-=1
        
    def dualLatticeSelected(self,index):
        col,row = index.column(),index.row()
        mode = self.dual_lattice_table.ButtonDelegates[col].mode[row]
        printl("StructureSelected",row,col,self.dual_lattice_table.ButtonDelegates[col].mode[row])

        if(mode==0):
            exists = self.compare_dual_lattice_at_row_local_database(row)
            if exists:
                self.dual_lattice_table.ButtonDelegates[0].mode[row]  = 1
            else:
                self.dual_lattice_table.ButtonDelegates[0].mode[row]  = 2
            self.dual_lattice_table.ButtonDelegates[0].mode[row]-=1
        if(mode==1):
            self.dual_lattice_table.ButtonDelegates[0].mode[row]-=1
        if(mode==2):
            self.add_dual_lattice_at_row_local_database(row)
            self.dual_lattice_table.ButtonDelegates[0].mode[row]-=1
                
    def add_dual_lattice_at_row_local_database(self,row):
        structure  = self.StructureLog.get_structure_at_position(row,sorted=True)
        self.StructureLog.add_dual_lattice_local_database(structure)
        self.dual_lattice_table.ButtonDelegates[0].mode[row]  = 1
    
    def compare_dual_lattice_at_row_local_database(self,row):
        structure  = self.StructureLog.get_structure_at_position(row,sorted=True)
        exists = self.StructureLog.compare_dual_lattice_local_database(structure)
        return exists
    
    def add_carbon_lattice_at_row_local_database(self,row):
        structure  = self.StructureLog.get_structure_at_position(row,sorted=True)
        self.StructureLog.add_carbon_lattice_local_database(structure)
        self.carbon_lattice_table.ButtonDelegates[0].mode[row]  = 1
    
    def compare_carbon_lattice_at_row_local_database(self,row):
        structure  = self.StructureLog.get_structure_at_position(row,sorted=True)
        exists = self.StructureLog.compare_carbon_lattice_local_database(structure)
        return exists
                
    def compare_local_database(self):
        indexes = self.StructureLog.get_sorted_indexes()
        for count,i in enumerate(indexes):
            #structure = self.StructureLog.structures[i]
            row = count
            #here check structure
            exists = self.compare_dual_lattice_at_row_local_database(row)
            if exists:
                self.dual_lattice_table.ButtonDelegates[0].mode[row]  = 1
            else:
                self.dual_lattice_table.ButtonDelegates[0].mode[row]  = 2
                
            exists = self.compare_carbon_lattice_at_row_local_database(row)
            if exists:
                self.carbon_lattice_table.ButtonDelegates[0].mode[row]  = 1
            else:
                self.carbon_lattice_table.ButtonDelegates[0].mode[row]  = 2
            
            printl("row",row,"mode",self.dual_lattice_table.ButtonDelegates[1].mode[row],exists)
        self.dual_lattice_table.repaint()
        self.carbon_lattice_table.repaint()
        
    def reset(self):
        self.carbon_lattice_table.reset()
        self.dual_lattice_table.reset()
        self.rings_table.reset()
        self.general_table.reset()
    def sizeHint(self):
        return QtCore.QSize(800,200) 
#         
    def updateStructureTable(self): 
        self.reset()
        indexes = self.StructureLog.get_sorted_indexes()

        for count,i in enumerate(indexes):
            row_data = self.StructureLog.get_data(i)
            
            printl("received",row_data)
            self.dual_lattice_table.addRow(row_data['dual_lattices'])
            self.carbon_lattice_table.addRow(row_data['carbon_lattices'])
            self.general_table.addRow(row_data['general'])
            self.rings_table.addRow(row_data['rings'])
            
        #raw_input()
            
            