'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: July 12 2013
Copyright Marc Robinson 2013
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

Generic Toolbar class, 
Parent class to the basic/advanced toolbars

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
'''

from nanocap.core.globals import *
import os,sys,math,copy,random,time,types
from nanocap.core.globals import QT
QtGui, QtCore = QT.QtGui, QT.QtCore

import numpy

import nanocap.gui.forms as forms
from nanocap.gui.forms import *
import nanocap.core.processes as processes
from nanocap.gui.structurewindow import StructureWindow
from nanocap.core.util import *
        

class toolbar(QtGui.QWidget):   
    def __init__(self, Gui, MainWindow,Advanced=False):
        QtGui.QWidget.__init__(self, None)
        self.MainWindow = MainWindow
        self.Gui = Gui
        self.Processor = self.Gui.processor
        self.ThreadManager = self.Gui.threadManager
        self.SignalManager = self.Gui.signalManager
        self.VTKFrame = self.Gui.vtkframe
        self.ObjectActors = self.Gui.objectActors
        self.Operations = self.Gui.operations
        self.Advanced = Advanced
        self.config = self.Processor.config
        
        
        self.GUIlock = False
        
        self.containerLayout = QtGui.QVBoxLayout()
        self.containerLayout.setContentsMargins(0, 0, 0, 0)
        self.containerLayout.setSpacing(4)
        #self.container.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)
        self.setLayout(self.containerLayout)

        self.NanotubeWidgets = []
        self.FullereneWidgets = []
        
        self.connect(self.SignalManager, QtCore.SIGNAL("update_fullerene_structure_table()"), self.UpdateProgress)
        self.connect(self.SignalManager, QtCore.SIGNAL("update_nanotube_structure_table()"), self.UpdateProgress)
             
    def UpdateProgress(self):
        printh("updating progress")
        self.SearchProgressbar.setValue(self.Processor.minsearch.NUnique)   
        #self.SearchProgressbar.setText(str(self.Processor.minsearch.NUnique))

        self.show()

    def draw(self):
        #reimplement me please
        pass
  
  
    def saveCurrentStructure(self):
        self.Gui.saveCurrentStructure(folder = self.OutputDirEntry.text())
        
    
    def showStructureWindow(self):
        if(self.config.opts["GenType"]=="Fullerene"):    
            self.Gui.structureWindows["Fullerene"].scaleWindow()
            self.Gui.structureWindows["Fullerene"].show()
        if(self.config.opts["GenType"]=="Nanotube"):    
            self.Gui.structureWindows["Nanotube"].scaleWindow()
            self.Gui.structureWindows["Nanotube"].show()    
            
    def StopMinSearch(self):  
        self.GenFullerenceRB.setEnabled(True)
        self.GenNanotubeRB.setEnabled(True)
        self.StartMinSearchBT.show()
        self.StopMinSearchBT.hide() 
        self.SearchProgressbar.hide() 
        self.config.opts["StopMin"]=1
        printl(self.config.opts["StopMin"])
        #self.SignalManager.emitSignal(signal="update_structure_table()")
        
    def StopMin(self):  
        self.GenFullerenceRB.setEnabled(True)
        self.GenNanotubeRB.setEnabled(True)
        self.StartMinBT.show()
        self.StopMinBT.hide() 
        self.config.opts["StopMin"]=1
        printl(self.config.opts["StopMin"])
        #self.SignalManager.emitSignal(signal="update_structure_table()")
    
    def MinimaSearch(self):
        self.StartMinSearchBT.hide()
        self.StopMinSearchBT.show() 
        self.SearchProgressbar.show()
        self.SearchProgressbar.setValue(0) 
        self.SearchProgressbar.setMaximum(self.config.opts["NMinima"])
        #self.Processor.minimiser.stopmin=0 
        self.config.opts["StopMin"]=0  
        #self.Gui.submitUpdatePointSet(self.Processor.thomsonPoints)
        self.ThreadManager.submit_to_queue(self.Processor.minimaSearch)
        self.ThreadManager.submit_to_queue(self.StopMinSearch)
        #self.ThreadManager.submit_to_queue(self.UpdateAll,emit = "update_structure_table")
    
    def MinimiseThomsonPoints(self):
        self.StartMinBT.hide()
        self.StopMinBT.show() 
        #self.Processor.minimiser.stopmin=0 
        self.config.opts["StopMin"]=0  
        #self.Gui.submitUpdatePointSet(self.Processor.thomsonPoints)
        printl("StopMin",self.config.opts["StopMin"])
        self.ThreadManager.submit_to_queue(self.Processor.minimiseDualLattice)
        #self.ThreadManager.submit_to_queue(self.Processor.addCurrentStructure)
        self.ThreadManager.submit_to_queue(self.StopMin)
        #self.ThreadManager.submit_to_queue(self.UpdateAll,emit = "update_structure_table")
        #self.ThreadManager.submit_to_queue(self.null,emit = "update_structure_table")
        
        #while(self.config.opts["StopMin==0):pass
        #self.updateGUIStructureTable()
    
    def null(self):
        pass
    
    def MinimiseCarbonAtoms(self):
        self.StartMinCarbonBT.hide()
        self.StopMinCarbonBT.show() 
        self.Processor.minimiser.stopcarbonmin=0  
        self.config.opts["StopMin"]=0 
        #self.Gui.submitUpdatePointSet(self.Processor.thomsonPoints)
        self.ThreadManager.submit_to_queue(self.Processor.minimiseCarbonAtoms)
        self.ThreadManager.submit_to_queue(self.StopMinCarbon)
        #self.ThreadManager.submit_to_queue(self.UpdateCarbonLattice,emit = "update_structure_table")
        
    
    def StopMinCarbon(self):  
        try:
            self.StartMinCarbonBT.show()
            self.StopMinCarbonBT.hide() 
        except:
            pass
        self.GenFullerenceRB.setEnabled(True)
        self.GenNanotubeRB.setEnabled(True)
        
        self.Processor.minimiser.stopcarbonmin=1        
        #self.SignalManager.emitSignal(signal="update_structure_table()")
    
    def getFullereneSeed(self):
        printl("getting seed",self.config.opts["FullereneUseRandomSeed"],self.config.opts["FullereneRandomSeed"])
        if not self.config.opts["FullereneUseRandomSeed"]:
            seed = self.config.opts["FullereneRandomSeed"]
        else:
            seed = random.randint(1,100000) 
            if(self.Advanced):self.FullereneDualLatticeSeedEntry.setValue(seed) 
            else:self.DualLatticeSeedEntry.setValue(seed) 
            self.config.opts["FullereneRandomSeed"] = seed
        return seed
    
    def getNanotubeCapSeed(self):
        printl("getNanotubeCapSeed",self.config.opts["NanotubeCapUseRandomSeed"])
        if not self.config.opts["NanotubeCapUseRandomSeed"]:
            seed = self.config.opts["NanotubeCapRandomSeed"]
        else:
            seed = random.randint(1,100000) 
            if(self.Advanced):self.NanotubeCapSeedEntry.setValue(seed) 
            else:self.DualLatticeSeedEntry.setValue(seed) 
            self.config.opts["NanotubeCapRandomSeed"] = seed
        return seed
        
    def ResetFullereneDualLatticePoints(self):
        self.VTKFrame.rotateCameraFlag=False
        self.ObjectActors.removeAllActors()
        seed = self.getFullereneSeed()          
        self.Processor.resetFullereneDualLattice(seed=seed)
        
        self.ObjectActors.FullereneDualLatticePoints.initArrays(self.Processor.fullerene.thomsonPoints)
        self.ObjectActors.FullereneDualLatticePoints.update()
        self.Operations.ToggleFullereneDualLatticePoints()
        self.VTKFrame.resetCamera()
        
        
    def ResetNanotube(self):
        printl("resetting nanotube",self.config.opts["EstimateCapPoints"])
        self.ObjectActors.removeAllActors()
        self.Processor.resetNanotube(self.config.opts["NanotubeChiralityN"],
                                     self.config.opts["NanotubeChiralityM"],
                                     l=self.config.opts["NanotubeLength"],
                                     capEstimate = self.config.opts["EstimateCapPoints"])
        
        self.NanotubeTubeThomsonPointsEntry.setValue(self.Processor.nanotube.tubeThomsonPoints.npoints)
        self.NanotubeTubeCarbonAtomEntry.setValue(self.Processor.nanotube.tubeCarbonAtoms.npoints)
        
        self.NanotubeCapThomsonPointsEntry.setValue(self.config.opts["NCapDualLatticePoints"])
        self.NanotubeCapCarbonAtomEntry.setValue(self.config.opts["NCapCarbonAtoms"])
        
        self.NanotubeForceCutoffChanged(self.Processor.nanotube.cutoff)
        
        self.NanotubeLengthEntry.setValue(self.Processor.nanotube.length)
        printl("setting minimum",int(self.Processor.nanotube.minimumLength*100))
        self.NanotubeLengthSlider.setMinimum(int(self.Processor.nanotube.minimumLength)*100)
        self.NanotubeLengthEntry.setMinimum(self.Processor.nanotube.minimumLength)
            
        self.ObjectActors.NanotubeTubeDualLatticePoints.initArrays(self.Processor.nanotube.tubeThomsonPoints)
        self.ObjectActors.NanotubeTubeDualLatticePoints.update()
        
        self.ObjectActors.NanotubeTubeCarbonAtomsPoints.initArrays(self.Processor.nanotube.tubeCarbonAtoms)
        self.ObjectActors.NanotubeTubeCarbonAtomsPoints.update()
        
        self.Operations.ToggleTubeDualLatticePoints()
        self.VTKFrame.resetCamera()
        
    def ResetNanotubeCapDualLatticePoints(self):
        printl("Reset Nanotube Cap Thomson points")
        self.VTKFrame.rotateCameraFlag=False
        
        self.ObjectActors.removePointSetFromRenderer(self.ObjectActors.CappedNanotubeTubeDualLatticePoints)
        try:
            self.ObjectActors.removePointSetFromRenderer(self.ObjectActors.CapDualLatticePoints)
            self.ObjectActors.removePointSetFromRenderer(self.ObjectActors.ReflectedCapDualLatticePoints)
        except:pass
        
        
        seed = self.getNanotubeCapSeed()
        self.Processor.resetCap(seed=seed)
        
        self.NanotubeCapThomsonPointsEntry.setValue(self.Processor.cap.thomsonPoints.npoints)
        NcCap = self.Processor.cap.thomsonPoints.npoints*2 - 2
        self.NanotubeCapCarbonAtomEntry.setValue(NcCap)
        
        tNt = 2*self.Processor.cap.thomsonPoints.npoints + self.Processor.nanotube.tubeThomsonPoints.npoints
        tNc = 2*NcCap + self.Processor.nanotube.tubeCarbonAtoms.npoints
        
        self.CappedNanotubeThomsonPointsEntry.setValue(tNt)
        self.CappedNanotubeCarbonAtomEntry.setValue(tNc)
        
        self.ObjectActors.CappedNanotubeTubeDualLatticePoints.initArrays(self.Processor.nanotube.cappedTubeThomsonPoints)
        self.ObjectActors.CappedNanotubeTubeDualLatticePoints.update()
        
        self.ObjectActors.CapDualLatticePoints.initArrays(self.Processor.cap.thomsonPoints)
        self.ObjectActors.CapDualLatticePoints.update()
        
        self.ObjectActors.ReflectedCapDualLatticePoints.initArrays(self.Processor.reflectedCap.thomsonPoints)
        self.ObjectActors.ReflectedCapDualLatticePoints.update()
        
        self.Operations.ToggleTubeDualLatticePoints()
        self.Operations.ToggleCappedTubeDualLatticePoints()
        self.Operations.ToggleCapDualLatticePoints()
        #self.Operations.ToggleCappedTubeCarbonAtoms()
        self.VTKFrame.resetCamera()
    
    def UpdateAll(self):
        if(self.config.opts["CarbonMinimise"]):
            self.Processor.updateCarbonLattice()
        else:
            self.Processor.updateDualLattice()
        self.RenderUpdate()
    
    def UpdateDualLattice(self):
        self.Processor.updateDualLattice()
        #self.RenderUpdate()
        
    def UpdateCarbonLattice(self):        
        self.Processor.updateCarbonLattice()
        #self.RenderUpdate()
    
    def StructureWindowUpdateEmit(self,*args):
        waitGUIlock()         
        #self.emit(QtCore.SIGNAL("update_structure_table()"))    
        printl("emit update_structure_table()") 
        waitGUIlock() 
    
    def StructureWindowUpdate(self,*args): 
        return
        waitGUIlock()       
        self.config.opts["GUIlock"] = True
        self.Gui.structureWindows["Fullerene"].updateStructureTable()
        self.config.opts["GUIlock"] = False
        
        waitGUIlock()
        self.config.opts["GUIlock"] = True 
        self.Gui.structureWindows["Nanotube"].updateStructureTable()
        self.config.opts["GUIlock"] = False
        
        
    def RenderUpdate(self,*args): 
        self.Operations.RenderUpdate()
    
    def BondThicknessChanged(self,val):
        self.config.opts["CarbonBondThickness"] = float(self.bondThicknessEntry.text())
        self.ObjectActors.carbonBonds.setBondThickness(val)
        self.VTKFrame.refreshWindow()  
        #self.Processor.changeBondThickness(self.config.opts["CarbonBondThickness)
    
    def SetCarbonMinimise(self):
        if(self.CarbonMinimiseCk.isChecked()):
            self.config.opts["CarbonMinimise"]=True
        else:
            self.config.opts["CarbonMinimise"]=False
            
    def ShowCarbonRings(self):
        if(self.ShowBondingPolygonsCk.isChecked()==True):
            if(self.Advanced):self.CalcBondingPolygonsCk.setChecked(True)
            self.config.opts["ShowCarbonRings"] = True
            #self.Processor.addBondingPolygons()
        else:
            self.config.opts["ShowCarbonRings"] = False
            #self.Processor.removeBondingPolygons()    
        
        printl("ShowCarbonRings",self.config.opts["ShowCarbonRings"])    
        if(self.Advanced):self.UpdateCheckboxes()
        self.Operations.ToggleCarbonRings()
        
    def ShowCarbonBonds(self):
        if(self.ShowCarbonBondsCk.isChecked()==True):
            if(self.Advanced):self.CalcCarbonBondsCk.setChecked(True)
            self.config.opts["ShowCarbonBonds"]=True
            #self.Processor.addCarbonBonds()
        else:
            self.config.opts["ShowCarbonBonds"]=False
            #self.Processor.removeCarbonBonds()
        if(self.Advanced):self.UpdateCheckboxes()
        self.Operations.ToggleCarbonBonds()
    
    def ShowScreenInfo(self):
        if(self.ShowScreenInfoCk.isChecked()==True):
            self.config.opts["ShowScreenInfo"]=True
            #self.Processor.addTriangles()
        else:
            self.config.opts["ShowScreenInfo"]=False
            #self.Processor.removeTriangles()
        self.Operations.ToggleScreenInfo()
        
    def ShowTriangles(self):
        if(self.ShowTriCk.isChecked()==True):
            if(self.Advanced):self.CalcTriCk.setChecked(True)
            self.config.opts["ShowTriangulation"]=True
            #self.Processor.addTriangles()
        else:
            self.config.opts["ShowTriangulation"]=False
            #self.Processor.removeTriangles()
        if(self.Advanced):self.UpdateCheckboxes()
        self.Operations.ToggleTriangulation()
    
    def ShowFullereneDualLatticePoints(self):
        if(self.ShowFullereneDualLatticePointsCk.isChecked()):
            self.config.opts["ShowFullereneDualLatticePoints"] = True
            #self.Processor.addFullereneDualLatticePoints() 
        else:
            #self.Processor.removeFullereneDualLatticePoints()
            self.config.opts["ShowFullereneDualLatticePoints"] = False
        self.Operations.ToggleFullereneDualLatticePoints()
    
    def ShowFullereneCarbonAtoms(self):
        if(self.ShowFullereneCarbonAtomsCk.isChecked()):
            self.config.opts["ShowFullereneCarbonAtoms"] = True
            #self.Processor.addFullereneCarbonAtoms() 
        else:
            #self.Processor.removeFullereneCarbonAtoms()
            self.config.opts["ShowFullereneCarbonAtoms"] = False
            
        if(self.Advanced):self.UpdateCheckboxes()
        self.Operations.ToggleFullereneCarbonAtoms()
    
    def ShowCappedTubeCarbonAtoms(self):
        if(self.ShowCappedTubeCarbonAtomsCk.isChecked()==True):
            if(self.Advanced):
                self.CalcCappedTubeCarbonAtomsCk.setChecked(True)
                
            self.config.opts["ShowCappedTubeCarbonAtoms"]=True
            #self.Processor.addCappedTubeCarbonAtoms()
        else:
            self.config.opts["ShowCappedTubeCarbonAtoms"]=False
            #self.Processor.removeCappedTubeCarbonAtoms()
        if(self.Advanced):self.UpdateCheckboxes()    
        self.Operations.ToggleCappedTubeCarbonAtoms()
            
    def ShowTubeDualLatticePoints(self):
        if(self.ShowTubeDualLatticePointsCk.isChecked()):
            self.config.opts["ShowTubeDualLatticePoints"] = True
            #self.Processor.addNanotubeDualLatticePoints() 
        else:
            #self.Processor.removeNanotubeDualLatticePoints() 
            self.config.opts["ShowTubeDualLatticePoints"] = False
        self.Operations.ToggleTubeDualLatticePoints()
        
    def ShowCappedTubeDualLatticePoints(self):
        if(self.ShowCappedTubeDualLatticePointsCB.isChecked()):
            self.config.opts["ShowCappedTubeDualLatticePoints"] = True
            #self.Processor.addCappedTubeThomsonPoints() 
        else:
            #self.Processor.removeCappedTubeThomsonPoints() 
            self.config.opts["ShowCappedTubeDualLatticePoints"] = False
        self.Operations.ToggleCappedTubeDualLatticePoints()
            
    def ShowCapDualLatticePoints(self):
        if(self.ShowCapDualLatticePointsCB.isChecked()):
            self.config.opts["ShowCapDualLatticePoints"] = True
        else:
            self.config.opts["ShowCapDualLatticePoints"] = False
        
        self.Operations.ToggleCapDualLatticePoints()

    def ShowTubeCarbonAtoms(self):
        if(self.ShowTubeCarbonAtomsCk.isChecked()):
            self.config.opts["ShowTubeCarbonAtoms"] = True
        else:
            self.config.opts["ShowTubeCarbonAtoms"] = False
            
        self.Operations.ToggleNanotubeCarbonAtoms()  
    

    
    def ShowLabels(self):
        self.config.opts["ShowCappedTubeCarbonAtomsLabels"] = True if self.ShowCappedTubeCarbonAtomsLabelsCk.isChecked() else False
        self.config.opts["ShowCappedTubeDualLatticePointsLabels"] = True if self.ShowCappedTubeDualLatticeLabelsCk.isChecked() else False
        self.config.opts["ShowCapDualLatticePointsLabels"] = True if self.ShowCapDualLatticeLabelsCk.isChecked() else False
        self.config.opts["ShowFullereneCarbonAtomsLabels"] = True if self.ShowFullereneCarbonAtomsLabelsCk.isChecked() else False
        self.config.opts["ShowFullereneDualLatticePointsLabels"] = True if self.ShowFullereneDualLatticeLabelsCk.isChecked() else False
        self.config.opts["ShowTubeDualLatticePointsLabels"] = True if self.ShowTubeDualLatticeLabelsCk.isChecked() else False
        self.config.opts["ShowTubeCarbonAtomsLabels"] = True if self.ShowTubeCarbonAtomsLabelsCk.isChecked() else False  
        self.Operations.ToggleLabels()
    
    def ShowBoundingBoxes(self):
        self.config.opts["ShowFullereneDualLatticePointsBox"] = True if self.ShowFullereneDualLatticeBoxCk.isChecked() else False
        self.config.opts["ShowFullereneCarbonAtomsBox"] = True if self.ShowFullereneCarbonAtomsBoxCk.isChecked() else False
        
        
        self.config.opts["ShowCapDualLatticePointsBox"] = True if self.ShowCapDualLatticeBoxCk.isChecked() else False
        self.config.opts["ShowCappedTubeDualLatticePointsBox"] = True if self.ShowCappedTubeDualLatticeBoxCk.isChecked() else False
        self.config.opts["ShowTubeDualLatticePointsBox"] = True if self.ShowTubeDualLatticeBoxCk.isChecked() else False
        self.config.opts["ShowCappedTubeCarbonAtomsBox"] = True if self.ShowCappedTubeCarbonAtomsBoxCk.isChecked() else False
        self.config.opts["ShowTubeCarbonAtomsBox = True"] if self.ShowTubeCarbonAtomsBoxCk.isChecked() else False  
        self.Operations.ToggleBoundingBoxes()

    def setFullereneDualLatticeUseRandomSeed(self,val):
        self.config.opts["FullereneUseRandomSeed"]=val
        #True if self.FullereneDualLatticeRandomSeedCB.isChecked() else False
   
    def setFullereneDualLatticeSeed(self,val):
        self.config.opts["FullereneRandomSeed"] = val            
    
    def setCappedNanotubeCarbonAtoms(self,val):
        self.config.opts["NCappedTubeCarbonAtoms"] = val
    
    def setCappedNanotubeThomsonPoints(self,val):
        self.config.opts["NCappedTubeDualLatticePoints"] = val
    
    def setNanotubeUseRandomSeed(self,val):
        self.config.opts["NanotubeCapUseRandomSeed"]=val
    
    def setNanotubeCapSeed(self,val):
        self.config.opts["NanotubeCapRandomSeed"] = val        
    
    def ResetGaussians(self):
        self.Processor.minsearch.reset()
    
    def AddGaussian(self):            
        if(self.config.opts["GenType"]=="Fullerene"):
            self.Processor.minsearch.addGaussian(self.Processor.fullerene.thomsonPoints)    
        if(self.config.opts["GenType"]=="Nanotube"):
            self.Processor.minsearch.addGaussian(self.Processor.nanotube.cappedTubeThomsonPoints) 
    
    def setAddGaussians(self):
        if(self.AddGaussiansCk.isChecked()):
            self.config.opts["AddGaussians"] = True
        else:
            self.config.opts["AddGaussians"] = False

            
    def setGaussianWidth(self,val):
        self.config.opts["GaussianWidth"] = val
        
    def setGaussianHeight(self,val):
        self.config.opts["GaussianHeight"] = val    
        
    def GenTypeChanged(self):
        if(self.GenFullerenceRB.isChecked()==True):
            self.config.opts["GenType"]="Fullerene"
            for widget in self.NanotubeWidgets:
                widget.hide()
            for widget in self.FullereneWidgets:
                widget.show()    
                
        else:
            self.config.opts["GenType"]="Nanotube"
            for widget in self.NanotubeWidgets:
                widget.show()
            for widget in self.FullereneWidgets:
                widget.hide()       
        printl("GenType",self.config.opts["GenType"])
    
        
    def setResetPerIteration(self):
        if(self.ResetLoopCK.isChecked()):
            self.config.opts["ResetPerIteration"]=True
        else:
            self.config.opts["ResetPerIteration"]=False
    def setPerturbationPerIteration(self):
        if(self.PerturbLoopCK.isChecked()):
            self.config.opts["RandomPertubationPerIteration"]=True
        else:
            self.config.opts["RandomPertubationPerIteration"]=False                
    
    def setBasinClimbing(self):
        if(self.BasinClimbCK.isChecked()):
            self.config.opts["BasinClimb"]=True
        else:
            self.config.opts["BasinClimb"]=False   
        
    def setNMinima(self,val):
        self.config.opts["NMinima"]=val
        
    def setNMaxMinima(self,val):
        self.config.opts["NMaxMinima"]=val    
    
    
    def NanotubeLengthSliderPressed(self):
        #self.ObjectActors.addNanotubeCutoffPlane(self.Processor.nanotube.cutoff)
        pass
        
    def NanotubeLengthSliderReleased(self):    
        #self.ObjectActors.removeNanotubeCutoffPlane()
        pass
        
    def NanotubeLengthSliderChanged(self,val):
        cutoff = float(val)/100.0
        self.NanotubeLengthEntry.setValue(cutoff)
        #self.Processor.nanotube.cutoff = cutoff 
    
    def NanotubeForceSliderPressed(self):
        self.ObjectActors.addNanotubeCutoffPlane(self.Processor.nanotube.cutoff)
        
    def NanotubeForceSliderReleased(self):    
        self.ObjectActors.removeNanotubeCutoffPlane()
        
    def NanotubeForceSliderChanged(self,val):
        cutoff = float(val)/100.0
        self.NanotubeForceCutoff.setValue(cutoff)
        self.Processor.nanotube.cutoff = cutoff 
    
    
    def setAutoNanotubeZCutoff(self):
        self.config.opts["AutoNanotubeZCutoff"]=True if self.autoCutoffCB.isChecked() else False
        if self.autoCutoffCB.isChecked():
            self.NanotubeForceCutoffSlider.setDisabled(True)
            self.NanotubeForceCutoff.setDisabled(True)
            self.Processor.nanotube.setZcutoff(self.config.opts["NCapDualLatticePoints"])
            try:
                self.NanotubeForceCutoffSlider.setValue(self.Processor.nanotube.cutoff*100)
                self.NanotubeForceCutoff.setValue(self.Processor.nanotube.cutoff)
            except:pass
            
            self.ObjectActors.moveNanotubeCutoffPlane(self.Processor.nanotube.cutoff)
            
        else:
            self.NanotubeForceCutoffSlider.setDisabled(False)
            self.NanotubeForceCutoff.setDisabled(False)
                       
    def NanotubeForceCutoffChanged(self,val):
        try:self.NanotubeForceCutoffSlider.setValue(val*100)
        except:pass
        self.ObjectActors.moveNanotubeCutoffPlane(val)
        self.Processor.nanotube.cutoff = val 
        self.config.opts["NanotubeZCutoff"] = val
    
        
    def setNanotubeTubeThomsonPoints(self,val):
        self.config.opts["NTubeDualLatticePoints"] = val
        self.config.opts["NCappedTubeDualLatticePoints"] = int(2*self.config.opts["NCapDualLatticePoints"] + val)
        self.CappedNanotubeThomsonPointsEntry.setValue(self.config.opts["NCappedTubeDualLatticePoints"])
    
    def setNanotubeTubeCarbonAtoms(self,val):
        self.config.opts["NTubeCarbonAtoms"] = val
        self.config.opts["NCappedTubeCarbonAtoms"] = int(2*self.config.opts["NCapCarbonAtoms"] + val)
        self.CappedNanotubeCarbonAtomEntry.setValue(self.config.opts["NCappedTubeCarbonAtoms"])
        
    def setNanotubeCapThomsonPoints(self,var):
        printl("Nanotube Cap Thomson points changed")
        self.NanotubeCapThomsonPointsEntry.setValue(var)
        Nc = 2.0*float(var) - 2
        self.NanotubeCapCarbonAtomEntry.setValue(int(Nc))
        
        self.config.opts["NCapDualLatticePoints"]=int(var)
        self.config.opts["NCappedTubeDualLatticePoints"] = int(2*var + self.config.opts["NTubeDualLatticePoints"])
        self.CappedNanotubeThomsonPointsEntry.setValue(self.config.opts["NCappedTubeDualLatticePoints"])
        
    def setNanotubeCapCarbonAtoms(self,var):  
        printl("Nanotube Cap carbon atoms changed")
        self.NanotubeCapCarbonAtomEntry.setValue(var)
        Nt = (float(var) + 2)/2.0 
        self.NanotubeCapThomsonPointsEntry.setValue(int(Nt)) 
        
        self.config.opts["NCapCarbonAtoms"] = int(var)
        self.config.opts["NCappedTubeCarbonAtoms"]  = int(2*var + self.config.opts["NTubeCarbonAtoms"])
        self.CappedNanotubeCarbonAtomEntry.setValue(self.config.opts["NCappedTubeCarbonAtoms"])
        
    
    def browseToFolder(self):
        fdiag = QtGui.QFileDialog()
        self.outputfolder = fdiag.getExistingDirectory()
        self.OutputDirEntry.setText(self.outputfolder)
    
    def CalcSchlegelPressed(self):
        if(self.CalcSchlegelCk.isChecked()):
            self.config.opts["CalcSchlegel"]=True
        else:
            self.config.opts["CalcSchlegel"]=False
        
        self.UpdateCheckboxes()
    
    def SchlegelParamsChanged(self,val):
        self.config.opts["SchlegelCutoff"] = self.schlegelCutoffSB.value()
        self.config.opts["SchlegelGamma"] = self.schlegelParamSB.value()
 
    def setNanotubeChirality(self,val):
        self.config.opts["NanotubeChiralityN"] = self.NanotubeNEntry.value()
        self.config.opts["NanotubeChiralityM"] = self.NanotubeMEntry.value()
        self.config.opts["NanotubeChiralityU"] = self.NanotubeUEntry.value()
    
    def setNanotubeLength(self,val):
        try:self.NanotubeLengthSlider.setValue(val*100)
        except:pass
        self.config.opts["NanotubeLength"] = self.NanotubeLengthEntry.value()
        printl("NanotubeLength",self.config.opts["NanotubeLength"])
        
    def changeUpdateFreq(self,val):
        self.config.opts["RenderUpdate"] = val
    
    def changeMinSteps(self,val):
        self.config.opts["MinSteps"] = val
    
    def changeMinTol(self,val):
        self.config.opts["MinTol"] = float(val)
        
    def changeMinType(self,val):
        self.config.opts["MinType"] = val
    
    
    def setMinStopIP(self):
        if(self.IPstopCk.isChecked()):
            self.config.opts["StopCriteriaIP"] = True
        else:
            self.config.opts["StopCriteriaIP"] = False
    
    def setMinStopPentsOnly(self):
        if(self.PentsOnlyCK.isChecked()):
            self.config.opts["StopCriteriaPentsOnly"] = True
        else:
            self.config.opts["StopCriteriaPentsOnly"] = False
            
    def setFullereneDualLatticePoints(self,val):
        self.config.opts["NFullereneDualLatticePoints"] = val
        Nc = int(2.0*float(self.config.opts["NFullereneDualLatticePoints"]) - 4)
        self.config.opts["NFullereneCarbonAtoms"] = Nc
        self.FullereneCarbonAtomsEntry.setValue(Nc)
        
    def setFullereneCarbonAtoms(self,val):
        self.config.opts["NFullereneCarbonAtoms"] = val
        Nt = int((float(self.config.opts["NFullereneCarbonAtoms"]) + 4)/2.0)
        self.config.opts["NFullereneDualLatticePoints"] = Nt
        self.FullereneDualLatticePointsEntry.setValue(Nt)

    def setFullereneDualLatticeNFixedEquator(self,val):
        self.config.opts["FullereneDualLatticeNFixedEquator"]= val
        printl("setting FullereneDualLatticeNFixedEquator",val,self.config.opts["FullereneDualLatticeNFixedEquator"])
        
    def setFullereneDualLatticeFixPole(self,val):
        self.config.opts["FullereneDualLatticeFixPole"] = False if val==0 else True
        printl("setting FullereneDualLatticeFixPole",val,self.config.opts["FullereneDualLatticeFixPole"])
    
    def UpdateCheckboxes(self):
        if(self.ShowBondingPolygonsCk.isChecked()):
            self.config.opts["ShowCarbonRings"] = True
            self.CalcBondingPolygonsCk.setChecked(True)
        else:
            self.config.opts["ShowCarbonRings"] = False
                
        if(self.ShowCarbonBondsCk.isChecked()):
            self.config.opts["ShowCarbonBonds"]=True
            self.CalcCarbonBondsCk.setChecked(True)
        else:
            self.config.opts["ShowCarbonBonds"] = False
                
        if(self.ShowTriCk.isChecked()):
            self.config.opts["ShowTriangulation"] = True
            self.CalcTriCk.setChecked(True)
        else:
            self.config.opts["ShowTriangulation"] = False   
             
        if(self.ShowFullereneCarbonAtomsCk.isChecked()):
            self.config.opts["ShowFullereneCarbonAtoms"] = True
            self.CalcFullereneCarbonAtomsCk.setChecked(True)
        else:
            self.config.opts["ShowFullereneCarbonAtoms"] = False    
        
        if(self.ShowCappedTubeCarbonAtomsCk.isChecked()):
            self.config.opts["ShowCappedTubeCarbonAtoms"] = True
            self.CalcCappedTubeCarbonAtomsCk.setChecked(True)
        else:
            self.config.opts["ShowCappedTubeCarbonAtoms"] = False    
        
        
        if(self.CarbonMinimiseCk.isChecked()):
            self.CalcFullereneCarbonAtomsCk.setChecked(True)
            self.CalcCappedTubeCarbonAtomsCk.setChecked(True)
                
        if(self.CalcBondingPolygonsCk.isChecked()):
            self.CalcFullereneCarbonAtomsCk.setChecked(True)
            self.CalcCappedTubeCarbonAtomsCk.setChecked(True)
            self.CalcTriCk.setChecked(True)
            self.CalcCarbonBondsCk.setChecked(True)
            self.config.opts["CalcCarbonRings"] = True  
        else:
            self.config.opts["CalcCarbonRings"] = False   
             
        if(self.CalcCarbonBondsCk.isChecked()):
            self.CalcFullereneCarbonAtomsCk.setChecked(True)
            self.CalcCappedTubeCarbonAtomsCk.setChecked(True)
            self.CalcTriCk.setChecked(True)
            self.config.opts["CalcCarbonBonds"] = True
        else:
            self.config.opts["CalcCarbonBonds"] = False
        
        if(self.config.opts["GenType"]=="Fullerene"):       
            if(self.CalcFullereneCarbonAtomsCk.isChecked()):
                self.CalcTriCk.setChecked(True)
                self.config.opts["CalcFullereneCarbonAtoms"]=True
            else:
                self.config.opts["CalcFullereneCarbonAtoms"] = False
        
        if(self.config.opts["GenType"]=="Nanotube"):    
            if(self.CalcCappedTubeCarbonAtomsCk.isChecked()):
                self.CalcTriCk.setChecked(True)
                self.config.opts["CalcCappedTubeCarbonAtoms"]=True
            else:
                self.config.opts["CalcCappedTubeCarbonAtoms"] = False
            
        if(self.CalcTriCk.isChecked()):   
            self.config.opts["CalcTriangulation"] = True
        else:
            self.config.opts["CalcTriangulation"] = False
        
        printl("ShowTriangulation",self.config.opts["ShowTriangulation"])    
        
    def ToggleNanotubeDamping(self):
        if(self.NanotubeDampingCB.isChecked()):
            self.config.opts["NanotubeDamping"]=True
        else:
            self.config.opts["NanotubeDamping"]=False
        self.config.opts["NanotubeDampingCutoff"] = self.NanotubeDampingCutoff.value()
        self.Processor.nanotubeDampingCutoffChanged(self.config.opts["NanotubeDampingCutoff"])
        
    def NanotubeDampingCutoffChanged(self,val):
        self.Processor.nanotubeDampingCutoffChanged(val)
        self.config.opts["NanotubeDampingCutoff"] = val
        
    def NanotubeDampingConstantChanged(self,val):
        self.Processor.nanotubeDampingConstantChanged(val) 
        self.config.opts["NanotubeDampingConstant"] = val
        
                
    #+#+#+#+#+#+#+#+#+#+
#    def loadThomsonPoints(self):
#        npoints = sum(1 for line in open(self.file))-3
#        
#        points = numpy.zeros(npoints*3,NPF)
#        printl("Loading file",self.file,npoints)
#        f = open(self.file,"r")
#        f.readline()
#        f.readline()
#        f.readline()
#        for i in range(0,npoints):
#            array = f.readline().split()
#            for d in range(0,3):
#                points[i*3 + d] = float(array[d])
#            print i,points[i*3 + 0],points[i*3 + 1],points[i*3 + 2]
#            
#        self.StopRotate()
#        self.ThomsonPointsEntry.setText(str(npoints))
#        Nc = 2.0*float(npoints) - 4
#        self.CarbonAtomEntry.setText(str(int(Nc)))
#        self.Processor.resetFullereneThomsonPoints(inputpoints=points)
#    def loadFullereneDualLattice(self):
#        pass      
#    def browseToFile(self):
#        fdiag = QtGui.QFileDialog() 
#        #fdiag.setFilters(formatGen.getFilters())
#        fdiag.setModal(1)
#        fdiag.setFileMode(fdiag.ExistingFile)
#        ret = fdiag.exec_()
#        if  ret == QtGui.QDialog.Accepted:
#            self.file=fdiag.selectedFiles()[0]
#            self.ThomsonFileEntry.setText(self.file)
#            #ftype = str(fdiag.selectedFilter()).split("(")[0].rstrip()
#            #return f
#        else:
#            return
         
    #def SaveLattice(self):
        #self.Processor.saveOutput(self.OutputDirEntry.text())
        #self.Processor.writeCarbonAtoms()

    
#    def MinLoopToggle(self):
#        if(self.MinLoopCk.isChecked()):
#            self.config.opts["MinLoop = True
#        else:
#            self.config.opts["MinLoop = False

#    def thomsonPointCuttoffChanged(self,index):
#        print "thomsonPointCuttoffChanged",index
#        self.Processor.thomsonPointCutoffChanged(index)



                 