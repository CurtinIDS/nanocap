'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Apr 11, 2014
Copyright Marc Robinson  2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

Structure Generation Window
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
'''

from nanocap.core.globals import *
import os,sys,math,copy,random,time,threading,Queue,types
import numpy

from nanocap.gui.settings import *
from nanocap.gui.common import *
from nanocap.core.util import *

from nanocap.gui.widgets import SpinBox,DoubleSpinBox,HolderWidget,BaseWidget,TableWidget,ColorButton
import nanocap.gui.structuretable as structuretable
import nanocap.gui.progresswidget as progresswidget
import nanocap.gui.structureinputoptions as structureinputoptions
import nanocap.gui.minimiserinputoptions as minimiserinputoptions 

from nanocap.structures import fullerene
from nanocap.structures import cappednanotube

from nanocap.core import globals,minimisation,triangulation,minimasearch,structurelog

class StructureGenWindow(BaseWidget):
    def __init__(self,Gui,MainWindow,ThreadManager):
        self.Gui = Gui
        self.MainWindow = MainWindow
        self.ThreadManager = ThreadManager
        
        self.GenType = STRUCTURE_TYPES[FULLERENE]
        self.NanotubeWidgets = []
        self.FullereneWidgets = []
        
        BaseWidget.__init__(self,self.MainWindow,show=False,align = QtCore.Qt.AlignTop)#,QtCore.Qt.Window)
        
        self.setWindowTitle("Structure Search ")
        
        self.setSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Preferred)

        #self.grid = self.newGrid()
        
        self.ButtonsHolder = BaseWidget(self,group=False,show=True,align = QtCore.Qt.AlignTop,w=300,h=200)
        self.ButtonsHolder.setSizePolicy(QtGui.QSizePolicy.Fixed,QtGui.QSizePolicy.Preferred)
        #self.ButtonsHolder.setBackgroundColour('red')
                
        self.GenTypeBTGroup = QtGui.QButtonGroup()
        self.GenTypeBTGroup.setExclusive(True)
        self.GenFullerenceRB = QtGui.QRadioButton('Fullerene')
        self.GenFullerenceRB.setChecked(True)
        self.GenNanotubeRB = QtGui.QRadioButton('Nanotube')
        self.GenNanotubeRB.setChecked(False)
        self.connect(self.GenFullerenceRB, QtCore.SIGNAL('clicked()'), self.GenTypeChanged)
        self.connect(self.GenNanotubeRB, QtCore.SIGNAL('clicked()'), self.GenTypeChanged)
        self.GenTypeBTGroup.addButton(self.GenFullerenceRB)
        self.GenTypeBTGroup.addButton(self.GenNanotubeRB)
        
       
        self.ButtonsHolder.addWidgets((self.GenFullerenceRB,self.GenNanotubeRB))
        
        self.ButtonsHolder.addSeparator(dummy=1)
        self.setup_fullerene_widgets()
        self.setup_nanotube_widgets()
        self.ButtonsHolder.addSeparator(dummy=1)
        self.setup_minimisation_widgets()
        self.ButtonsHolder.addSeparator(dummy=1)
        self.setup_minsearch_widgets()
        
        self.SearchProgressbar = progresswidget.ProgressWidget()
        
        self.MinSearchStartBT = QtGui.QPushButton("Generate")
        self.ResetSearchBT = QtGui.QPushButton("Reset")
        self.CompareLocalBT = QtGui.QPushButton("Check Local DB")
        self.MinSearchStartBT.setMaximumWidth(100)
        self.ResetSearchBT.setMaximumWidth(100)
        self.CompareLocalBT.setMaximumWidth(130)
        self.addWidget(self.MinSearchStartBT)
        
        self.ButtonsHolder.addSeparator(dummy=True)
        
        #self.grid.addWidget(HolderWidget((self.MinSearchStartBT,self.ResetSearchBT,self.CompareLocalBT)),1,0,1,2)
        
        
        self.connect(self.MinSearchStartBT, QtCore.SIGNAL('clicked()'), self.StartMinSearch)
        self.connect(self.ResetSearchBT, QtCore.SIGNAL('clicked()'), self.ResetSearch)
        self.connect(self.SearchProgressbar.stopBT, QtCore.SIGNAL('clicked()'), self.StopMinSearch)
        self.connect(self.CompareLocalBT, QtCore.SIGNAL('clicked()'), self.compare_structures_local)
        

        self.SearchProgressbar.hide()
        
        self.structureLogs = {}
        self.structureLogs[FULLERENE] = structurelog.StructureLog(STRUCTURE_TYPES[FULLERENE])
        self.structureLogs[CAPPEDNANOTUBE] = structurelog.StructureLog(STRUCTURE_TYPES[CAPPEDNANOTUBE])
        
        self.structureTables = {}
        self.FullereneStructureTables = structuretable.StructureTable(self.structureLogs[FULLERENE])
        self.structureTables[FULLERENE] = self.FullereneStructureTables
        self.CappedNanotubeStructureTables = structuretable.StructureTable(self.structureLogs[CAPPEDNANOTUBE])
        self.structureTables[CAPPEDNANOTUBE] = self.CappedNanotubeStructureTables
        
        self.structureTables[CAPPEDNANOTUBE].hide()
        self.NanotubeWidgets.append(self.structureTables[CAPPEDNANOTUBE])
        self.FullereneWidgets.append(self.structureTables[FULLERENE])
        
        holder = HolderWidget([self.ButtonsHolder,
                                     self.structureTables[CAPPEDNANOTUBE],
                                     self.structureTables[FULLERENE]])
        
        holder.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        self.addWidget(holder)
        
        #self.grid.addWidget(self.structureTables[CAPPEDNANOTUBE],0,1)
        #self.grid.addWidget(self.structureTables[FULLERENE],0,1)
        
        self.connect(self, QtCore.SIGNAL('updateStructureTable()'), self.structureTables[FULLERENE].updateStructureTable)
        self.connect(self, QtCore.SIGNAL('updateStructureTable()'), self.structureTables[CAPPEDNANOTUBE].updateStructureTable)
        self.connect(self, QtCore.SIGNAL('updateProgress(int,QString)'), self.SearchProgressbar.updateProgress)
        self.connect(self, QtCore.SIGNAL('searchFinished()'), self.StopMinSearch)
        
        self.connect(self.structureTables[FULLERENE], QtCore.SIGNAL('viewStructure(int)'), self.viewStructure)
        self.connect(self.structureTables[CAPPEDNANOTUBE], QtCore.SIGNAL('viewStructure(int)'), self.viewStructure)

        #self.grid.addWidget(self.SearchProgressbar,1,0,1,2)
        self.addWidget(HolderWidget((self.MinSearchStartBT,self.ResetSearchBT,self.CompareLocalBT)))
        self.addWidget(self.SearchProgressbar)
        
        self.GenTypeChanged()
    def bringToFront(self):
        self.raise_()
        self.show()

        
    def viewStructure(self,row):
        
        structure  = self.structureLogs[self.GenType.enum].get_structure_at_position(row,sorted=True)
        printd("selected structure",
               self.structureLogs[self.GenType.enum].get_structure_at_position(row,sorted=True))   
        
        self.MainWindow.activateWindow()   
        self.MainWindow.gui.dock.toolbar.structurelist.addStructure(structure) 
        
    def StructureFound(self):
        printl("StructureFound!")
        self.emit(QtCore.SIGNAL("updateStructureTable()"))
        self.emit(QtCore.SIGNAL("updateProgress(int,QString)"),self.Searcher.NUnique,self.Searcher.status)
    
    def compare_structures_local(self):
        self.structureTables[self.GenType.enum].compare_local_database()
    
    def StartMinSearch(self):
        
        self.structureTables[self.GenType.enum].reset_db_buttons()
        
        self.SearchProgressbar.reset(self.NStructures.value())
        self.SearchProgressbar.show()
        
        self.MinSearchStartBT.hide()
        self.ResetSearchBT.hide()
        self.CompareLocalBT.hide()
        
        self.ThreadManager.submit_to_queue(self.MinSearch)
        #self.resize(self.sizeHint())     
    
    def ResetSearch(self):
        #self.structureLogs = {}
        self.structureLogs[FULLERENE].reset() 
        self.structureLogs[CAPPEDNANOTUBE].reset() 
        self.structureTables[FULLERENE].reset()
        self.structureTables[CAPPEDNANOTUBE].reset()
        
    def StopMinSearch(self):
        self.Searcher.StopMin=1
        while not self.Searcher.finished:
            pass
        
        self.MinSearchStartBT.show()
        self.ResetSearchBT.show()
        self.CompareLocalBT.show()
        self.SearchProgressbar.hide()
        #self.resize(self.sizeHint())     
    
    def DualLatticeMinimiserCallback(self):
        printl(self.Dminimiser.__repr__())
        self.emit(QtCore.SIGNAL("updateProgress(int,QString)"),self.Searcher.NUnique,self.Dminimiser.__repr__())
    
    def CarbonLatticeMinimiserCallback(self):
        printl(self.Cminimiser.__repr__())
        self.emit(QtCore.SIGNAL("updateProgress(int,QString)"),self.Searcher.NUnique,self.Cminimiser.__repr__())
    
    def MinSearch(self):
        '''
        we can now thread this as we have set the callback to self.structurefound which
        can be used to update progressbar etc
        
        '''
        if(self.GenType==FULLERENE):
            self.fullerene_input_widgets.initialise_structure()
            struct = self.fullerene_input_widgets.structure
        
        
        if(self.GenType==CAPPEDNANOTUBE):
            self.cappednanotube_inputwidgets.initialise_structure()
            struct = self.cappednanotube_inputwidgets.structure
            
        
        DualLatticeMinimiser = str(self.dual_lattice_min_options.FF_type_cb.currentText())
        DualLattice_mintol=float(self.dual_lattice_min_options.min_tol_entry.text())
        DualLattice_minsteps=self.dual_lattice_min_options.min_steps_entry.value()
        Dmintype=str(self.dual_lattice_min_options.min_type_cb.currentText())  
        
        CarbonLatticeMinimiser = str(self.carbon_lattice_min_options.FF_type_cb.currentText())
        CarbonLattice_mintol=float(self.carbon_lattice_min_options.min_tol_entry.text())
        CarbonLattice_minsteps=self.carbon_lattice_min_options.min_steps_entry.value()
        Cmintype=str(self.carbon_lattice_min_options.min_type_cb.currentText())        
            
        NStructures = self.NStructures.value()
        NMaxStructures = self.NMaxStructures.value()
        BasinClimb = self.BasinClimbCK.isChecked()
        CalcRings = self.CalcRingsCK.isChecked()
             
        self.Dminimiser = minimisation.DualLatticeMinimiser(FFID=DualLatticeMinimiser,structure = struct,
                                                            callback=self.DualLatticeMinimiserCallback)
        self.Dminimiser.mintype = Dmintype
        self.Dminimiser.ftol=DualLattice_mintol
        self.Dminimiser.minsteps=DualLattice_minsteps
        self.Cminimiser = minimisation.CarbonLatticeMinimiser(FFID=CarbonLatticeMinimiser,structure = struct,
                                                              callback=self.CarbonLatticeMinimiserCallback)
        self.Cminimiser.mintype = Cmintype
        self.Cminimiser.ftol=CarbonLattice_mintol
        self.Cminimiser.minsteps=CarbonLattice_minsteps
        
        self.Searcher = minimasearch.MinimaSearch(self.Dminimiser,carbon_lattice_minimiser= self.Cminimiser,
                                             basin_climb=BasinClimb,calc_rings=CalcRings,
                                             callback = self.StructureFound,
                                             StructureLog = self.structureLogs[self.GenType.enum])
        
        self.Searcher.StopMin=0
        self.Searcher.start_search(struct.dual_lattice,NStructures,NMaxStructures)
        
        self.emit(QtCore.SIGNAL("searchFinished()"))
        
    def setup_minsearch_widgets(self):

        self.MinSearchWidgetsHolder = BaseWidget(group=True,title="Structure Search Options",
                                                        show=True)
        
        self.MinSearchWidgetsHolder.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Preferred)
        
        self.ButtonsHolder.addWidget(self.MinSearchWidgetsHolder)
        
        row = self.MinSearchWidgetsHolder.newGrid()
        
        self.NStructures = SpinBox()
        self.NStructures.setValue(10)
        self.NStructures.setFixedWidth(50)
        self.NMaxStructures = SpinBox()
        self.NMaxStructures.setValue(100)
        self.NMaxStructures.setFixedWidth(50)
        row.addWidget(QL("N Minima"),0,0)
        row.addWidget(self.NStructures,0,1)
        row.addWidget(QL("N Max Minima"),0,2)
        row.addWidget(self.NMaxStructures,0,3)
        
        self.BasinClimbCK = QtGui.QCheckBox('Basin Climbing')
        self.BasinClimbCK.setChecked(True)
        row.addWidget(self.BasinClimbCK,1,0,1,4) 
                
        
        self.ResetLoopCK = QtGui.QCheckBox('Reset Per Iteration')
        self.ResetLoopCK.setChecked(False)
        self.PerturbLoopCK = QtGui.QCheckBox('Random Perturbation Per Iteration')
        self.PerturbLoopCK.setChecked(True)
        row.addWidget(self.ResetLoopCK,2,0,1,4) 
        row.addWidget(self.PerturbLoopCK,3,0,1,4) 
        
        self.CalcRingsCK = QtGui.QCheckBox('Calculate Rings')
        self.CalcRingsCK.setChecked(True)
        row.addWidget(self.CalcRingsCK,4,0,1,4) 
        
    
    def setup_minimisation_widgets(self):        
        self.DualMinWidgetsHolder = BaseWidget(group=True,title="Dual Lattice Optimisation Options",
                                                        show=True,align=QtCore.Qt.AlignTop)

        self.dual_lattice_min_options = minimiserinputoptions.DualLatticeMinimisationOptions()
        self.DualMinWidgetsHolder.addWidget(self.dual_lattice_min_options)
        self.ButtonsHolder.addWidget(self.DualMinWidgetsHolder)
        self.ButtonsHolder.addSeparator(dummy=1)
        
        self.CarbonMinWidgetsHolder = BaseWidget(group=True,title="Carbon Lattice Optimisation Options",
                                                        show=True,align=QtCore.Qt.AlignTop)
        
        self.ButtonsHolder.addWidget(self.CarbonMinWidgetsHolder)
        self.carbon_lattice_min_options = minimiserinputoptions.CarbonLatticeMinimisationOptions()
        self.CarbonMinWidgetsHolder.addWidget(self.carbon_lattice_min_options)
        
    
    def setup_nanotube_widgets(self):
        
        self.nanotube_widgets_holder = BaseWidget(group=True,title="Input Options",
                                                        show=True,align=QtCore.Qt.AlignTop)
        self.NanotubeWidgets.append(self.nanotube_widgets_holder)
        self.ButtonsHolder.addWidget(self.nanotube_widgets_holder)
        
        self.cappednanotube_inputwidgets = structureinputoptions.CappedNanotubeInputOptions()
        self.nanotube_widgets_holder.addWidget(self.cappednanotube_inputwidgets)
        
          
        
    def setup_fullerene_widgets(self):    
        self.FullereneWidgetsHolder = BaseWidget(group=True,title="Input Options",
                                                        show=True,align=QtCore.Qt.AlignTop)
        
        self.FullereneWidgetsHolder.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                                  QtGui.QSizePolicy.Preferred)

        self.FullereneWidgets.append(self.FullereneWidgetsHolder)
        self.ButtonsHolder.addWidget(self.FullereneWidgetsHolder)
        
        self.fullerene_input_widgets = structureinputoptions.FullereneInputOptions()
        self.FullereneWidgetsHolder.addWidget(self.fullerene_input_widgets)
 
     
    def GenTypeChanged(self):
        for widget in self.NanotubeWidgets:
                widget.hide()
        for widget in self.FullereneWidgets:
                widget.hide()       
        
                
        if(self.GenFullerenceRB.isChecked()==True):
            self.GenType= STRUCTURE_TYPES[FULLERENE]
            for widget in self.FullereneWidgets:
                widget.show()          
        else:
            self.GenType= STRUCTURE_TYPES[CAPPEDNANOTUBE]
            for widget in self.NanotubeWidgets:
                widget.show()
        
        #self.resize(self.sizeHint())     
        self.updateGeometry()
    def sizeHint(self):

        return QtCore.QSize(1100,500)     
        