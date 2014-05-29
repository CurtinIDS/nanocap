'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: May 21, 2014
Copyright Marc Robinson  2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
New list view with delegate for closing
and future functionality

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
'''

import os,time,platform,random,math,copy
from nanocap.core.globals import *
from nanocap.gui.settings import * 
from nanocap.gui.common import *
from nanocap.gui.widgets import *
from nanocap.gui.listitemdelegate import *
from nanocap.core.util import *
from nanocap.rendering import vtkqtrenderwidgets

class StructureList(QtGui.QListView):
    def __init__(self,gui):
        QtGui.QListView.__init__(self)
        #self.setStyleSheet("font: "+str(font_size+2)+"pt")
        self.gui = gui
        self.setSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Preferred)
        
        self.setModel(QtGui.QStandardItemModel())
        self.itemDelegate = ListItemDelegate(icons=['close_1.png'])
        self.setItemDelegate(self.itemDelegate)
        
        self.structures = []    
        
        self.gui.exportStructureWindow.export_structure.connect(self.exportCurrentStructure)
        self.gui.loadFromFileWindow.load_structure.connect(self.loadFromFileWindow)
        
        self.setMaximumHeight(120)

        self.connect(self.itemDelegate,QtCore.SIGNAL('buttonPressed (QModelIndex,int)'), self.list_clicked) 
        self.connect(self.itemDelegate,QtCore.SIGNAL('noButtonPressed (QModelIndex)'), self.selectStructure) 
        #self.connect(self,QtCore.SIGNAL('noButtonPressed (QModelIndex)'), self.selectStructure) 
        self.connect(self.selectionModel(),QtCore.SIGNAL('selectionChanged(QItemSelection,QItemSelection)'), self.selectionChanged) 
    
    def selectionChanged(self,to_index,from_index):
        if(len(to_index.indexes())==0):return
        self.selectStructure(to_index.indexes()[0])
        
    def list_clicked(self,index,buttonid):
        if(buttonid==0):
            self.removeStructure(index.row())
    
    def loadFromFileWindow(self):
        self.addStructure(self.gui.loadFromFileWindow.structure)
    
    def exportCurrentStructure(self,argdict):
        index = self.currentIndex()
        if(index.row()<0):return
        
        structure = self.structures[index.row()] 
        
        structure.export(**argdict)
        
        printl(argdict,structure)      
        
    
    def selectStructure(self,index):
        self.showStructure(index.row())
        
    def updateList(self):
        for i in range(0,self.model().rowCount()):
            description = self.structures[i].get_GUI_description()
            item = self.model().item(i,0)
            item.setText(str(description))
        
    def showStructure(self,i):
        printl( "Showing structure",i)
  
        for structure in self.structures:
            structure.hide()
        
        self.structures[i].show()
        
    
    def removeStructure(self,row):
        self.structures[row].hide()
        printl("removing structure",row)
        self.structures.pop(row)
        self.model().removeRow(row)
        
        pass
    
    def addStructure(self,structure=None):
        printl("adding structure",structure.type.label)
        
        structure.render(render_window_holder = self.gui.mdilayout,
                         options_holder = self.gui.dock.toolbar.MainWidget,show=False)
        
        self.structures.append(structure)
        
        if(structure!=None):
            description = structure.get_GUI_description()
            row = self.model().rowCount()
            self.model().setItem(row,0,QtGui.QStandardItem(str(description)))

        printl("update_structure",structure.type.label)
        self.connect(structure.options_window,QtCore.SIGNAL('update_structure()'), self.updateList) 

        structure.render_window.vtkframe.centerCameraOnPointSet(structure.carbon_lattice)
        
        self.showStructure(-1)
        self.setCurrentIndex(self.model().index(self.model().rowCount()-1,0))
        
    def sizeHint(self):
        return QtCore.QSize(400,200) 
