'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Aug 2 2013
Copyright Marc Robinson 2013
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

Advanced Toolbar class, 

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
'''
from nanocap.core.globals import *
import os,sys,math,copy,random,time,types
from nanocap.core.globals import QT
QtGui, QtCore = QT.QtGui, QT.QtCore

import numpy

import nanocap.gui.forms as forms
import nanocap.core.processes as processes
import nanocap.gui.toolbarbasic as toolbarbasic
from nanocap.gui.toolbar import toolbar,SpinBox,DoubleSpinBox,TableWidget,HolderWidget
from nanocap.core.util import *

class toolbarAdvanced(toolbar):    
    def __init__(self, Gui,MainWindow):
        toolbar.__init__(self, Gui,MainWindow,Advanced=True)
        self.MainWindow = MainWindow
        self.Gui = Gui
        self.Processor = self.Gui.processor
        self.config = self.Processor.config
        self.ThreadManager = self.Gui.threadManager
        self.VTKFrame = self.Gui.vtkframe
        self.ObjectActors = self.Gui.objectActors
        self.Operations = self.Gui.operations

        self.show()
    
    def selected(self):
        if(self.CalcTriCk.isChecked()):
            self.config.opts["CalcTriangulation"]=True
            self.config.opts["EstimateCapPoints"]=True

    def draw(self):
        printl("drawing")
        self.MainList = QtGui.QListWidget()
        self.MainList.setStyleSheet("font: "+str(font_size+2)+"pt")
        
        self.MainList.setFixedHeight(100)
        
        self.GenerateItem = QtGui.QListWidgetItem("Initialisation")
        self.CalcRenderItem = QtGui.QListWidgetItem("Calculations/Rendering")
        self.MinItem = QtGui.QListWidgetItem("Minimisation")
        self.OutputItem = QtGui.QListWidgetItem("Output")
        self.MainList.addItem(self.GenerateItem)
        self.MainList.addItem(self.CalcRenderItem)
        self.MainList.addItem(self.MinItem)
        self.MainList.addItem(self.OutputItem)
        self.GenerateItem.setData(QtCore.Qt.UserRole,"GEN")
        self.CalcRenderItem.setData(QtCore.Qt.UserRole,"CALCREN")
        self.MinItem.setData(QtCore.Qt.UserRole,"MIN")
        self.OutputItem.setData(QtCore.Qt.UserRole,"OUTPUT")

        self.connect(self.MainList, QtCore.SIGNAL('itemClicked(QListWidgetItem*)'), self.ItemClicked) 
        
        self.containerLayout.addWidget(self.MainList)
        
        self.OptionsWindow = forms.GenericForm(self,isScrollView=True,isGroup=False,show=True)
        #self.OptionsWindow.setMinimumHeight(600)
        #self.OptionsWindow.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

        #self.OptionsLayout = QtGui.QVBoxLayout(self.OptionsWindow)
        #self.OptionsLayout.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        self.OptionsWindow.layout().setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        
        self.containerLayout.addWidget(self.OptionsWindow)
        #self.OptionsLayout.setContentsMargins(0, 0, 0, 0)
        #self.OptionsLayout.setSpacing(0)
        #self.OptionsWindow.setStyleSheet("background-color: red")
        
        self.SubOptionsWindows = {}
        self.SubOptionsWindows["GEN"] = forms.GenericForm(self,doNotShrink=True,isGroup=False,show=False,isScrollView=True)
        self.SubOptionsWindows["CALCREN"] = forms.GenericForm(self,doNotShrink=True,isGroup=False,show=False,isScrollView=True)
        self.SubOptionsWindows["MIN"] = forms.GenericForm(self,doNotShrink=True,isGroup=False,show=False,isScrollView=True)
        self.SubOptionsWindows["OUTPUT"] = forms.GenericForm(self,doNotShrink=True,isGroup=False,show=False,isScrollView=True)

        for v in self.SubOptionsWindows.values():
            self.OptionsWindow.newRow(align="HTCenter").addWidget(v)
        
        #row = forms.FormRow()
        #self.SubOptionsWindows["GEN"].layout().addWidget(row)
        row = self.SubOptionsWindows["GEN"].newRow()
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
    
        self.setupFullereneWidgets()
    
        self.setupNanotubeWidgets()

        self.setupCalcRenderWidgets()
        
        self.setupMinWidgets()
        
        self.setupOutputWidgets()
        
        for widget in self.NanotubeWidgets:widget.hide()
    
    def ItemClicked(self,item):
        #Type = str(item.data(QtCore.Qt.UserRole).toString())
        Type = str(item.data(QtCore.Qt.UserRole))
        for i in self.SubOptionsWindows.values():
            i.hide()
            
        self.SubOptionsWindows[Type].show()
        print item.data(QtCore.Qt.UserRole)#.toString()
        
    def setupMinWidgets(self):
        
        #sep = self.SubOptionsWindows["MIN"].addSeparator(dummy=True)
        #self.FullereneWidgets.append(sep)
        
        lb = self.SubOptionsWindows["MIN"].addHeader("Force Modifications")
        
        #sep = self.SubOptionsWindows["MIN"].addSeparator(dummy=True)
        self.NanotubeWidgets.append(lb)
        #self.NanotubeWidgets.append(sep)
        
        row = self.SubOptionsWindows["MIN"].newRow(self)
        lb = QtGui.QLabel("Force Z cutoff ")
        lb.setFixedWidth(80)
        
        self.NanotubeForceCutoffSlider = QtGui.QSlider()
        self.NanotubeForceCutoffSlider.setOrientation(QtCore.Qt.Horizontal)
        self.NanotubeForceCutoffSlider.setMinimum(0)#0.0
        self.NanotubeForceCutoffSlider.setMaximum(1000)#10.0 (divide by 100)
        self.NanotubeForceCutoffSlider.setValue(200)
        self.NanotubeForceCutoffSlider.setTickInterval(10)#0.1
        #self.NanotubeCutoffSlider.setMinimumSize(120, 80)
        
        #self.TimeStepSlider.setTickPosition(QtGui.QSlider.TicksBelow)
        self.connect(self.NanotubeForceCutoffSlider, QtCore.SIGNAL('sliderMoved(int)'), self.NanotubeForceSliderChanged)
        self.connect(self.NanotubeForceCutoffSlider, QtCore.SIGNAL('valueChanged(int)'), self.NanotubeForceSliderChanged)
        self.connect(self.NanotubeForceCutoffSlider, QtCore.SIGNAL('sliderPressed()'), self.NanotubeForceSliderPressed)
        self.connect(self.NanotubeForceCutoffSlider, QtCore.SIGNAL('sliderReleased()'), self.NanotubeForceSliderReleased)
        
        self.NanotubeForceCutoff = DoubleSpinBox()
        self.NanotubeForceCutoff.setSingleStep(0.05)
        self.NanotubeForceCutoff.setValue(2.0)
        self.NanotubeForceCutoff.setFixedWidth(60)
        
        self.autoCutoffCB = QtGui.QCheckBox("Auto")
        self.autoCutoffCB.setChecked(self.config.opts["AutoNanotubeZCutoff"])
        row.addWidgets((lb,self.NanotubeForceCutoffSlider,self.NanotubeForceCutoff,self.autoCutoffCB))
        self.NanotubeWidgets.append(row)
        self.connect(self.autoCutoffCB, QtCore.SIGNAL('clicked(  )'), self.setAutoNanotubeZCutoff)
        
        self.connect(self.NanotubeForceCutoff, QtCore.SIGNAL('valueChanged(  double )'), self.NanotubeForceCutoffChanged)

        row = self.SubOptionsWindows["MIN"].newRow(self)
        self.NanotubeDampingCB = QtGui.QCheckBox("Damping")
        self.NanotubeDampingCB.setChecked(self.config.opts["NanotubeDamping"])
        #row.addWidgets((self.NanotubeDampingCB,))
        self.NanotubeWidgets.append(row)
        self.connect(self.NanotubeDampingCB, QtCore.SIGNAL('clicked()'), self.ToggleNanotubeDamping)
        
        row = self.SubOptionsWindows["MIN"].newRow(self)
        lb = QtGui.QLabel("Damping cutoff ")
        lb.setFixedWidth(100)
        self.NanotubeDampingCutoff = DoubleSpinBox()
        self.NanotubeDampingCutoff.setValue(1.0)
        self.NanotubeDampingCutoff.setFixedWidth(100)
        #row.addWidgets((lb,self.NanotubeDampingCutoff))
        self.NanotubeWidgets.append(row)
        self.connect(self.NanotubeDampingCutoff, QtCore.SIGNAL('valueChanged(  double )'), self.NanotubeDampingCutoffChanged)
        
        row = self.SubOptionsWindows["MIN"].newRow(self)
        lb = QtGui.QLabel("Damping constant ")
        lb.setFixedWidth(100)
        self.NanotubeDampingConstant = DoubleSpinBox()
        self.NanotubeDampingConstant.setValue(10.0)
        self.NanotubeDampingConstant.setFixedWidth(100)
        #row.addWidgets((lb,self.NanotubeDampingConstant))
        self.NanotubeWidgets.append(row)
        self.connect(self.NanotubeDampingConstant, QtCore.SIGNAL('valueChanged(  double )'), self.NanotubeDampingConstantChanged)
        
        #sep = self.SubOptionsWindows["MIN"].addSeparator()
        #self.NanotubeWidgets.append(sep)
        
        lb = self.SubOptionsWindows["MIN"].addHeader("Dual Lattice Minimisation Options")
        #sep = self.SubOptionsWindows["MIN"].addSeparator(dummy=True)
        
        row = self.SubOptionsWindows["MIN"].newRow(self)
        self.MinTypeCB = QtGui.QComboBox()
        self.MinTypeCB.addItem("SD")
        self.MinTypeCB.addItem("LBFGS")
        #self.MinTypeCB.addItem("LBFGS-C")
        self.MinTypeCB.addItem("MC")
        self.MinTypeCB.setCurrentIndex(1)
        #lb = QtGui.QLabel("Type: SD")
        row.addWidgets((self.MinTypeCB,))
        
        self.connect(self.MinTypeCB, QtCore.SIGNAL('currentIndexChanged (  QString )'), self.changeMinType)
        
        
        row = self.SubOptionsWindows["MIN"].newRow(self)
        lb = QtGui.QLabel("Steps")
        self.MinStepsEntry = SpinBox()
        self.MinStepsEntry.setFixedWidth(60)
        self.MinStepsEntry.setMaximum(10000000)
        self.MinStepsEntry.setValue(100)
        lb2 = QtGui.QLabel("Tol")
        self.MinTolEntry = QtGui.QLineEdit()
        self.MinTolEntry.setText("1e-10")
        self.MinTolEntry.setFixedWidth(60)
        row.addWidgets((lb,self.MinStepsEntry,lb2,self.MinTolEntry))
        
        self.connect(self.MinStepsEntry, QtCore.SIGNAL('valueChanged (  int )'), self.changeMinSteps)
        self.connect(self.MinTolEntry, QtCore.SIGNAL('textEdited (  QString )'), self.changeMinTol)
        
        row = self.SubOptionsWindows["MIN"].newRow(self)
        lb = QtGui.QLabel("Render Update")
        self.UpdateStepsEntry = SpinBox()
        self.UpdateStepsEntry.setValue(10)
        self.UpdateStepsEntry.setFixedWidth(60)
        self.UpdateStepsEntry.setMaximum(10000000)
        row.addWidgets((lb,self.UpdateStepsEntry))
        
        self.connect(self.UpdateStepsEntry, QtCore.SIGNAL('valueChanged (  int )'), self.changeUpdateFreq)
        
        row = self.SubOptionsWindows["MIN"].newRow()
        self.StartMinBT = QtGui.QPushButton('Minimise Dual Lattice')
        self.connect(self.StartMinBT, QtCore.SIGNAL('clicked()'), self.MinimiseThomsonPoints)
        self.StopMinBT = QtGui.QPushButton('Stop')
        self.StopMinBT.hide()
        self.connect(self.StopMinBT, QtCore.SIGNAL('clicked()'), self.StopMin)
        row.addWidgets((self.StartMinBT,self.StopMinBT))
        
        lb = self.SubOptionsWindows["MIN"].addHeader("Carbon Lattice Minimisation Options")
        
        row = self.SubOptionsWindows["MIN"].newRow()
        self.CarbonMinimiseCombo= QtGui.QComboBox()
        #self.CarbonMinimiseCombo.addItem("Unit Radius Topology")
        self.CarbonMinimiseCombo.addItem("Scaled Topology")
        self.CarbonMinimiseCombo.addItem("EDIP")
        self.CarbonMinimiseCombo.addItem("LAMMPS-AREBO")
        
        self.connect(self.CarbonMinimiseCombo, QtCore.SIGNAL('currentIndexChanged(int)'), self.setCarbonForceField)
        row.addWidgets((self.CarbonMinimiseCombo,))
        
        row = self.SubOptionsWindows["MIN"].newRow()
        self.StartMinCarbonBT = QtGui.QPushButton('Minimise Carbon Atoms')
        self.connect(self.StartMinCarbonBT, QtCore.SIGNAL('clicked()'), self.MinimiseCarbonAtoms)
        self.StopMinCarbonBT = QtGui.QPushButton('Stop')
        self.StopMinCarbonBT.hide()
        self.connect(self.StopMinCarbonBT, QtCore.SIGNAL('clicked()'), self.StopMinCarbon)
        row.addWidgets((self.StartMinCarbonBT,self.StopMinCarbonBT))
        
        #sep = self.SubOptionsWindows["MIN"].addSeparator()
        
        lb = self.SubOptionsWindows["MIN"].addHeader("Minima Search Options")
        #sep = self.SubOptionsWindows["MIN"].addSeparator(dummy=True)
        
#        row = self.SubOptionsWindows["MIN"].newRow()
#        self.MinLoopCk = QtGui.QCheckBox('Enable Minima Search')
#        self.MinLoopCk.setChecked(self.config.opts["MinLoop)
#        self.connect(self.MinLoopCk, QtCore.SIGNAL('clicked()'), self.MinLoopToggle)
#        row.addWidgets((self.MinLoopCk,))
        sep = self.SubOptionsWindows["MIN"].addSeparator(dummy=True)
        
        row = self.SubOptionsWindows["MIN"].newRow()
        lb = QtGui.QLabel("N Minima")
        self.NStructures = SpinBox()
        self.NStructures.setValue(10)
        self.NStructures.setFixedWidth(50)
        self.NMaxStructures = SpinBox()
        self.NMaxStructures.setValue(100)
        self.NMaxStructures.setFixedWidth(50)
        self.connect(self.NStructures, QtCore.SIGNAL('valueChanged(int)'), self.setNStructures)
        self.connect(self.NMaxStructures, QtCore.SIGNAL('valueChanged(int)'), self.setNMaxStructures)
        row.addWidgets((lb,self.NStructures,QtGui.QLabel("N Max Minima"),self.NMaxStructures))
        sep = self.SubOptionsWindows["MIN"].addSeparator(dummy=True)
        
        
        row = self.SubOptionsWindows["MIN"].newRow()
        self.BasinClimbCK = QtGui.QCheckBox('Basin Climbing')
        self.BasinClimbCK.setChecked(self.config.opts["BasinClimb"])
        self.connect(self.BasinClimbCK, QtCore.SIGNAL('clicked()'), self.setBasinClimbing)
        row.addWidgets((self.BasinClimbCK,)) 
        
        
        
        #sep = self.SubOptionsWindows["MIN"].addSeparator()
        row = self.SubOptionsWindows["MIN"].newRow()
        self.ResetLoopCK = QtGui.QCheckBox('Reset   ')
        self.ResetLoopCK.setChecked(self.config.opts["ResetPerIteration"])
        self.connect(self.ResetLoopCK, QtCore.SIGNAL('clicked()'), self.setResetPerIteration)
        self.PerturbLoopCK = QtGui.QCheckBox('Random Perturbation')
        self.PerturbLoopCK.setChecked(self.config.opts["ResetPerIteration"])
        self.connect(self.PerturbLoopCK, QtCore.SIGNAL('clicked()'), self.setPerturbationPerIteration)
        row.addWidgets((QtGui.QLabel("Per iteration: "),self.ResetLoopCK,self.PerturbLoopCK))
        

        
        #sep = self.SubOptionsWindows["MIN"].addSeparator(dummy=True)
        
        row = self.SubOptionsWindows["MIN"].newRow()
        lb = QtGui.QLabel("Stopping Criteria:  ")
        row.addWidgets((lb,))
        
        self.IPstopCk = QtGui.QCheckBox('IP   ')
        self.IPstopCk.setChecked(self.config.opts["StopCriteriaIP"])
        self.connect(self.IPstopCk, QtCore.SIGNAL('clicked()'), self.setMinStopIP)
        self.PentsOnlyCK = QtGui.QCheckBox('Pentagons Only')
        self.PentsOnlyCK.setChecked(self.config.opts["StopCriteriaPentsOnly"])
        self.connect(self.PentsOnlyCK, QtCore.SIGNAL('clicked()'), self.setMinStopPentsOnly)
        
  
        #row = self.SubOptionsWindows["MIN"].newRow()
        row.addWidgets((self.IPstopCk,)) 
        #row = self.SubOptionsWindows["MIN"].newRow()
        row.addWidgets((self.PentsOnlyCK,)) 
        
        sep = self.SubOptionsWindows["MIN"].addSeparator(dummy=True)
        
        row = self.SubOptionsWindows["MIN"].newRow()
        self.AddGaussiansCk = QtGui.QCheckBox('Add Gaussian')
        self.AddGaussiansCk.setChecked(self.config.opts["AddGaussians"])
        self.connect(self.AddGaussiansCk, QtCore.SIGNAL('clicked()'), self.setAddGaussians)
        row.addWidgets((self.AddGaussiansCk,))
        
        row = self.SubOptionsWindows["MIN"].newRow(self)
#        lb = QtGui.QLabel("N")
#        self.NGaussians = QtGui.QLineEdit()
#        self.NGaussians.setText("10")
#        self.NGaussians.setFixedWidth(50)
        lb2 = QtGui.QLabel("W")
        self.GaussianWidth = DoubleSpinBox()
        self.GaussianWidth.setValue(0.5)
        self.GaussianWidth.setSingleStep(0.001)
        self.GaussianWidth.setFixedWidth(50)
        lb3 = QtGui.QLabel("H")
        self.GaussianHeight = DoubleSpinBox()
        self.GaussianHeight.setValue(0.5)
        self.GaussianHeight.setSingleStep(0.001)
        self.GaussianHeight.setFixedWidth(50)
        self.connect(self.GaussianWidth, QtCore.SIGNAL('valueChanged(  double )'), self.setGaussianWidth)
        self.connect(self.GaussianHeight, QtCore.SIGNAL('valueChanged(  double )'), self.setGaussianHeight)
        
        row.addWidgets((lb2,self.GaussianWidth,lb3,self.GaussianHeight))
        
        row = self.SubOptionsWindows["MIN"].newRow()
        self.AddGaussianBT = QtGui.QPushButton('Add Gaussian')
        self.connect(self.AddGaussianBT, QtCore.SIGNAL('clicked()'), self.AddGaussian)
        row.addWidgets((self.AddGaussianBT,))
        
        #row = self.SubOptionsWindows["MIN"].newRow()
        self.ResetGaussiansBT = QtGui.QPushButton('Reset Gaussians')
        self.connect(self.ResetGaussiansBT, QtCore.SIGNAL('clicked()'), self.ResetGaussians)
        row.addWidgets((self.ResetGaussiansBT,))
        
        sep = self.SubOptionsWindows["MIN"].addSeparator(dummy=True)
        
        self.CarbonMinimiseCk = QtGui.QCheckBox("Carbon Lattice Minimisation")
        self.CarbonMinimiseCk.setChecked(self.config.opts["CarbonMinimise"])
        #self.CalcEDIPCk.setMinimumWidth(222)
        self.connect(self.CarbonMinimiseCk, QtCore.SIGNAL('clicked()'), self.SetCarbonMinimise)
        row = self.SubOptionsWindows["MIN"].newRow()
        row.addWidgets((self.CarbonMinimiseCk,))

        
        row = self.SubOptionsWindows["MIN"].newRow()
        self.StartMinSearchBT = QtGui.QPushButton('Perform Minima Search')
        self.connect(self.StartMinSearchBT, QtCore.SIGNAL('clicked()'), self.MinimaSearch)
        self.StopMinSearchBT = QtGui.QPushButton('Stop')
        self.StopMinSearchBT.hide()
        self.connect(self.StopMinSearchBT, QtCore.SIGNAL('clicked()'), self.StopMinSearch)
        
        self.SearchProgressbar = QtGui.QProgressBar()
        self.SearchProgressbar.setMinimum(0)
        self.SearchProgressbar.setMaximum(self.config.opts["NStructures"])
        self.SearchProgressbar.setTextVisible(True)
        self.SearchProgressbar.hide()
        
        
        row.addWidgets((self.StartMinSearchBT,self.SearchProgressbar,self.StopMinSearchBT))
        

        
        #sep = self.SubOptionsWindows["MIN"].addSeparator()
        #self.FullereneWidgets.append(sep)
        #sep = self.SubOptionsWindows["MIN"].addSeparator(dummy=True)      
        #self.FullereneWidgets.append(sep)  
        #row = self.SubOptionsWindows["MIN"].newRow()
        #lb2 = QtGui.QLabel("Known Dual Lattice Global Minimum:")
#        lb = self.SubOptionsWindows["MIN"].addHeader("Known Dual Lattice Global Minimum:")
#        self.FullereneWidgets.append(lb)
#        self.KnownMinimum = QtGui.QLineEdit()
#        self.KnownMinimum.setText("0")
#        self.KnownMinimum.setFixedWidth(150)
#        #row.addWidgets((lb2,))
#        row = self.SubOptionsWindows["MIN"].newRow()
#        row.addWidgets((self.KnownMinimum,))
#        
#        self.FullereneWidgets.append(row)
        
        

        
        sep = self.SubOptionsWindows["MIN"].addSeparator()
        
        row = self.SubOptionsWindows["MIN"].newRow()
        self.ShowStructureTableBT = QtGui.QPushButton('Structures Table')
        self.connect(self.ShowStructureTableBT, QtCore.SIGNAL('clicked()'), self.showStructureWindow)
        row.addWidgets((self.ShowStructureTableBT,))

        
        #sep = self.SubOptionsWindows["MIN"].addSeparator()
        


        

    def setupCalcRenderWidgets(self):        
        #self.SubOptionsWindows["CALCREN"].setMinimumWidth(200)
        #sep = self.SubOptionsWindows["CALCREN"].addSeparator(dummy=True)
        #self.FullereneWidgets.append(sep)
        
        ############### Dual Lattice / Thomson Points ###########################
        self.SubOptionsWindows["CALCREN"].addSeparator(dummy=True)
        self.SubOptionsWindows["CALCREN"].addHeader("Points")
        
        row = self.SubOptionsWindows["CALCREN"].newRow(self)
        self.FullereneCalcRenTable = TableWidget(290,300)
        self.FullereneCalcRenTable.verticalHeader().hide()
        self.FullereneCalcRenTable.setupHeaders(["Option","Calc","Ren","IDs","Rad","Col","Box"],
                                       [90,30,30,30,50,30,30])
        
        
#        self.FullereneCalcRenTable.setColumnCount(7)
#        self.FullereneCalcRenTable.setHorizontalHeaderLabels(("Option","Calc","Ren","IDs","Rad","Col","Box"))
#        #self.MinimaTable.setMinimumHeight(200)
#        
#        #self.MinimaTable.setRowHeight(30)
#        #self.MinimaTable.setColumnWidth(0,40)
#        self.FullereneCalcRenTable.setColumnWidth(0,100)
#        self.FullereneCalcRenTable.setColumnWidth(1,30)
#        self.FullereneCalcRenTable.setColumnWidth(2,30)
#        self.FullereneCalcRenTable.setColumnWidth(3,30)
#        self.FullereneCalcRenTable.setColumnWidth(4,50)
#        self.FullereneCalcRenTable.setColumnWidth(5,40)
#        self.FullereneCalcRenTable.setColumnWidth(6,30)
        row.addWidget(self.FullereneCalcRenTable)
        self.FullereneWidgets.append(self.FullereneCalcRenTable)
        
        row = self.SubOptionsWindows["CALCREN"].newRow(self)
        self.NanotubeCalcRenTable = TableWidget(290,300)
        self.NanotubeCalcRenTable.verticalHeader().hide()
        self.NanotubeCalcRenTable.setupHeaders(["Option","Calc","Ren","IDs","Rad","Col","Box"],
                                       [90,30,30,30,50,30,30])
        
        
#        self.NanotubeCalcRenTable.setColumnCount(7)
#        #self.NanotubeCalcRenTable.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding,QtGui.QSizePolicy.Expanding)
#        
#        self.NanotubeCalcRenTable.setHorizontalHeaderLabels(("Option","Calc","Ren","IDs","Rad","Col","Box"))
#        #self.MinimaTable.setMinimumHeight(200)
#        
#        #self.MinimaTable.setRowHeight(30)
#        #self.MinimaTable.setColumnWidth(0,40)
#        self.NanotubeCalcRenTable.setColumnWidth(0,100)
#        self.NanotubeCalcRenTable.setColumnWidth(1,30)
#        self.NanotubeCalcRenTable.setColumnWidth(2,30)
#        self.NanotubeCalcRenTable.setColumnWidth(3,30)
#        self.NanotubeCalcRenTable.setColumnWidth(4,50)
#        self.NanotubeCalcRenTable.setColumnWidth(5,40)
#        self.NanotubeCalcRenTable.setColumnWidth(6,30)
        row.addWidget(self.NanotubeCalcRenTable)
        self.NanotubeWidgets.append(self.NanotubeCalcRenTable)   
        
        #lb = self.SubOptionsWindows["CALCREN"].addHeader("Thomson Points")
        #sep = self.SubOptionsWindows["CALCREN"].addSeparator(dummy=True)

        #lb = self.SubOptionsWindows["CALCREN"].addSubHeader("Cap")
        
                        
        self.ShowFullereneDualLatticePointsCk = QtGui.QCheckBox()
        #self.ShowTubeDualLatticePointsCk.setFixedWidth(60)
        self.ShowFullereneDualLatticePointsCk.setChecked(self.config.opts["ShowFullereneDualLatticePoints"])
        self.connect(self.ShowFullereneDualLatticePointsCk, QtCore.SIGNAL('clicked()'), self.ShowFullereneDualLatticePoints)
                
        
        self.FullereneDualLatticePointRadSB = DoubleSpinBox()
        self.FullereneDualLatticePointRadSB.setValue(0.02)
        self.FullereneDualLatticePointRadSB.setSingleStep(0.01)
        self.FullereneDualLatticePointRadSB.setFixedWidth(50)
        self.connect(self.FullereneDualLatticePointRadSB, QtCore.SIGNAL('valueChanged(  double )'), 
                     self.Operations.setFullereneDualLatticePointRad)
        
        rgb = numpy.array(self.config.opts["FullereneDualLatticePointColourRGB"])*255
        self.FullereneDualLatticePointColour = QtGui.QColor(rgb[0],rgb[1],rgb[2])         
        self.FullereneDualLatticePointColourBT = QtGui.QPushButton("")
        self.FullereneDualLatticePointColourBT.setFixedWidth(25)
        #self.TubeThomsonPointColourBT.setFixedHeight(20)
        self.FullereneDualLatticePointColourBT.setStyleSheet("QPushButton { background-color: %s ; border-radius: 5px }" % self.FullereneDualLatticePointColour.name())
        #self.connect(self.FullereneDualLatticePointColourBT, QtCore.SIGNAL('clicked()'), self.Operations.changeFullereneDualLatticePointColour)
        call = lambda button=self.FullereneDualLatticePointColourBT: self.Operations.changeFullereneDualLatticePointColour(button)
        self.connect(self.FullereneDualLatticePointColourBT, QtCore.SIGNAL('clicked()'), call)
        
        
        self.ShowFullereneDualLatticeLabelsCk = QtGui.QCheckBox()
        self.connect(self.ShowFullereneDualLatticeLabelsCk, QtCore.SIGNAL('clicked()'), self.ShowLabels)

        self.ShowFullereneDualLatticeBoxCk = QtGui.QCheckBox()
        self.connect(self.ShowFullereneDualLatticeBoxCk, QtCore.SIGNAL('clicked()'), self.ShowBoundingBoxes)

        
        self.FullereneCalcRenTable.insertRow(0)
        lab = QtGui.QTableWidgetItem("Thomson Points")
        self.FullereneCalcRenTable.setItem(0,0,lab)
        
        self.FullereneCalcRenTable.setCellWidget(0,2,HolderWidget(self.ShowFullereneDualLatticePointsCk))
        self.FullereneCalcRenTable.setCellWidget(0,3,HolderWidget(self.ShowFullereneDualLatticeLabelsCk))
        self.FullereneCalcRenTable.setCellWidget(0,4,HolderWidget(self.FullereneDualLatticePointRadSB))
        self.FullereneCalcRenTable.setCellWidget(0,5,HolderWidget(self.FullereneDualLatticePointColourBT))
        self.FullereneCalcRenTable.setCellWidget(0,6,HolderWidget(self.ShowFullereneDualLatticeBoxCk))
                        
        self.ShowTubeDualLatticePointsCk = QtGui.QCheckBox()
        #self.ShowTubeDualLatticePointsCk.setFixedWidth(60)
        self.ShowTubeDualLatticePointsCk.setChecked(self.config.opts["ShowTubeDualLatticePoints"])
        self.connect(self.ShowTubeDualLatticePointsCk, QtCore.SIGNAL('clicked()'), self.ShowTubeDualLatticePoints)
        self.TubeDualLatticePointRadSB = DoubleSpinBox()
        self.TubeDualLatticePointRadSB.setValue(0.02)
        self.TubeDualLatticePointRadSB.setSingleStep(0.01)
        self.TubeDualLatticePointRadSB.setFixedWidth(50)
        self.connect(self.TubeDualLatticePointRadSB, QtCore.SIGNAL('valueChanged(  double )'), 
                     self.Operations.setTubeDualLatticePointRad)
        
        
        rgb = numpy.array(self.config.opts["TubeDualLatticePointColourRGB"])*255
        printl("rgb",rgb)
        self.TubeDualLatticePointColour = QtGui.QColor(rgb[0],rgb[1],rgb[2])    
        self.TubeDualLatticePointColourBT = QtGui.QPushButton("")
        self.TubeDualLatticePointColourBT.setFixedWidth(25)
        #self.TubeThomsonPointColourBT.setFixedHeight(20)
        self.TubeDualLatticePointColourBT.setStyleSheet("QPushButton { background-color: %s ; border-radius: 5px }" % self.TubeDualLatticePointColour.name())
        call = lambda button=self.TubeDualLatticePointColourBT: self.Operations.changeTubeDualLatticePointColour(button)
        self.connect(self.TubeDualLatticePointColourBT, QtCore.SIGNAL('clicked()'), call)
               
        
        
        
        self.ShowTubeDualLatticeLabelsCk = QtGui.QCheckBox()
        self.connect(self.ShowTubeDualLatticeLabelsCk, QtCore.SIGNAL('clicked()'), self.ShowLabels)
        self.ShowTubeDualLatticeBoxCk = QtGui.QCheckBox()
        self.connect(self.ShowTubeDualLatticeBoxCk, QtCore.SIGNAL('clicked()'), self.ShowBoundingBoxes)
        
        self.NanotubeCalcRenTable.insertRow(0)
        lab = QtGui.QTableWidgetItem("Tube Thomson Points")
        self.NanotubeCalcRenTable.setItem(0,0,lab)
        
        self.NanotubeCalcRenTable.setCellWidget(0,2,HolderWidget(self.ShowTubeDualLatticePointsCk))
        self.NanotubeCalcRenTable.setCellWidget(0,3,HolderWidget(self.ShowTubeDualLatticeLabelsCk))
        self.NanotubeCalcRenTable.setCellWidget(0,4,HolderWidget(self.TubeDualLatticePointRadSB))
        self.NanotubeCalcRenTable.setCellWidget(0,5,HolderWidget(self.TubeDualLatticePointColourBT))
        self.NanotubeCalcRenTable.setCellWidget(0,6,HolderWidget(self.ShowTubeDualLatticeBoxCk))
        
        self.CapDualLatticePointRadSB = DoubleSpinBox()
        self.CapDualLatticePointRadSB.setValue(0.02)
        self.CapDualLatticePointRadSB.setSingleStep(0.01)
        self.CapDualLatticePointRadSB.setFixedWidth(50)
        self.connect(self.CapDualLatticePointRadSB, QtCore.SIGNAL('valueChanged(  double )'), 
                     self.Operations.setCapDualLatticePointRad)
        #row.addWidgets((lb,self.ThomsonPointRad))
        
        rgb = numpy.array(self.config.opts["CapDualLatticePointColourRGB"])*255
        self.CapDualLatticePointColour = QtGui.QColor(rgb[0],rgb[1],rgb[2])      
        self.CapDualLatticePointColourBT = QtGui.QPushButton("")
        self.CapDualLatticePointColourBT.setFixedWidth(25)
        #self.TubeThomsonPointColourBT.setFixedHeight(50)
        self.CapDualLatticePointColourBT.setStyleSheet("QPushButton { background-color: %s ; border-radius: 5px }" % self.CapDualLatticePointColour.name())
        #self.connect(self.CapDualLatticePointColourBT, QtCore.SIGNAL('clicked()'), self.Operations.changeCapDualLatticePointColour)
        call = lambda button=self.CapDualLatticePointColourBT: self.Operations.changeCapDualLatticePointColour(button)
        self.connect(self.CapDualLatticePointColourBT, QtCore.SIGNAL('clicked()'), call)
        
        #row = self.TriForm.newRow()
        self.ShowCapDualLatticePointsCB = QtGui.QCheckBox('')
        self.ShowCapDualLatticePointsCB.setChecked(self.config.opts["ShowCapDualLatticePoints"])
        self.connect(self.ShowCapDualLatticePointsCB, QtCore.SIGNAL('clicked()'), self.ShowCapDualLatticePoints)
        
        self.ShowCapDualLatticeLabelsCk = QtGui.QCheckBox()  
        self.connect(self.ShowCapDualLatticeLabelsCk, QtCore.SIGNAL('clicked()'), self.ShowLabels)     
        self.ShowCapDualLatticeBoxCk = QtGui.QCheckBox()
        self.connect(self.ShowCapDualLatticeBoxCk, QtCore.SIGNAL('clicked()'), self.ShowBoundingBoxes)
         
        #lb = self.SubOptionsWindows["CALCREN"].addSubHeader("Full System")
        #self.NanotubeWidgets.append(lb)    
        
        self.NanotubeCalcRenTable.insertRow(1)
        lab = QtGui.QTableWidgetItem("Cap Thomson Points")
        self.NanotubeCalcRenTable.setItem(1,0,lab)
        
        self.NanotubeCalcRenTable.setCellWidget(1,2,HolderWidget(self.ShowCapDualLatticePointsCB))
        self.NanotubeCalcRenTable.setCellWidget(1,3,HolderWidget(self.ShowCapDualLatticeLabelsCk))
        self.NanotubeCalcRenTable.setCellWidget(1,4,HolderWidget(self.CapDualLatticePointRadSB))
        self.NanotubeCalcRenTable.setCellWidget(1,5,HolderWidget(self.CapDualLatticePointColourBT))
        self.NanotubeCalcRenTable.setCellWidget(1,6,HolderWidget(self.ShowCapDualLatticeBoxCk))

        row = self.SubOptionsWindows["CALCREN"].newRow()
        self.CappedTubeDualLatticePointRadSB = DoubleSpinBox()
        self.CappedTubeDualLatticePointRadSB.setValue(0.02)
        self.CappedTubeDualLatticePointRadSB.setSingleStep(0.01)
        self.CappedTubeDualLatticePointRadSB.setFixedWidth(50)
        self.connect(self.CappedTubeDualLatticePointRadSB, QtCore.SIGNAL('valueChanged(  double )'), 
                     self.Operations.setCappedTubeDualLatticePointRad)
        #row.addWidgets((lb,self.ThomsonPointRad))
        
        rgb = numpy.array(self.config.opts["CappedTubeDualLatticePointColourRGB"])*255
        self.CappedTubeDualLatticePointColour = QtGui.QColor(rgb[0],rgb[1],rgb[2])      
        self.CappedTubeDualLatticePointColourBT = QtGui.QPushButton("")
        self.CappedTubeDualLatticePointColourBT.setFixedWidth(25)
        #self.TubeThomsonPointColourBT.setFixedHeight(50)
        self.CappedTubeDualLatticePointColourBT.setStyleSheet("QPushButton { background-color: %s ; border-radius: 5px }" % self.CappedTubeDualLatticePointColour.name())
        #self.connect(self.CappedTubeDualLatticePointColourBT, QtCore.SIGNAL('clicked()'), self.Operations.changeCappedTubeDualLatticePointColour)
        call = lambda button=self.CappedTubeDualLatticePointColourBT: self.Operations.changeCappedTubeDualLatticePointColour(button)
        self.connect(self.CappedTubeDualLatticePointColourBT, QtCore.SIGNAL('clicked()'), call)
        
        #row = self.TriForm.newRow()
        self.ShowCappedTubeDualLatticePointsCB = QtGui.QCheckBox('')
        self.ShowCappedTubeDualLatticePointsCB.setChecked(self.config.opts["ShowCappedTubeDualLatticePoints"])
        self.connect(self.ShowCappedTubeDualLatticePointsCB, QtCore.SIGNAL('clicked()'), self.ShowCappedTubeDualLatticePoints)
        
        self.ShowCappedTubeDualLatticeLabelsCk = QtGui.QCheckBox()  
        self.connect(self.ShowCappedTubeDualLatticeLabelsCk, QtCore.SIGNAL('clicked()'), self.ShowLabels)      
        self.ShowCappedTubeDualLatticeBoxCk = QtGui.QCheckBox()
        self.connect(self.ShowCappedTubeDualLatticeBoxCk, QtCore.SIGNAL('clicked()'), self.ShowBoundingBoxes)
        
        self.NanotubeCalcRenTable.insertRow(2)
        lab = QtGui.QTableWidgetItem("Capped Tube Thomson Points")
        self.NanotubeCalcRenTable.setItem(2,0,lab)
        
        self.NanotubeCalcRenTable.setCellWidget(2,2,HolderWidget(self.ShowCappedTubeDualLatticePointsCB))
        self.NanotubeCalcRenTable.setCellWidget(2,3,HolderWidget(self.ShowCappedTubeDualLatticeLabelsCk))
        self.NanotubeCalcRenTable.setCellWidget(2,4,HolderWidget(self.CappedTubeDualLatticePointRadSB))
        self.NanotubeCalcRenTable.setCellWidget(2,5,HolderWidget(self.CappedTubeDualLatticePointColourBT))
        self.NanotubeCalcRenTable.setCellWidget(2,6,HolderWidget(self.ShowCappedTubeDualLatticeBoxCk))
        
        ############### Carbon Atoms ###########################


        self.CalcFullereneCarbonAtomsCk = QtGui.QCheckBox()
        self.CalcFullereneCarbonAtomsCk.setChecked(self.config.opts["CalcFullereneCarbonAtoms"])
        self.connect(self.CalcFullereneCarbonAtomsCk, QtCore.SIGNAL('clicked()'), self.UpdateCheckboxes)
        self.FullereneWidgets.append(row)
        
        
        self.ShowFullereneCarbonAtomsCk = QtGui.QCheckBox()
        self.ShowFullereneCarbonAtomsCk.setChecked(self.config.opts["ShowFullereneCarbonAtoms"])
        self.connect(self.ShowFullereneCarbonAtomsCk, QtCore.SIGNAL('clicked()'), self.ShowFullereneCarbonAtoms)
        
        self.FullereneCarbonAtomsRadSB = DoubleSpinBox()
        self.FullereneCarbonAtomsRadSB.setValue(0.02)
        self.FullereneCarbonAtomsRadSB.setSingleStep(0.01)
        self.FullereneCarbonAtomsRadSB.setFixedWidth(50)
        self.connect(self.FullereneCarbonAtomsRadSB, QtCore.SIGNAL('valueChanged(  double )'), self.Operations.setFullereneCarbonAtomRad)
        
        rgb = numpy.array(self.config.opts["FullereneCarbonAtomColourRGB"])*255
        self.FullereneCarbonAtomsColour = QtGui.QColor(rgb[0],rgb[1],rgb[2])      
        self.FullereneCarbonAtomsColourBT = QtGui.QPushButton("")
        self.FullereneCarbonAtomsColourBT.setFixedWidth(25)
        #self.TubeThomsonPointColourBT.setFixedHeight(20)
        self.FullereneCarbonAtomsColourBT.setStyleSheet("QPushButton { background-color: %s ; border-radius: 5px }" % self.FullereneCarbonAtomsColour.name())
        #self.connect(self.FullereneCarbonAtomsColourBT, QtCore.SIGNAL('clicked()'), self.Operations.changeFullereneCarbonAtomsColour)
        call = lambda button=self.FullereneCarbonAtomsColourBT: self.Operations.changeFullereneCarbonAtomsColour(button)
        self.connect(self.FullereneCarbonAtomsColourBT, QtCore.SIGNAL('clicked()'), call)
        
        self.ShowFullereneCarbonAtomsLabelsCk = QtGui.QCheckBox()     
        self.connect(self.ShowFullereneCarbonAtomsLabelsCk, QtCore.SIGNAL('clicked()'), self.ShowLabels)
        
        self.ShowFullereneCarbonAtomsBoxCk = QtGui.QCheckBox()
        self.connect(self.ShowFullereneCarbonAtomsBoxCk, QtCore.SIGNAL('clicked()'), self.ShowBoundingBoxes)
        
        self.FullereneCalcRenTable.insertRow(1)
        lab = QtGui.QTableWidgetItem("Carbon Atoms")
        self.FullereneCalcRenTable.setItem(1,0,lab)
        
        
        self.FullereneCalcRenTable.setCellWidget(1,1,HolderWidget(self.CalcFullereneCarbonAtomsCk))
        self.FullereneCalcRenTable.setCellWidget(1,2,HolderWidget(self.ShowFullereneCarbonAtomsCk))
        self.FullereneCalcRenTable.setCellWidget(1,3,HolderWidget(self.ShowFullereneCarbonAtomsLabelsCk))
        self.FullereneCalcRenTable.setCellWidget(1,4,HolderWidget(self.FullereneCarbonAtomsRadSB))
        self.FullereneCalcRenTable.setCellWidget(1,5,HolderWidget(self.FullereneCarbonAtomsColourBT))
        self.FullereneCalcRenTable.setCellWidget(1,6,HolderWidget(self.ShowFullereneCarbonAtomsBoxCk))
        
        row = self.SubOptionsWindows["GEN"].newRow()
        self.ShowTubeCarbonAtomsCk = QtGui.QCheckBox()
        self.ShowTubeCarbonAtomsCk.setChecked(self.config.opts["ShowTubeCarbonAtoms"])
        self.connect(self.ShowTubeCarbonAtomsCk, QtCore.SIGNAL('clicked()'), self.ShowTubeCarbonAtoms)
        
        self.TubeCarbonAtomRad = DoubleSpinBox()
        self.TubeCarbonAtomRad.setValue(0.02)
        self.TubeCarbonAtomRad.setFixedWidth(50)
        #self.TubeCarbonAtomRad.setFixedHeight(50)
        self.TubeCarbonAtomRad.setSingleStep(0.01)
        self.connect(self.TubeCarbonAtomRad, QtCore.SIGNAL('valueChanged(  double )'), self.Operations.setTubeCarbonAtomRad)
          
        self.TubeCarbonAtomColour = QtGui.QColor(0, 0, 0)     
        r= "%0.2f" % (float(self.TubeCarbonAtomColour.red())/255.0)
        g= "%0.2f" % (float(self.TubeCarbonAtomColour.green())/255.0)
        b= "%0.2f" % (float(self.TubeCarbonAtomColour.blue())/255.0)
        self.TubeCarbonAtomColourRGB = (float(r),float(g),float(b))
        self.TubeCarbonAtomColourBT = QtGui.QPushButton("")
        self.TubeCarbonAtomColourBT.setFixedWidth(25)
        #self.TubeThomsonPointColourBT.setFixedHeight(20)
        self.TubeCarbonAtomColourBT.setStyleSheet("QPushButton { background-color: %s ; border-radius: 5px }" % self.TubeCarbonAtomColour.name())
        #self.connect(self.TubeCarbonAtomColourBT, QtCore.SIGNAL('clicked()'), self.Operations.changeTubeCarbonAtomColour)
        call = lambda button=self.TubeCarbonAtomColourBT: self.Operations.changeTubeCarbonAtomColour(button)
        self.connect(self.TubeCarbonAtomColourBT, QtCore.SIGNAL('clicked()'), call)
        
        self.ShowTubeCarbonAtomsLabelsCk = QtGui.QCheckBox() 
        self.connect(self.ShowTubeCarbonAtomsLabelsCk, QtCore.SIGNAL('clicked()'), self.ShowLabels)
        
        self.ShowTubeCarbonAtomsBoxCk = QtGui.QCheckBox()
        self.connect(self.ShowTubeCarbonAtomsBoxCk, QtCore.SIGNAL('clicked()'), self.ShowBoundingBoxes)
        
        self.NanotubeCalcRenTable.insertRow(2)
        lab = QtGui.QTableWidgetItem("Tube Carbon Atoms")
        self.NanotubeCalcRenTable.setItem(2,0,lab)
        
        self.NanotubeCalcRenTable.setCellWidget(2,2,HolderWidget(self.ShowTubeCarbonAtomsCk))
        self.NanotubeCalcRenTable.setCellWidget(2,3,HolderWidget(self.ShowTubeCarbonAtomsLabelsCk))
        self.NanotubeCalcRenTable.setCellWidget(2,4,HolderWidget(self.TubeCarbonAtomRad))
        self.NanotubeCalcRenTable.setCellWidget(2,5,HolderWidget(self.TubeCarbonAtomColourBT))
        self.NanotubeCalcRenTable.setCellWidget(2,6,HolderWidget(self.ShowTubeCarbonAtomsBoxCk))
        
        self.CappedTubeCarbonAtomRadSB = DoubleSpinBox()
        self.CappedTubeCarbonAtomRadSB.setValue(0.02)
        self.CappedTubeCarbonAtomRadSB.setFixedWidth(50)
        self.CappedTubeCarbonAtomRadSB.setSingleStep(0.01)
        self.connect(self.CappedTubeCarbonAtomRadSB, QtCore.SIGNAL('valueChanged(  double )'), self.Operations.setCappedTubeCarbonAtomRad)
        
        self.ShowCappedTubeCarbonAtomsCk = QtGui.QCheckBox()
        self.connect(self.ShowCappedTubeCarbonAtomsCk, QtCore.SIGNAL('clicked()'), self.ShowCappedTubeCarbonAtoms)

        
        self.CalcCappedTubeCarbonAtomsCk = QtGui.QCheckBox()
        self.CalcCappedTubeCarbonAtomsCk.setChecked(self.config.opts["CalcCappedTubeCarbonAtoms"])
        self.connect(self.CalcCappedTubeCarbonAtomsCk, QtCore.SIGNAL('clicked()'), self.UpdateCheckboxes)
        self.NanotubeWidgets.append(row)
        
        
        rgb = numpy.array(self.config.opts["CappedTubeCarbonAtomColourRGB"])*255
        self.CappedTubeCarbonAtomColour = QtGui.QColor(rgb[0],rgb[1],rgb[2])     
        self.CappedTubeCarbonAtomColourBT = QtGui.QPushButton("")
        self.CappedTubeCarbonAtomColourBT.setFixedWidth(25)
        #self.TubeThomsonPointColourBT.setFixedHeight(20)
        self.CappedTubeCarbonAtomColourBT.setStyleSheet("QPushButton { background-color: %s ; border-radius: 5px }" % self.CappedTubeCarbonAtomColour.name())
        #self.connect(self.CappedTubeCarbonAtomColourBT, QtCore.SIGNAL('clicked()'), self.Operations.changeCappedTubeCarbonAtomColour)
        call = lambda button=self.CappedTubeCarbonAtomColourBT: self.Operations.changeCappedTubeCarbonAtomColour(button)
        self.connect(self.CappedTubeCarbonAtomColourBT, QtCore.SIGNAL('clicked()'), call)

        self.ShowCappedTubeCarbonAtomsLabelsCk = QtGui.QCheckBox() 
        self.connect(self.ShowCappedTubeCarbonAtomsLabelsCk, QtCore.SIGNAL('clicked()'), self.ShowLabels)
        
        self.ShowCappedTubeCarbonAtomsBoxCk = QtGui.QCheckBox()
        self.connect(self.ShowCappedTubeCarbonAtomsBoxCk, QtCore.SIGNAL('clicked()'), self.ShowBoundingBoxes)
        
        self.NanotubeCalcRenTable.insertRow(3)
        lab = QtGui.QTableWidgetItem("Capped Tube Carbon Atoms")
        self.NanotubeCalcRenTable.setItem(3,0,lab)
        
        
        self.NanotubeCalcRenTable.setCellWidget(3,1,HolderWidget(self.CalcCappedTubeCarbonAtomsCk))
        self.NanotubeCalcRenTable.setCellWidget(3,2,HolderWidget(self.ShowCappedTubeCarbonAtomsCk))
        self.NanotubeCalcRenTable.setCellWidget(3,3,HolderWidget(self.ShowCappedTubeCarbonAtomsLabelsCk))
        self.NanotubeCalcRenTable.setCellWidget(3,4,HolderWidget(self.CappedTubeCarbonAtomRadSB))
        self.NanotubeCalcRenTable.setCellWidget(3,5,HolderWidget(self.CappedTubeCarbonAtomColourBT))
        self.NanotubeCalcRenTable.setCellWidget(3,6,HolderWidget(self.ShowCappedTubeCarbonAtomsBoxCk))
        #sep = self.SubOptionsWindows["CALCREN"].addSeparator()
        #self.FullereneWidgets.append(sep)
        #self.NanotubeCalcRenTable.updateGeometry() 
        
        
        ###### General Calc Render ######
        self.SubOptionsWindows["CALCREN"].addSeparator(dummy=True)
        self.SubOptionsWindows["CALCREN"].addHeader("General")
        
        row = self.SubOptionsWindows["CALCREN"].newRow(self)
        self.GeneralCalcRenTable = TableWidget(280,300)
        self.GeneralCalcRenTable.verticalHeader().hide()
        self.GeneralCalcRenTable.setupHeaders(["Option","Calc","Ren","Parameters"],
                                       [100,30,30,150])
        #self.GeneralCalcRenTable.horizontalHeader().updateGeometry()
        
#        self.GeneralCalcRenTable.setColumnCount(4)
#        #self.NanotubeCalcRenTable.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding,QtGui.QSizePolicy.Expanding)
#        
#        self.GeneralCalcRenTable.setHorizontalHeaderLabels(("Option","Calc","Ren","Parameters"))
#        #self.MinimaTable.setMinimumHeight(200)
#        
#        #self.MinimaTable.setRowHeight(30)
#        #self.MinimaTable.setColumnWidth(0,40)
#        self.GeneralCalcRenTable.setColumnWidth(0,100)
#        self.GeneralCalcRenTable.setColumnWidth(1,30)
#        self.GeneralCalcRenTable.setColumnWidth(2,30)
#        self.GeneralCalcRenTable.setColumnWidth(3,150)

        row.addWidget(self.GeneralCalcRenTable)
        
        #lb = self.SubOptionsWindows["CALCREN"].addHeader("Triangulation")
        #self.NanotubeWidgets.append(lb)
        
        #row = self.SubOptionsWindows["CALCREN"].newRow()
        self.CalcTriCk = QtGui.QCheckBox()
        self.CalcTriCk.setChecked(self.config.opts["CalcTriangulation"])
        #self.CalcTriCk.setMinimumWidth(180)
        self.connect(self.CalcTriCk, QtCore.SIGNAL('clicked()'), self.UpdateCheckboxes)
        
        self.ShowTriCk = QtGui.QCheckBox()
        self.ShowTriCk.setChecked(self.config.opts["ShowTriangulation"])
        
        self.connect(self.ShowTriCk, QtCore.SIGNAL('clicked()'), self.ShowTriangles)
        #row.addWidgets((self.CalcTriCk,self.ShowTriCk,))
        
        self.GeneralCalcRenTable.insertRow(0)
        lab = QtGui.QTableWidgetItem("Triangulation")
        self.GeneralCalcRenTable.setItem(0,0,lab)
        self.GeneralCalcRenTable.setCellWidget(0,1,HolderWidget(self.CalcTriCk))
        self.GeneralCalcRenTable.setCellWidget(0,2,HolderWidget(self.ShowTriCk))

        
                
        #sep = self.SubOptionsWindows["CALCREN"].addSeparator()
        #lb = self.SubOptionsWindows["CALCREN"].addHeader("Carbon Bonds")
        
        
        #row = self.SubOptionsWindows["CALCREN"].newRow()
        self.CalcCarbonBondsCk = QtGui.QCheckBox()
        self.CalcCarbonBondsCk.setChecked(self.config.opts["CalcCarbonBonds"])
        #self.CalcCarbonBondsCk.setMinimumWidth(180)
        self.connect(self.CalcCarbonBondsCk, QtCore.SIGNAL('clicked()'), self.UpdateCheckboxes)
        self.ShowCarbonBondsCk = QtGui.QCheckBox()
        self.ShowCarbonBondsCk.setChecked(self.config.opts["ShowCarbonBonds"])
        self.connect(self.ShowCarbonBondsCk, QtCore.SIGNAL('clicked()'), self.ShowCarbonBonds)
        #row.addWidgets((self.CalcCarbonBondsCk,self.ShowCarbonBondsCk,))
        
        #row = self.SubOptionsWindows["CALCREN"].newRow()
        lb = QtGui.QLabel("Thickness")
        self.bondThicknessEntry = DoubleSpinBox()
        self.bondThicknessEntry.setMinimum(0.0001)
        self.bondThicknessEntry.setValue(0.01)
        self.bondThicknessEntry.setDecimals(4)
        self.bondThicknessEntry.setSingleStep(0.001)
        self.bondThicknessEntry.setFixedWidth(60)
        self.connect(self.bondThicknessEntry, QtCore.SIGNAL('valueChanged(  double )'), self.BondThicknessChanged)
        #row.addWidgets((lb,self.bondThicknessEntry))
        
        
        self.GeneralCalcRenTable.insertRow(1)
        lab = QtGui.QTableWidgetItem("Carbon Bonds")
        self.GeneralCalcRenTable.setItem(1,0,lab)
        self.GeneralCalcRenTable.setCellWidget(1,1,HolderWidget(self.CalcCarbonBondsCk))
        self.GeneralCalcRenTable.setCellWidget(1,2,HolderWidget(self.ShowCarbonBondsCk))
        self.GeneralCalcRenTable.setCellWidget(1,3,HolderWidget((lb,self.bondThicknessEntry)))
        
        
        #sep = self.SubOptionsWindows["CALCREN"].addSeparator()
        #lb = self.SubOptionsWindows["CALCREN"].addHeader("Carbon Bonding Polygons")        
        #row = self.SubOptionsWindows["CALCREN"].newRow()
        self.CalcBondingPolygonsCk = QtGui.QCheckBox()
        self.CalcBondingPolygonsCk.setChecked(self.config.opts["CalcCarbonRings"])
        self.connect(self.CalcBondingPolygonsCk, QtCore.SIGNAL('clicked()'), self.UpdateCheckboxes)
        self.ShowBondingPolygonsCk = QtGui.QCheckBox()
        self.ShowBondingPolygonsCk.setChecked(self.config.opts["ShowCarbonRings"])
        self.connect(self.ShowBondingPolygonsCk, QtCore.SIGNAL('clicked()'), self.ShowCarbonRings)
        #row.addWidgets((self.CalcBondingPolygonsCk,self.ShowBondingPolygonsCk,))
        
        self.GeneralCalcRenTable.insertRow(2)
        lab = QtGui.QTableWidgetItem("Carbon Rings")
        self.GeneralCalcRenTable.setItem(2,0,lab)
        self.GeneralCalcRenTable.setCellWidget(2,1,HolderWidget(self.CalcBondingPolygonsCk))
        self.GeneralCalcRenTable.setCellWidget(2,2,HolderWidget(self.ShowBondingPolygonsCk))


        #sep = self.SubOptionsWindows["CALCREN"].addSeparator()
        #lb = self.SubOptionsWindows["CALCREN"].addHeader("Schlegel View")    
        #row = self.SubOptionsWindows["CALCREN"].newRow()
        self.CalcSchlegelCk = QtGui.QCheckBox()
        self.CalcSchlegelCk.setChecked(self.config.opts["CalcSchlegel"])
        #self.CalcSchlegelCk.setMinimumWidth(222)
        self.connect(self.CalcSchlegelCk, QtCore.SIGNAL('clicked()'), self.CalcSchlegelPressed)
        #self.ShowSchlegelCk = QtGui.QCheckBox('Show')
        #self.connect(self.ShowSchlegelCk, QtCore.SIGNAL('clicked()'), self.ShowSchlegel)
        #row.addWidgets((self.CalcSchlegelCk,))#self.ShowSchlegelCk,))
        

        #row = self.SubOptionsWindows["CALCREN"].newRow()
        self.schlegelParamSB = DoubleSpinBox()
        self.schlegelParamSB.setValue(self.config.opts["SchlegelGamma"])
        self.schlegelParamSB.setMinimum(0)
        self.schlegelParamSB.setMaximum(5.0)
        self.schlegelParamSB.setDecimals(4)
        self.schlegelParamSB.setSingleStep(0.001)
        self.schlegelParamSB.setFixedWidth(50)
        self.schlegelCutoffSB = DoubleSpinBox()
        self.schlegelCutoffSB.setValue(self.config.opts["SchlegelCutoff"])
        self.schlegelCutoffSB.setMinimum(-100)
        self.schlegelCutoffSB.setMaximum(100)
        self.schlegelCutoffSB.setSingleStep(0.5)
        self.schlegelCutoffSB.setFixedWidth(50)
        
        #row.addWidgets((QtGui.QLabel("Gamma"),self.schlegelParamSB,QtGui.QLabel("Cutoff"),self.schlegelCutoffSB))
        self.connect(self.schlegelParamSB, QtCore.SIGNAL('valueChanged( double)'), self.SchlegelParamsChanged)
        self.connect(self.schlegelCutoffSB, QtCore.SIGNAL('valueChanged( double)'), self.SchlegelParamsChanged)
        
        self.GeneralCalcRenTable.insertRow(3)
        lab = QtGui.QTableWidgetItem("Schlegel")
        self.GeneralCalcRenTable.setItem(3,0,lab)
        self.GeneralCalcRenTable.setCellWidget(3,1,HolderWidget(self.CalcSchlegelCk))
        #self.GeneralCalcRenTable.setCellWidget(3,2,HolderWidget(self.ShowBondingPolygonsCk))
        self.GeneralCalcRenTable.setCellWidget(3,3,HolderWidget((QtGui.QLabel("G"),self.schlegelParamSB,
                                                                 QtGui.QLabel("r0"),self.schlegelCutoffSB)))
        
        
        self.ShowScreenInfoCk = QtGui.QCheckBox()
        self.ShowScreenInfoCk.setChecked(self.config.opts["ShowScreenInfo"])
        #self.CalcSchlegelCk.setMinimumWidth(222)
        self.connect(self.ShowScreenInfoCk, QtCore.SIGNAL('clicked()'), self.ShowScreenInfo)
        self.GeneralCalcRenTable.insertRow(4)
        lab = QtGui.QTableWidgetItem("Show Screen Info")
        self.GeneralCalcRenTable.setItem(4,0,lab)
        self.GeneralCalcRenTable.setCellWidget(4,1,HolderWidget(self.ShowScreenInfoCk))
        
        #sep = self.SubOptionsWindows["CALCREN"].addSeparator()
        #lb = self.SubOptionsWindows["CALCREN"].addHeader("EDIP")    
        #row = self.SubOptionsWindows["CALCREN"].newRow()
#        self.CalcEDIPCk = QtGui.QCheckBox()
#        self.CalcEDIPCk.setChecked(self.config.opts["CarbonMinimise)
#        #self.CalcEDIPCk.setMinimumWidth(222)
#        self.connect(self.CalcEDIPCk, QtCore.SIGNAL('clicked()'), self.CalcEDIPPressed)
        
        #self.ShowSchlegelCk = QtGui.QCheckBox('Show')
        #self.connect(self.ShowSchlegelCk, QtCore.SIGNAL('clicked()'), self.ShowSchlegel)
        #row.addWidgets((self.CalcEDIPCk,))#self.ShowSchlegelCk,))
#        
#        self.GeneralCalcRenTable.insertRow(4)
#        lab = QtGui.QTableWidgetItem("EDIP")
#        self.GeneralCalcRenTable.setItem(4,0,lab)
#        self.GeneralCalcRenTable.setCellWidget(4,1,HolderWidget(self.CalcEDIPCk))


        
        sep = self.SubOptionsWindows["CALCREN"].addSeparator()
        
        row = self.SubOptionsWindows["CALCREN"].newRow()
        self.UpdateDLBT = QtGui.QPushButton('Update Dual Lattice')
        self.UpdateCLBT = QtGui.QPushButton('Update Carbon Lattice')
        self.connect(self.UpdateDLBT, QtCore.SIGNAL('clicked()'), self.UpdateDualLattice)
        self.connect(self.UpdateCLBT, QtCore.SIGNAL('clicked()'), self.UpdateCarbonLattice)
        row.addWidgets((self.UpdateDLBT,self.UpdateCLBT))      
        
        
    def setupOutputWidgets(self):
        #sep = self.SubOptionsWindows["OUTPUT"].addSeparator(dummy=True)
        
        lb = self.SubOptionsWindows["OUTPUT"].addHeader("Output Options")
        
        #sep = self.SubOptionsWindows["OUTPUT"].addSeparator(dummy=True)
        
        row = self.SubOptionsWindows["OUTPUT"].newRow()
        self.OutputDirEntry = QtGui.QLineEdit()
        row.addWidgets((QtGui.QLabel("Directory:"),self.OutputDirEntry))
        
        row = self.SubOptionsWindows["OUTPUT"].newRow()
        self.BrowseToFolderBT = QtGui.QPushButton('Browse')
        self.connect(self.BrowseToFolderBT, QtCore.SIGNAL('clicked()'), self.browseToFolder)
        row.addWidgets((self.BrowseToFolderBT,))

        
        #row = self.SubOptionsWindows["OUTPUT"].newRow()
        #row = self.SubOptionsWindows["OUTPUT"].newRow()
        self.SaveLatticeBT = QtGui.QPushButton('Save Current Structure')
        self.connect(self.SaveLatticeBT, QtCore.SIGNAL('clicked()'), self.saveCurrentStructure)
        row.addWidgets((self.SaveLatticeBT,))
        
#        row = self.SubOptionsWindows["OUTPUT"].newRow()
#        self.SaveImagesCB = QtGui.QCheckBox('Save Images During Minimisation')
#        row.addWidgets((self.SaveImagesCB,))
        
        #sep = self.SubOptionsWindows["OUTPUT"].addSeparator()
        
#        lb = self.SubOptionsWindows["OUTPUT"].addHeader("Current Minimum")
#        
#        #sep = self.SubOptionsWindows["OUTPUT"].addSeparator(dummy=True)
#        
#        row = self.SubOptionsWindows["OUTPUT"].newRow()
#        self.ShowCurrentMinimumBT = QtGui.QPushButton('Show')
#        self.connect(self.ShowCurrentMinimumBT, QtCore.SIGNAL('clicked()'), self.ShowCurrentMinimum)
#        row.addWidgets((self.ShowCurrentMinimumBT,))
#        
#        sep = self.SubOptionsWindows["OUTPUT"].addSeparator()
#        
#        row = self.SubOptionsWindows["OUTPUT"].newRow()
#        self.ToggleScreenInfoCB = QtGui.QCheckBox('Show Screen Info')
#        self.connect(self.ToggleScreenInfoCB, QtCore.SIGNAL('clicked()'), self.ToggleScreenInfo)
#        row.addWidgets((self.ToggleScreenInfoCB,))
 
        
    def setupFullereneWidgets(self):
        #sep = self.SubOptionsWindows["GEN"].addSeparator(dummy=True)
        #self.FullereneWidgets.append(sep)
        lb = self.SubOptionsWindows["GEN"].addSeparator()
        self.FullereneWidgets.append(lb)
        
        row = self.SubOptionsWindows["GEN"].newRow(self)
        lb = QtGui.QLabel("Thomson Points")
        lb.setFixedWidth(140)
        self.FullereneDualLatticePointsEntry = SpinBox()
        self.FullereneDualLatticePointsEntry.setMaximum(9999999)
        self.FullereneDualLatticePointsEntry.setValue(100)
        self.FullereneDualLatticePointsEntry.setFixedWidth(60)
        row.addWidgets((lb,self.FullereneDualLatticePointsEntry))
        self.FullereneWidgets.append(row)
        row = self.SubOptionsWindows["GEN"].newRow(self)

        row = self.SubOptionsWindows["GEN"].newRow(self)
        lb = QtGui.QLabel("Carbon Atoms")
        lb.setFixedWidth(140)
        self.FullereneCarbonAtomsEntry = SpinBox()
        self.FullereneCarbonAtomsEntry.setMaximum(9999999)
        self.FullereneCarbonAtomsEntry.setValue(196)
        self.FullereneCarbonAtomsEntry.setFixedWidth(60)
        self.FullereneCarbonAtomsEntry.setSingleStep(2)
        row.addWidgets((lb,self.FullereneCarbonAtomsEntry))
        self.FullereneWidgets.append(lb)
        self.FullereneWidgets.append(row)
        
        self.connect(self.FullereneDualLatticePointsEntry, QtCore.SIGNAL('valueChanged(int)'), self.setFullereneDualLatticePoints)
        self.connect(self.FullereneCarbonAtomsEntry, QtCore.SIGNAL('valueChanged(int)'), self.setFullereneCarbonAtoms)

        #row = self.SubOptionsWindows["GEN"].newRow(self)
        #row.addWidgets((self.ShowCarbonAtomsCk,QtGui.QLabel(" Radius"),self.CarbonAtomRad,QtGui.QLabel("Col "),self.CarbonAtomColourBT))
        
        row = self.SubOptionsWindows["GEN"].newRow(self)
        lb = QtGui.QLabel("Seed")
        lb.setFixedWidth(100) 
        self.FullereneDualLatticeSeedEntry = SpinBox()
        self.FullereneDualLatticeSeedEntry.setMaximum(9999999)
        #self.DualLatticeSeedEntry.setFixedWidth(60)     
        self.FullereneDualLatticeRandomSeedCB = QtGui.QCheckBox("random")
        self.FullereneDualLatticeRandomSeedCB.setChecked(self.config.opts["FullereneUseRandomSeed"]) 
        self.connect(self.FullereneDualLatticeSeedEntry, QtCore.SIGNAL('valueChanged(int)'), self.setFullereneDualLatticeSeed) 
        self.connect(self.FullereneDualLatticeRandomSeedCB, QtCore.SIGNAL('stateChanged(int)'), self.setFullereneDualLatticeUseRandomSeed) 
        row.addWidgets((lb,self.FullereneDualLatticeSeedEntry,self.FullereneDualLatticeRandomSeedCB))        
        self.FullereneWidgets.append(row)
        
        row = self.SubOptionsWindows["GEN"].newRow(self)
        lb = QtGui.QLabel("NFixed Equator")
        lb.setFixedWidth(100) 
        self.FullereneDualLatticeNFixedEquator = SpinBox()
        self.FullereneDualLatticeNFixedEquator.setMaximum(9999999)
        #self.FullereneDualLatticeNFixedEquator.setFixedWidth(60)     
        self.FullereneDualLatticeFixPoleCB = QtGui.QCheckBox("Fix Pole")
        self.FullereneDualLatticeFixPoleCB.setChecked(self.config.opts["FullereneDualLatticeFixPole"]) 
        row.addWidgets((lb,self.FullereneDualLatticeNFixedEquator,self.FullereneDualLatticeFixPoleCB))    
        self.connect(self.FullereneDualLatticeNFixedEquator, QtCore.SIGNAL('valueChanged(int)'), self.setFullereneDualLatticeNFixedEquator)    
        self.connect(self.FullereneDualLatticeFixPoleCB, QtCore.SIGNAL('stateChanged(int)'), self.setFullereneDualLatticeFixPole)    

        self.FullereneWidgets.append(row)
        
        row = self.SubOptionsWindows["GEN"].newRow()
        self.GenerateFullereneBT = QtGui.QPushButton('Generate Random Points')
        self.connect(self.GenerateFullereneBT, QtCore.SIGNAL('clicked()'), self.ResetFullereneDualLatticePoints)
        row.addWidget(self.GenerateFullereneBT)        
        self.FullereneWidgets.append(row)
        
        sep = self.SubOptionsWindows["GEN"].addSeparator()
        self.FullereneWidgets.append(sep)
        
#        row = self.container.newRow()
#        self.TPForm = forms.GenericForm(self,title="Thomson Points",doNotShrink=False,isGroup=True,show=True)
#        #lb = QtGui.QLabel("Minimisation")
#        row.addWidgets((self.TPForm,))     
    
        row = self.SubOptionsWindows["GEN"].newRow()
        lb=QtGui.QLabel("Load Fullerene Dual Lattice Points from file")
        row.addWidgets((lb,))  
        self.FullereneWidgets.append(row)
        
        row = self.SubOptionsWindows["GEN"].newRow()
        self.FullereneDualLatticeFileEntry = QtGui.QLineEdit()
        row.addWidgets((self.FullereneDualLatticeFileEntry,))  
        self.FullereneWidgets.append(row)
        
        row = self.SubOptionsWindows["GEN"].newRow()
        self.BrowseBT = QtGui.QPushButton('Browse')
        #self.connect(self.BrowseBT, QtCore.SIGNAL('clicked()'), self.browseToFile)
        self.LoadBT = QtGui.QPushButton('Load')
        #self.connect(self.LoadBT, QtCore.SIGNAL('clicked()'), self.loadFullereneDualLattice)
        row.addWidgets((self.BrowseBT,self.LoadBT))        
        self.FullereneWidgets.append(row)
        #self.FullereneWidgets.append(self.LoadBT)
        
        sep = self.SubOptionsWindows["GEN"].addSeparator()
        self.FullereneWidgets.append(sep)
    
#    def getFullereneSeed(self):
#        if not self.config.opts["FullereneUseRandomSeed:
#            seed = int(self.FullereneDualLatticeSeedEntry.value())
#        else:
#            seed = random.randint(1,100000) 
#            self.FullereneDualLatticeSeedEntry.setValue(seed) 
#        return seed
    
    def setupNanotubeWidgets(self):
        #sep = self.SubOptionsWindows["GEN"].addSeparator(dummy=True)
        #self.NanotubeWidgets.append(sep)
                
        lb = self.SubOptionsWindows["GEN"].addHeader("Tube")
        self.NanotubeWidgets.append(lb)
        
        #sep = self.SubOptionsWindows["GEN"].addSeparator()
        #self.NanotubeWidgets.append(sep)
        
        row = self.SubOptionsWindows["GEN"].newRow(self)
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
        row.addWidgets((lb2,self.NanotubeNEntry,lb,self.NanotubeMEntry))#,lb3,self.NanotubeUEntry))
        self.connect(self.NanotubeMEntry, QtCore.SIGNAL('valueChanged(int)'), self.setNanotubeChirality)
        self.connect(self.NanotubeNEntry, QtCore.SIGNAL('valueChanged(int)'), self.setNanotubeChirality)
        self.connect(self.NanotubeUEntry, QtCore.SIGNAL('valueChanged(int)'), self.setNanotubeChirality)
        self.NanotubeWidgets.append(row)
        
        row = self.SubOptionsWindows["GEN"].newRow(self)
        lb = QtGui.QLabel("Nanotube Dual Lattice Points")
        lb.setFixedWidth(140)
        self.NanotubeTubeThomsonPointsEntry = SpinBox()
        self.NanotubeTubeThomsonPointsEntry.setValue(0)
        self.NanotubeTubeThomsonPointsEntry.setReadOnly(True)
        self.NanotubeTubeThomsonPointsEntry.setFixedWidth(60)
        self.NanotubeTubeThomsonPointsEntry.setMaximum(1000000)   
        self.connect(self.NanotubeTubeThomsonPointsEntry, QtCore.SIGNAL('valueChanged(int)'), self.setNanotubeTubeThomsonPoints)
        row.addWidgets((lb,self.NanotubeTubeThomsonPointsEntry))
        self.NanotubeWidgets.append(row)
        
        #row.addWidgets((self.ShowNanotubeTPCk,QtGui.QLabel("Radius"),self.TubeThomsonPointRad,QtGui.QLabel("Col "),self.TubeThomsonPointColourBT))
        #self.NanotubeWidgets.append(row)
        
        row = self.SubOptionsWindows["GEN"].newRow(self)
        lb = QtGui.QLabel("Nanotube Carbon Atoms")
        lb.setFixedWidth(140)
        self.NanotubeTubeCarbonAtomEntry = SpinBox()
        self.NanotubeTubeCarbonAtomEntry.setValue(0)
        self.NanotubeTubeCarbonAtomEntry.setFixedWidth(60)
        self.NanotubeTubeCarbonAtomEntry.setMaximum(1000000)   
        self.NanotubeTubeCarbonAtomEntry.setReadOnly(True)
        self.connect(self.NanotubeTubeCarbonAtomEntry, QtCore.SIGNAL('valueChanged(int)'), self.setNanotubeTubeCarbonAtoms)
        row.addWidgets((lb,self.NanotubeTubeCarbonAtomEntry))
        self.NanotubeWidgets.append(row)

        #row.addWidgets((self.ShowNanotubeCACk,QtGui.QLabel("Radius"),self.TubeCarbonAtomRad,QtGui.QLabel("Col "),self.TubeCarbonAtomColourBT))
        #self.NanotubeWidgets.append(row)
        
        row = self.SubOptionsWindows["GEN"].newRow()
        self.GenerateNanotubeBT = QtGui.QPushButton('Generate Nanotube')
        self.connect(self.GenerateNanotubeBT, QtCore.SIGNAL('clicked()'), self.ResetNanotube)
        row.addWidget(self.GenerateNanotubeBT)        
        self.NanotubeWidgets.append(row)        
        
        lb = self.SubOptionsWindows["GEN"].addHeader("Cap")
        self.NanotubeWidgets.append(lb)
        
        #sep = self.SubOptionsWindows["GEN"].addSeparator()
        #self.NanotubeWidgets.append(sep)
        
        row = self.SubOptionsWindows["GEN"].newRow(self)
        lb = QtGui.QLabel("Dual Lattice Points")
        lb.setFixedWidth(140)
        self.NanotubeCapThomsonPointsEntry = SpinBox()
        self.NanotubeCapThomsonPointsEntry.setValue(16)
        self.NanotubeCapThomsonPointsEntry.setMaximum(100000)
        self.NanotubeCapThomsonPointsEntry.setFixedWidth(60)
        row.addWidgets((lb,self.NanotubeCapThomsonPointsEntry))
        
        
        self.NanotubeWidgets.append(row)
        
        
        row = self.SubOptionsWindows["GEN"].newRow(self)
        lb = QtGui.QLabel("Carbon Atoms")
        lb.setFixedWidth(140)
        self.NanotubeCapCarbonAtomEntry = SpinBox()
        self.NanotubeCapCarbonAtomEntry.setValue(30)
        self.NanotubeCapCarbonAtomEntry.setMaximum(100000)
        self.NanotubeCapCarbonAtomEntry.setFixedWidth(60)
        row.addWidgets((lb,self.NanotubeCapCarbonAtomEntry))
        self.NanotubeWidgets.append(row)
        
        self.connect(self.NanotubeCapThomsonPointsEntry, QtCore.SIGNAL('valueChanged(  int )'), self.setNanotubeCapThomsonPoints)
        self.connect(self.NanotubeCapCarbonAtomEntry, QtCore.SIGNAL('valueChanged(  int )'), self.setNanotubeCapCarbonAtoms)
         
        row = self.SubOptionsWindows["GEN"].newRow(self)
        lb = QtGui.QLabel("Seed")
        lb.setFixedWidth(60) 
        self.NanotubeCapSeedEntry = SpinBox()
        self.NanotubeCapSeedEntry.setValue(0)
        self.NanotubeCapSeedEntry.setFixedWidth(80)
        self.NanotubeCapSeedEntry.setMaximum(1000000)     
        self.NanotubeRandomSeedCB = QtGui.QCheckBox("random")
        self.NanotubeRandomSeedCB.setChecked(self.config.opts["NanotubeCapUseRandomSeed"]) 
        row.addWidgets((lb,self.NanotubeCapSeedEntry,self.NanotubeRandomSeedCB))        
        self.connect(self.NanotubeCapSeedEntry, QtCore.SIGNAL('valueChanged(  int )'), self.setNanotubeCapSeed)
        self.connect(self.NanotubeRandomSeedCB, QtCore.SIGNAL('stateChanged ( int )'), self.setNanotubeUseRandomSeed)
        self.NanotubeWidgets.append(row) 
         
        
        row = self.SubOptionsWindows["GEN"].newRow()
        self.GenerateNanotubeCapBT = QtGui.QPushButton('Generate Random Cap')
        self.connect(self.GenerateNanotubeCapBT, QtCore.SIGNAL('clicked()'), self.ResetNanotubeCapDualLatticePoints)
        row.addWidget(self.GenerateNanotubeCapBT)        
        self.NanotubeWidgets.append(row)    
        
        
        lb = self.SubOptionsWindows["GEN"].addHeader("Full system")
        self.NanotubeWidgets.append(lb)
        
        
        row = self.SubOptionsWindows["GEN"].newRow(self)
        lb = QtGui.QLabel("Dual Lattice Points")
        lb.setFixedWidth(140)
        self.CappedNanotubeThomsonPointsEntry = SpinBox()
        self.CappedNanotubeThomsonPointsEntry.setMaximum(1000000) 
        self.CappedNanotubeThomsonPointsEntry.setValue(self.NanotubeCapThomsonPointsEntry.value()+self.NanotubeTubeThomsonPointsEntry.value())
        self.CappedNanotubeThomsonPointsEntry.setFixedWidth(60)
        self.CappedNanotubeThomsonPointsEntry.setReadOnly(True)
        self.connect(self.CappedNanotubeThomsonPointsEntry, QtCore.SIGNAL('valueChanged(  int )'), self.setCappedNanotubeThomsonPoints)
        row.addWidgets((lb,self.CappedNanotubeThomsonPointsEntry))
        self.NanotubeWidgets.append(row)

        
        row = self.SubOptionsWindows["GEN"].newRow(self)
        lb = QtGui.QLabel("Carbon Atoms")
        lb.setFixedWidth(140)
        self.CappedNanotubeCarbonAtomEntry = SpinBox()
        self.CappedNanotubeCarbonAtomEntry.setMaximum(1000000)
        self.CappedNanotubeCarbonAtomEntry.setValue(self.NanotubeCapCarbonAtomEntry.value() + self.NanotubeTubeCarbonAtomEntry.value())
        self.CappedNanotubeCarbonAtomEntry.setFixedWidth(60)
        self.connect(self.CappedNanotubeCarbonAtomEntry, QtCore.SIGNAL('valueChanged(  int )'), self.setCappedNanotubeCarbonAtoms)
        self.CappedNanotubeCarbonAtomEntry.setReadOnly(True)
         
        
        row = self.SubOptionsWindows["GEN"].newRow(self)
        row.addWidgets((lb,self.CappedNanotubeCarbonAtomEntry))
        self.NanotubeWidgets.append(row)
        
        lb = self.SubOptionsWindows["GEN"].addHeader("Uncapped length")
        self.NanotubeWidgets.append(lb)
        
        row = self.SubOptionsWindows["GEN"].newRow(self)
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
        
           