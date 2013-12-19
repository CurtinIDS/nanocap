'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Aug 2 2013
Copyright Marc Robinson 2013
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

Basic Toolbar class, 
No Dual Lattice options

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
'''
from nanocap.core.globals import *
import os,sys,math,copy,random,time,threading,types
from nanocap.core.globals import QT
QtGui, QtCore = QT.QtGui, QT.QtCore

import numpy

from nanocap.core import globals
import nanocap.gui.forms as forms
import nanocap.core.processes as processes
from nanocap.core.util import *
from nanocap.gui.toolbar import toolbar,SpinBox,DoubleSpinBox,TableWidget,HolderWidget


class toolbarBasic(toolbar):    
    def __init__(self, Gui, MainWindow):
        toolbar.__init__(self, Gui,MainWindow)
        self.MainWindow = MainWindow
        self.Gui = Gui
        self.Processor = self.Gui.processor
        self.ThreadManager = self.Gui.threadManager
        self.VTKFrame = self.Gui.vtkframe
        self.ObjectActors = self.Gui.objectActors  
        self.Operations = self.Gui.operations
        self.config = self.Processor.config
        
        #for key,val in self.config.opts.items():

            #print key,val
        printl(self.config)
            
    def selected(self):
        self.config.opts["ShowTriangulation"] = False
        self.config.opts["ShowCapDualLatticePoints"] = False
        self.config.opts["ShowTubeDualLatticePoints"] = False
        self.config.opts["ShowCappedTubeDualLatticePoints"] = False
        self.config.opts["ShowFullereneDualLatticePoints"] = False
        self.config.opts["CalcSchlegel"] = True
        
            
    def draw(self):
        
        self.MainWidget = forms.GenericForm(self,doNotShrink=True,isGroup=False,show=True,isScrollView=True)
        self.containerLayout.addWidget(self.MainWidget)
        
        sep = self.MainWidget.addSeparator(dummy=True)
        
        row = self.MainWidget.newRow()
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
        row.addWidgets((self.GenFullerenceRB,self.GenNanotubeRB))
        row.show()   
        
        sep = self.MainWidget.addSeparator()
        
        self.setup_fullerene_widgets()
        self.setup_nanotube_widgets()
        self.setup_general_widgets()
    
        for widget in self.NanotubeWidgets:
            widget.hide()
#
    def ShowCarbonAtoms(self):
        if(self.config.opts["GenType"]=="Fullerene"):
            self.ShowFullereneCarbonAtoms()
        else:
            self.ShowCappedTubeCarbonAtoms()

    
    def setDualLatticeUseRandomSeed(self,val):
        if(self.config.opts["GenType"]=="Fullerene"):
            if(val==1):self.setFullereneDualLatticeUseRandomSeed(True)
            else:self.setFullereneDualLatticeUseRandomSeed(False)
        else:
            if(val==1):self.setNanotubeUseRandomSeed(True)    
            else:self.setNanotubeUseRandomSeed(False)
    
    def GenerateMinimisedCappedNanotube(self):
        self.config.opts["NanotubeChiralityU"] = None
        self.config.opts["EstimateCapPoints"]=False
        
        
        self.ResetNanotube()
        
        self.ResetNanotubeCapDualLatticePoints()
        
        self.Processor.minsearch.reset()
        self.MinimaSearch()
    
    def GenerateMinimisedFullerene(self):
        
        self.ResetFullereneDualLatticePoints()
        self.Processor.minsearch.reset()
        self.MinimaSearch()        
            
    def GenerateStructure(self):
        self.config.opts["BasinClimb"]=True
        self.GenFullerenceRB.setEnabled(False)
        self.GenNanotubeRB.setEnabled(False)
        
        
        if(self.CarbonMinimiseCombo.currentText()=="Unit Radius Topology"):
            self.config.opts["CarbonMinimise"]=False
        else:
            self.config.opts["CarbonMinimise"]=True
        
            
            
        
        if(self.config.opts["GenType"] == "Fullerene"):
            self.GenerateMinimisedFullerene()
        if(self.config.opts["GenType"] =="Nanotube"):
            self.GenerateMinimisedCappedNanotube()
                 
    def setup_general_widgets(self):
        
        sep = self.MainWidget.addSeparator()
        row = self.MainWidget.newGrid()
        
        lb = QtGui.QLabel("Seed")
        #lb.setFixedWidth(100) 
        self.DualLatticeSeedEntry = SpinBox()
        self.DualLatticeSeedEntry.setMaximum(9999999)
        #self.FullereneDualLatticeSeedEntry = self.DualLatticeSeedEntry
        
        #self.DualLatticeSeedEntry.setFixedWidth(60)     
        self.DualLatticeRandomSeedCB = QtGui.QCheckBox("random")
        self.DualLatticeRandomSeedCB.setChecked(True) 
        self.connect(self.DualLatticeRandomSeedCB, QtCore.SIGNAL('stateChanged(int)'), self.setDualLatticeUseRandomSeed) 
        #row.addWidgets((lb,self.FullereneDualLatticeSeedEntry,self.FullereneDualLatticeRandomSeedCB))        
        row.addWidget(lb,1,0,alignment=QtCore.Qt.AlignRight)
        row.addWidget(self.DualLatticeSeedEntry,1,1)       
        row.addWidget(self.DualLatticeRandomSeedCB,1,2)
        
        
        lb = QtGui.QLabel("N Structures")
        self.NStructures = SpinBox()
        self.NStructures.setValue(self.config.opts["NStructures"])
        self.NStructures.setFixedWidth(50)
        self.connect(self.NStructures, QtCore.SIGNAL('valueChanged(int)'), self.setNStructures)
        row.addWidget(lb,2,0,alignment=QtCore.Qt.AlignRight)
        row.addWidget(self.NStructures,2,1,alignment=QtCore.Qt.AlignLeft)
        
        
        self.CarbonMinimiseCombo= QtGui.QComboBox()
        self.CarbonMinimiseCombo.addItem("Unit Radius Topology")
        self.CarbonMinimiseCombo.addItem("Scaled Topology")
        self.CarbonMinimiseCombo.addItem("EDIP")
        self.CarbonMinimiseCombo.addItem("LAMMPS-AREBO")
        
        self.connect(self.CarbonMinimiseCombo, QtCore.SIGNAL('currentIndexChanged(int)'), self.setCarbonForceField)
         
        row.addWidget(QtGui.QLabel("Carbon Lattice"),3,0,alignment=QtCore.Qt.AlignRight) 
        row.addWidget(self.CarbonMinimiseCombo,3,1,alignment=QtCore.Qt.AlignLeft) 
        
        

        sep = self.MainWidget.addSeparator(dummy=False)
        row = self.MainWidget.newRow(self)
        row.RowLayout.setSpacing(5)
        self.StartMinSearchBT = QtGui.QPushButton('Generate')
        #self.connect(self.StartMinCarbonBT, QtCore.SIGNAL('clicked()'), self.MinimiseCarbonAtomsDirect)
        
        self.connect(self.StartMinSearchBT, QtCore.SIGNAL('clicked()'), self.GenerateStructure )
        
        self.StopMinSearchBT = QtGui.QPushButton('Stop')
        self.StopMinSearchBT.hide()
        self.connect(self.StopMinSearchBT, QtCore.SIGNAL('clicked()'), self.StopMinSearch)
        
        
        self.SearchProgressbar = QtGui.QProgressBar()
        self.SearchProgressbar.setMinimum(0)
        self.SearchProgressbar.setMaximum(self.config.opts["NStructures"])
        self.SearchProgressbar.setTextVisible(True)
        self.SearchProgressbar.hide()
        
        row.addWidgets((self.StartMinSearchBT,self.SearchProgressbar,self.StopMinSearchBT))
        #row = self.MainWidget.newRow(self)
        #row.addWidget(self.SearchProgressbar)
        
        lb = self.MainWidget.addHeader("Current Structures")
        
        row = self.MainWidget.newRow(self)
        self.ShowStructureTableBT = QtGui.QPushButton('Structures Table')
        self.connect(self.ShowStructureTableBT, QtCore.SIGNAL('clicked()'), self.showStructureWindow)
        row.addWidgets((self.ShowStructureTableBT,))
                
        lb = self.MainWidget.addHeader("Render Options")
        
        row = self.MainWidget.newRow(self)
        self.CalcRenTable = TableWidget(310,300)
        #self.CalcRenTable.show()
        self.CalcRenTable.verticalHeader().hide()
        
        self.CalcRenTable.setupHeaders(["Option","Show","Label","Rad","Col"],
                                       [100,40,40,80,50])

        
        row.addWidget(self.CalcRenTable)
        
        row = self.MainWidget.newGrid()
        row.setVerticalSpacing(10) 
        
        self.ShowFullereneCarbonAtomsCk = QtGui.QCheckBox()
        self.ShowFullereneCarbonAtomsCk.setChecked(True)
        self.ShowCappedTubeCarbonAtomsCk = QtGui.QCheckBox()
        self.ShowCappedTubeCarbonAtomsCk.setChecked(True)
        self.ShowCarbonBondsCk = QtGui.QCheckBox()
        self.ShowCarbonBondsCk.setChecked(True)
        self.ShowBondingPolygonsCk = QtGui.QCheckBox()
        self.ShowBondingPolygonsCk.setChecked(True)
        self.ShowScreenInfoCk = QtGui.QCheckBox()        
        self.ShowScreenInfoCk.setChecked(True)
        self.connect(self.ShowScreenInfoCk, QtCore.SIGNAL('clicked()'), self.ShowScreenInfo)
        self.connect(self.ShowFullereneCarbonAtomsCk, QtCore.SIGNAL('clicked()'), self.ShowFullereneCarbonAtoms)
        self.connect(self.ShowCappedTubeCarbonAtomsCk, QtCore.SIGNAL('clicked()'), self.ShowCappedTubeCarbonAtoms)
        self.connect(self.ShowCarbonBondsCk, QtCore.SIGNAL('clicked()'), self.ShowCarbonBonds)
        self.connect(self.ShowBondingPolygonsCk, QtCore.SIGNAL('clicked()'), self.ShowCarbonRings)

        self.NanotubeWidgets.append(self.ShowCappedTubeCarbonAtomsCk)
        self.FullereneWidgets.append(self.ShowFullereneCarbonAtomsCk)
        #row.addWidget(self.ShowCarbonAtomsCk,0,0,alignment=QtCore.Qt.AlignLeft)
        #row.addWidget(self.ShowCarbonBondsCk,1,0,alignment=QtCore.Qt.AlignLeft)
        #row.addWidget(self.ShowBondingPolygonsCk,2,0,alignment=QtCore.Qt.AlignLeft)
        #row.addWidget(self.ToggleScreenInfoCB,3,0,alignment=QtCore.Qt.AlignLeft)
         
        self.CarbonAtomsRadSB = DoubleSpinBox()
        self.CarbonAtomsRadSB.setValue(0.25)
        self.CarbonAtomsRadSB.setSingleStep(0.01)
        self.CarbonAtomsRadSB.setFixedWidth(80)
        self.connect(self.CarbonAtomsRadSB, QtCore.SIGNAL('valueChanged(  double )'), self.setCarbonAtomRad)
        
        rgb = numpy.array(self.config.opts["FullereneCarbonAtomColourRGB"])*255
        self.CarbonAtomsColour = QtGui.QColor(rgb[0],rgb[1],rgb[2])      
        self.CarbonAtomsColourBT = QtGui.QPushButton("")
        self.CarbonAtomsColourBT.setFixedWidth(25)
        self.CarbonAtomsColourBT.setFixedHeight(20)
        self.CarbonAtomsColourBT.setStyleSheet("QPushButton { background-color: %s ; border-radius: 5px; padding: 6px}" % self.CarbonAtomsColour.name())
        self.connect(self.CarbonAtomsColourBT, QtCore.SIGNAL('clicked()'), self.changeCarbonAtomsColour)
        
        #row.addWidget(QtGui.QLabel("Rad:"),0,1,alignment=QtCore.Qt.AlignRight)
        #row.addWidget(self.CarbonAtomsRadSB,0,2,alignment=QtCore.Qt.AlignLeft)
        #row.addWidget(QtGui.QLabel("Col: "),0,3,alignment=QtCore.Qt.AlignRight)
        #row.addWidget(self.CarbonAtomsColourBT,0,4,alignment=QtCore.Qt.AlignCenter)
        
        self.bondThicknessEntry = DoubleSpinBox()
        self.bondThicknessEntry.setMinimum(0.0001)
        self.bondThicknessEntry.setValue(0.08)
        self.bondThicknessEntry.setDecimals(4)
        self.bondThicknessEntry.setSingleStep(0.001)
        self.bondThicknessEntry.setFixedWidth(80)
        self.connect(self.bondThicknessEntry, QtCore.SIGNAL('valueChanged(  double )'), self.BondThicknessChanged)
        #row.addWidget(QtGui.QLabel("Width"),1,1,alignment=QtCore.Qt.AlignRight)
        #row.addWidget(self.bondThicknessEntry,1,2,alignment=QtCore.Qt.AlignLeft)
    
        self.ShowCarbonAtomsLabelsCk = QtGui.QCheckBox()
        self.connect(self.ShowCarbonAtomsLabelsCk, QtCore.SIGNAL('clicked()'), self.ToggleCarbonLabels)
    
        self.ShowCarbonAtomsBoxCk = QtGui.QCheckBox()
        self.connect(self.ShowCarbonAtomsBoxCk, QtCore.SIGNAL('clicked()'), self.ToggleCarbonBoxes)
        
        self.CalcRenTable.insertRow(0)
        lab = QtGui.QTableWidgetItem("Atoms")
        self.CalcRenTable.setItem(0,0,lab)
        self.CalcRenTable.setCellWidget(0,1,HolderWidget((self.ShowCappedTubeCarbonAtomsCk,self.ShowFullereneCarbonAtomsCk)))
        self.CalcRenTable.setCellWidget(0,2,HolderWidget(self.ShowCarbonAtomsLabelsCk))
        self.CalcRenTable.setCellWidget(0,3,HolderWidget(self.CarbonAtomsRadSB))
        self.CalcRenTable.setCellWidget(0,4,HolderWidget(self.CarbonAtomsColourBT))
    
        self.CalcRenTable.insertRow(1)
        lab = QtGui.QTableWidgetItem("Bonds")
        self.CalcRenTable.setItem(1,0,lab)
        self.CalcRenTable.setCellWidget(1,1,HolderWidget(self.ShowCarbonBondsCk))
        self.CalcRenTable.setCellWidget(1,3,HolderWidget(self.bondThicknessEntry))

        
        self.CalcRenTable.insertRow(2)
        lab = QtGui.QTableWidgetItem("Rings")
        self.CalcRenTable.setItem(2,0,lab)
        self.CalcRenTable.setCellWidget(2,1,HolderWidget(self.ShowBondingPolygonsCk))

        
        self.CalcRenTable.insertRow(3)
        lab = QtGui.QTableWidgetItem("Screen Info")
        self.CalcRenTable.setItem(3,0,lab)
        self.CalcRenTable.setCellWidget(3,1,HolderWidget(self.ShowScreenInfoCk))
        
        
        self.CalcRenTable.insertRow(4)
        lab = QtGui.QTableWidgetItem("Bounding Box")
        self.CalcRenTable.setItem(4,0,lab)
        self.CalcRenTable.setCellWidget(4,1,HolderWidget(self.ShowCarbonAtomsBoxCk))
        
        lb = self.MainWidget.addHeader("Output Current Structure")
        
        #sep = self.SubOptionsWindows["OUTPUT"].addSeparator(dummy=True)
        
        row = self.MainWidget.newRow()
        self.OutputDirEntry = QtGui.QLineEdit()
        row.addWidgets((QtGui.QLabel("Directory:"),self.OutputDirEntry))
        
        row = self.MainWidget.newRow()
        self.BrowseToFolderBT = QtGui.QPushButton('Browse')
        self.connect(self.BrowseToFolderBT, QtCore.SIGNAL('clicked()'), self.browseToFolder)
        row.addWidgets((self.BrowseToFolderBT,))

        self.SaveLatticeBT = QtGui.QPushButton('Save')
        self.connect(self.SaveLatticeBT, QtCore.SIGNAL('clicked()'), self.saveCurrentStructure)
        row.addWidgets((self.SaveLatticeBT,))
        
    
    def ToggleCarbonBoxes(self):
        if(self.ShowCarbonAtomsBoxCk.isChecked()):
            
            if(self.config.opts["GenType"]=="Fullerene"):self.config.opts["ShowFullereneCarbonAtomsBox"] = True
            if(self.config.opts["GenType"]=="Nanotube"):self.config.opts["ShowCappedTubeCarbonAtomsBox"] = True
        else:
            if(self.config.opts["GenType"]=="Fullerene"):self.config.opts["ShowFullereneCarbonAtomsBox"] = False
            if(self.config.opts["GenType"]=="Nanotube"):self.config.opts["ShowCappedTubeCarbonAtomsBox"] = False    
        self.Operations.ToggleBoundingBoxes() 
        
    def ToggleCarbonLabels(self):
        if(self.ShowCarbonAtomsLabelsCk.isChecked()):
            
            if(self.config.opts["GenType"]=="Fullerene"):self.config.opts["ShowFullereneCarbonAtomsLabels"] = True
            if(self.config.opts["GenType"]=="Nanotube"):self.config.opts["ShowCappedTubeCarbonAtomsLabels"] = True
        else:
            if(self.config.opts["GenType"]=="Fullerene"):self.config.opts["ShowFullereneCarbonAtomsLabels"] = False
            if(self.config.opts["GenType"]=="Nanotube"):self.config.opts["ShowCappedTubeCarbonAtomsLabels"] = False    

        
        self.Operations.ToggleLabels() 
    
    
#    def setCarbonForceField(self,val):
#        
#        if(self.CarbonMinimiseCombo.currentText()=="EDIP"):
#            self.config.opts["CarbonForceField"]="EDIP"  
#        if(self.CarbonMinimiseCombo.currentText()=="Scaled Topology"):
#            self.config.opts["CarbonForceField"]="RSSBond"  
#        if(self.CarbonMinimiseCombo.currentText()=="LAMMPS-AREBO"):
#            self.config.opts["CarbonForceField"]="LAMMPS-AREBO"     
#        
#        printl("set CarbonForceField",self.config.opts["CarbonForceField"])
    
    def setCarbonAtomRad(self,val):
        if(self.config.opts["GenType"]=="Nanotube"):
            try:self.Operations.setCappedTubeCarbonAtomRad(val)
            except:pass
            try:self.Operations.setTubeCarbonAtomRad(val)
            except:pass
        if(self.config.opts["GenType"]=="Fullerene"):
            self.Operations.setFullereneCarbonAtomRad(val)
            
    def changeCarbonAtomsColour(self):
        col = QtGui.QColorDialog().getColor(self.CarbonAtomsColour)
        if col.isValid():
            self.CarbonAtomsColour = col
            r=0
            g=0
            b=0
            r= "%0.2f" % (float(self.CarbonAtomsColour.red())/255.0)
            g= "%0.2f" % (float(self.CarbonAtomsColour.green())/255.0)
            b= "%0.2f" % (float(self.CarbonAtomsColour.blue())/255.0)
            self.CarbonAtomsColourRGB = (float(r),float(g),float(b))
            #print "Setting",self.TubeThomsonPointColour.name(),self.TubeThomsonPointColourRGB
            self.CarbonAtomsColourBT.setStyleSheet("QPushButton { background-color: %s ; border-radius: 5px ; border-radius: 5px }" % self.CarbonAtomsColour.name())
            
        if(self.config.opts["GenType"]=="Nanotube"):
            self.config.opts["CappedTubeCarbonAtomColourRGB"] = self.CarbonAtomsColourRGB
            self.config.opts["TubeCarbonAtomColourRGB"] = self.CarbonAtomsColourRGB
            self.Processor.nanotube.cappedTubeCarbonAtoms.col=self.CarbonAtomsColourRGB
            self.Processor.nanotube.cappedTubeCarbonAtoms.update() 
            try:
                self.Processor.nanotube.cappedTubeCarbonAtoms.update() 
            except:
                pass
            
        if(self.config.opts["GenType"]=="Fullerene"):        
            self.config.opts["FullereneCarbonAtomColourRGB"] = self.CarbonAtomsColourRGB
            self.Processor.fullerene.carbonAtoms.col=self.CarbonAtomsColourRGB
            self.Processor.fullerene.carbonAtoms.update() 
            
        self.Gui.vtkframe.refreshWindow()

    
    def setup_nanotube_widgets(self):     
        
        self.NanotubeTubeThomsonPointsEntry = SpinBox()
        self.NanotubeCapThomsonPointsEntry = SpinBox()
        self.CappedNanotubeThomsonPointsEntry = SpinBox()
        
        #row = self.MainWidget.newGrid()
        row = self.MainWidget.newRow()
        #row.addWidget(QtGui.QLabel("Nanotube"),0,0,alignment=QtCore.Qt.AlignRight)
        lb = QtGui.QLabel("M")
        lb.setFixedWidth(20)
        self.NanotubeMEntry = SpinBox()
        self.NanotubeMEntry.setValue(5)
        self.NanotubeMEntry.setFixedWidth(60)
        lb2 = QtGui.QLabel("N")
        lb2.setFixedWidth(20)
        self.NanotubeNEntry = SpinBox()
        self.NanotubeNEntry.setValue(5)
        self.NanotubeNEntry.setFixedWidth(60)
        lb3 = QtGui.QLabel("U")
        lb3.setFixedWidth(20)
        self.NanotubeUEntry = SpinBox()
        self.NanotubeUEntry.setValue(5)
        self.NanotubeUEntry.setFixedWidth(60)
#        row.addWidget(lb2,0,1,alignment=QtCore.Qt.AlignRight)
#        row.addWidget(self.NanotubeNEntry,0,2,alignment=QtCore.Qt.AlignLeft)
#        row.addWidget(lb,0,3,alignment=QtCore.Qt.AlignLeft)
#        row.addWidget(self.NanotubeMEntry,0,4,alignment=QtCore.Qt.AlignLeft)
        row.addWidgets((lb2,self.NanotubeNEntry,lb,self.NanotubeMEntry))
#        row.addWidget(lb3,0,5,alignment=QtCore.Qt.AlignRight)
#        row.addWidget(self.NanotubeUEntry,0,6,alignment=QtCore.Qt.AlignLeft)
        self.connect(self.NanotubeMEntry, QtCore.SIGNAL('valueChanged(int)'), self.setNanotubeChirality)
        self.connect(self.NanotubeNEntry, QtCore.SIGNAL('valueChanged(int)'), self.setNanotubeChirality)
        #self.connect(self.NanotubeUEntry, QtCore.SIGNAL('valueChanged(int)'), self.setNanotubeChirality)
        
        self.NanotubeWidgets.append(lb)
        self.NanotubeWidgets.append(lb2)
        #self.NanotubeWidgets.append(lb3)
        self.NanotubeWidgets.append(self.NanotubeNEntry)
        self.NanotubeWidgets.append(self.NanotubeMEntry)
        #self.NanotubeWidgets.append(self.NanotubeUEntry)
        
        

        row = self.MainWidget.newRow()
        self.EstimateCapAtomsBT = QtGui.QPushButton("Initialise")
        self.connect(self.EstimateCapAtomsBT, QtCore.SIGNAL('clicked()'), self.InitialiseNanotube)
        row.addWidget(self.EstimateCapAtomsBT)
        self.NanotubeWidgets.append(self.EstimateCapAtomsBT)
        
        row = self.MainWidget.newGrid()
        lb = QtGui.QLabel("Tube Carbon Atoms")
        #lb.setFixedWidth(140)
        self.NanotubeTubeCarbonAtomEntry = SpinBox()
        self.NanotubeTubeCarbonAtomEntry.setMaximum(9999999)
        self.NanotubeTubeCarbonAtomEntry.setValue(self.config.opts["NTubeCarbonAtoms"])
        self.NanotubeTubeCarbonAtomEntry.setReadOnly(True)
        self.NanotubeTubeCarbonAtomEntry.setSingleStep(2)
        #row.addWidgets((lb,self.FullereneCarbonAtomsEntry))
        row.addWidget(lb,0,0,alignment=QtCore.Qt.AlignRight)
        row.addWidget(self.NanotubeTubeCarbonAtomEntry,0,1,alignment=QtCore.Qt.AlignLeft)
        self.NanotubeWidgets.append(lb)
        self.NanotubeWidgets.append(self.NanotubeTubeCarbonAtomEntry)
        
        
        self.NanotubeCapCarbonAtomEntry = SpinBox()      
        self.connect(self.NanotubeCapThomsonPointsEntry, QtCore.SIGNAL('valueChanged(  int )'), self.setNanotubeCapThomsonPoints)
        
        row = self.MainWidget.newGrid()
        lb = QtGui.QLabel("Cap Carbon Atoms")
        #lb.setFixedWidth(140)
        self.NanotubeCapCarbonAtomEntry = SpinBox()
        self.NanotubeCapCarbonAtomEntry.setMaximum(9999999)
        self.NanotubeCapCarbonAtomEntry.setValue(self.config.opts["NCapCarbonAtoms"])
        #self.FullereneCarbonAtomsEntry.setFixedWidth(60)
        self.NanotubeCapCarbonAtomEntry.setSingleStep(2)
        #row.addWidgets((lb,self.FullereneCarbonAtomsEntry))
        row.addWidget(lb,0,0,alignment=QtCore.Qt.AlignRight)
        row.addWidget(self.NanotubeCapCarbonAtomEntry,0,1,alignment=QtCore.Qt.AlignLeft)
        self.connect(self.NanotubeCapCarbonAtomEntry, QtCore.SIGNAL('valueChanged(  int )'), self.setNanotubeCapCarbonAtoms)
        

        
        self.NanotubeWidgets.append(lb)
        self.NanotubeWidgets.append(self.NanotubeCapCarbonAtomEntry)
        
        row = self.MainWidget.newGrid()
        lb = QtGui.QLabel("Total Carbon Atoms")
        #lb.setFixedWidth(140)
        self.CappedNanotubeCarbonAtomEntry = SpinBox()
        self.CappedNanotubeCarbonAtomEntry.setMaximum(9999999)
        self.CappedNanotubeCarbonAtomEntry.setValue(self.config.opts["NCappedTubeCarbonAtoms"])
        #self.FullereneCarbonAtomsEntry.setFixedWidth(60)
        self.CappedNanotubeCarbonAtomEntry.setSingleStep(2)
        self.CappedNanotubeCarbonAtomEntry.setReadOnly(True)
        row.addWidget(lb,0,0,alignment=QtCore.Qt.AlignRight)
        row.addWidget(self.CappedNanotubeCarbonAtomEntry,0,1,alignment=QtCore.Qt.AlignLeft)
        
        self.NanotubeWidgets.append(lb)
        self.NanotubeWidgets.append(self.CappedNanotubeCarbonAtomEntry)
        
        row = self.MainWidget.newRow()
        self.NanotubeLengthEntry = DoubleSpinBox()
        self.NanotubeLengthEntry.setValue(self.config.opts["NanotubeLength"])
        lb = QtGui.QLabel("Length (Angs)")
        self.connect(self.NanotubeLengthEntry, QtCore.SIGNAL('valueChanged(double)'), self.setNanotubeLength)
        
        self.NanotubeLengthSlider = QtGui.QSlider()
        self.NanotubeLengthSlider.setOrientation(QtCore.Qt.Horizontal)
        self.NanotubeLengthSlider.setMinimum(0)#0.0
        self.NanotubeLengthSlider.setMaximum(10000)#10.0 (divide by 100)
        self.NanotubeLengthSlider.setValue(self.config.opts["NanotubeLength"]*100)
        self.NanotubeLengthSlider.setTickInterval(1)
        
        self.connect(self.NanotubeLengthSlider, QtCore.SIGNAL('sliderMoved(int)'), self.NanotubeLengthSliderChanged)
        self.connect(self.NanotubeLengthSlider, QtCore.SIGNAL('valueChanged(int)'), self.NanotubeLengthSliderChanged)
        self.connect(self.NanotubeLengthSlider, QtCore.SIGNAL('sliderPressed()'), self.NanotubeLengthSliderPressed)
        self.connect(self.NanotubeLengthSlider, QtCore.SIGNAL('sliderReleased()'), self.NanotubeLengthSliderReleased)
        
        row.addWidgets((lb,self.NanotubeLengthSlider,self.NanotubeLengthEntry))
        self.NanotubeWidgets.append(lb)
        self.NanotubeWidgets.append(self.NanotubeLengthEntry)
        self.NanotubeWidgets.append(self.NanotubeLengthSlider)
        
        
    def InitialiseNanotube(self):
        self.config.opts["ShowTubeDualLatticePoints"]=False
#        self.Processor.resetNanotube(self.config.opts["NanotubeChiralityN,
#                                     self.config.opts["NanotubeChiralityM,
#                                     self.config.opts["NanotubeChiralityU)
        
        self.config.opts["EstimateCapPoints"] = True
        
        self.Processor.estimateCapPoints(self.config.opts["NanotubeChiralityN"],
                                         self.config.opts["NanotubeChiralityM"])
        
        
        
        self.NanotubeCapThomsonPointsEntry.setValue(self.config.opts["NCapDualLatticePoints"])
        self.NanotubeCapCarbonAtomEntry.setValue(self.config.opts["NCapCarbonAtoms"])
        
        self.Processor.setMinimumNanotubeLength(self.config.opts["NanotubeChiralityN"],
                                                self.config.opts["NanotubeChiralityM"])
        
        self.NanotubeLengthEntry.setValue(self.config.opts["NanotubeLength"])
        self.setNanotubeLength(self.config.opts["NanotubeLength"])
        
        #self.ResetNanotube()
        
            
    def setup_fullerene_widgets(self):    
        row = self.MainWidget.newGrid()
        lb = QtGui.QLabel("Carbon Atoms")
        #lb.setFixedWidth(140)
        self.FullereneCarbonAtomsEntry = SpinBox()
        self.FullereneCarbonAtomsEntry.setMaximum(9999999)
        self.FullereneCarbonAtomsEntry.setValue(self.config.opts["NFullereneCarbonAtoms"])
        #self.FullereneCarbonAtomsEntry.setFixedWidth(60)
        self.FullereneCarbonAtomsEntry.setSingleStep(2)
        #row.addWidgets((lb,self.FullereneCarbonAtomsEntry))
        row.addWidget(lb,0,0,alignment=QtCore.Qt.AlignRight)
        row.addWidget(self.FullereneCarbonAtomsEntry,0,1,alignment=QtCore.Qt.AlignLeft)
        
        self.FullereneWidgets.append(lb)
        self.FullereneWidgets.append(self.FullereneCarbonAtomsEntry)
        
        self.connect(self.FullereneCarbonAtomsEntry, QtCore.SIGNAL('valueChanged(int)'), self.setFullereneCarbonAtoms)
        
        self.FullereneDualLatticePointsEntry = SpinBox()
        self.FullereneDualLatticePointsEntry.setMaximum(9999999)
        self.FullereneDualLatticePointsEntry.setValue(32)
        self.FullereneDualLatticePointsEntry.setFixedWidth(60)        
       
#    def ShowCappedTubeCarbonAtoms(self):
#        if(self.ShowCarbonAtomsCk.isChecked()==True):
#            #self.CalcCappedTubeCarbonAtomsCk.setChecked(True)
#            self.Processor.addCappedTubeCarbonAtoms()
#        else:
#            self.Processor.removeCappedTubeCarbonAtoms()    
#    
#    def ShowFullereneCarbonAtoms(self):
#        if(self.ShowCarbonAtomsCk.isChecked()):
#            self.config.opts["ShowFullereneCarbonAtoms=True
#            self.Processor.addFullereneCarbonAtoms()
#
#        else:
#            self.config.opts["ShowFullereneCarbonAtoms=False
#            self.Processor.removeFullereneCarbonAtoms()
#                
#    def ShowCarbonBonds(self):
#        
#        if(self.ShowCarbonBondsCk.isChecked()):
#            self.config.opts["ShowCarbonBonds=True
#            self.Processor.addCarbonBonds()
#        else:
#            self.config.opts["ShowCarbonBonds=False
#            self.Processor.removeCarbonBonds()
           
#    def ShowBondingPolygons(self):
#        if(self.ShowBondingPolygonsCk.isChecked()):
#            self.config.opts["ShowCarbonRings=True
#            self.Processor.addBondingPolygons()
#        else:
#            self.config.opts["ShowCarbonRings=False
#            self.Processor.removeBondingPolygons()       
            

            
#    def StopGenerateCappedNanotube(self):
#        self.GenFullerenceRB.setEnabled(True)
#        self.GenNanotubeRB.setEnabled(True)
#        self.Processor.minimiser.stopmin=1
#        self.Processor.stopgen=1
#        self.StartGenerateCappedNanotubeBT.show()
#        #printl("StopGenerateFullereneBT hide")
#        self.StopGenerateCappedNanotubeBT.hide()
#        #self.VTKFrame.VTKRenderer.ResetCamera() 
#        self.VTKFrame.refreshWindow()
#
#
#        
#        
#    def StopGenerateFullerene(self):
#        self.GenFullerenceRB.setEnabled(True)
#        self.GenNanotubeRB.setEnabled(True)
#        
#        
#        self.Processor.minimiser.stopmin=1
#        self.Processor.stopgen=1
#        self.StartGenerateFullereneBT.show()
#        #printl("StopGenerateFullereneBT hide")
#        self.StopGenerateFullereneBT.hide()
#        #self.VTKFrame.VTKRenderer.ResetCamera() 
#        self.VTKFrame.refreshWindow()        

#    def setupTableWidgets(self,N):
#        self.ShowFButtons = []
#        self.ShowCButtons = []
#        self.SaveButtons = []
#        for i in range(0,N):
#            
#            Fcheck = ShowButton()
#            Ccheck = ShowButton()
#            button = SaveButton()
#            #button.setFixedWidth(25)
#            #button.setCheckable(True)
#            #button.setStyleSheet("QPushButton { background-color: grey; border-radius: 5px }")
#            self.SaveButtons.append(button)
#            self.ShowFButtons.append(Fcheck)
#            self.ShowCButtons.append(Ccheck)


    
    
    
    
    
    
        