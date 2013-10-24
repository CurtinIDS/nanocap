'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Oct 8 2013
Copyright Marc Robinson 2013
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

Gui/Render operations
Add/Remove points etc
Update Triangles

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
'''
from nanocap.core.globals import *
import nanocap.core.globals as globals
import os,sys,math,copy,random,time,types,threading
from nanocap.core.globals import QT
QtGui, QtCore = QT.QtGui, QT.QtCore

import numpy

import nanocap.gui.forms as forms
from nanocap.gui.forms import *
import nanocap.core.processes as processes
from nanocap.gui.structurewindow import StructureWindow
from nanocap.core.util import *
import nanocap.rendering.pointset as pointset


class Operations(QtGui.QWidget):   
    def __init__(self, Gui, MainWindow):
        QtGui.QWidget.__init__(self, None)
        self.MainWindow = MainWindow
        self.Gui = Gui
        self.Processor = self.Gui.processor
        self.ThreadManager = self.Gui.threadManager
        self.SignalManager = self.Gui.signalManager
        self.VTKFrame = self.Gui.vtkframe
        self.ObjectActors = self.Gui.objectActors
        self.config = self.Processor.config
        self.Processor.renderUpdate = types.MethodType( self.RenderUpdate, self.Processor )
    
    def RenderUpdate(self,*args): 
        self.ObjectActors.removeAllActors() 
        
        self.config.opts["updatingRender"] = True 
        
        printl("RenderUpdate",threading.currentThread())
        
        if(self.config.opts["GenType"]=="Fullerene"):
            dualLattice = self.Processor.fullerene.thomsonPoints   

            self.ObjectActors.FullereneDualLatticePoints.initArrays(dualLattice)
            self.ObjectActors.FullereneDualLatticePoints.update()
            try:
                carbonLattice = self.Processor.fullerene.carbonAtoms
                self.ObjectActors.FullereneCarbonAtomsPoints.initArrays(carbonLattice)
                self.ObjectActors.FullereneCarbonAtomsPoints.update()
            except:pass
            
        if(self.config.opts["GenType"]=="Nanotube"):  
            dualLattice = self.Processor.nanotube.cappedTubeThomsonPoints
            printl("CappedNanotubeTubeDualLatticePoints arrays",
                   self.Processor.nanotube.cappedTubeThomsonPoints.pos[0:10],
                   self.Processor.cap.thomsonPoints.pos[0:10])
            self.ObjectActors.CappedNanotubeTubeDualLatticePoints.initArrays(dualLattice)
            self.ObjectActors.CappedNanotubeTubeDualLatticePoints.update()
            
            self.ObjectActors.CapDualLatticePoints.initArrays(self.Processor.cap.thomsonPoints)
            self.ObjectActors.CapDualLatticePoints.update()
        
            self.ObjectActors.ReflectedCapDualLatticePoints.initArrays(self.Processor.reflectedCap.thomsonPoints)
            self.ObjectActors.ReflectedCapDualLatticePoints.update()
            
            self.ObjectActors.NanotubeTubeDualLatticePoints.initArrays(self.Processor.nanotube.tubeThomsonPoints)
            self.ObjectActors.NanotubeTubeDualLatticePoints.update()
        
            try:
                carbonLattice = self.Processor.nanotube.cappedTubeCarbonAtoms
                self.ObjectActors.CappedNanotubeTubeCarbonAtomsPoints.initArrays(carbonLattice)
                self.ObjectActors.CappedNanotubeTubeCarbonAtomsPoints.update()
            except:pass
            
        if(self.config.opts["CalcTriangulation"] and self.config.opts["ShowTriangulation"]):
            self.ObjectActors.setupTriangleMesh(dualLattice,self.Processor.ntriangles,self.Processor.verts)
        
        if(self.config.opts["CalcCarbonBonds"] and self.config.opts["ShowCarbonBonds"]):
            self.ObjectActors.setupBondActors(self.Processor.nbonds,self.Processor.bonds)
##            
        if(self.config.opts["CalcCarbonRings"] and self.config.opts["ShowCarbonRings"]):
            self.ObjectActors.setupRingActors(carbonLattice,self.Processor.MaxVerts,
                                              self.Processor.Rings,self.Processor.VertsPerRingCount)    
        
        if(self.config.opts["CalcSchlegel"]):
            if(self.config.opts["GenType"]=="Fullerene"):
                self.ObjectActors.FullereneSchlegelDualLatticePoints.initArrays(self.Processor.schlegelThomsonPoints)
                self.ObjectActors.FullereneSchlegelDualLatticePoints.update()
                
                self.ObjectActors.FullereneSchlegelCarbonAtomsPoints.initArrays(self.Processor.schlegelCarbonAtoms)
                self.ObjectActors.FullereneSchlegelCarbonAtomsPoints.update()
                
            if(self.config.opts["GenType"]=="Nanotube"):
                self.ObjectActors.NanotubeSchlegelDualLatticePoints.initArrays(self.Processor.schlegelThomsonPoints)
                self.ObjectActors.NanotubeSchlegelDualLatticePoints.update()
                
                self.ObjectActors.NanotubeSchlegelCarbonAtomsPoints.initArrays(self.Processor.schlegelCarbonAtoms)
                self.ObjectActors.NanotubeSchlegelCarbonAtomsPoints.update()
                
                self.ObjectActors.NanotubeTubeSchlegelDualLatticePoints.initArrays(self.Processor.schlegelTubeThomsonPoints)
                self.ObjectActors.NanotubeTubeSchlegelDualLatticePoints.update()
            
            self.ObjectActors.setupSchlegelRingActors(self.Processor.schlegelCarbonLattice,self.Processor.schlegelMaxVerts,
                                              self.Processor.schlegelRings,self.Processor.schlegelVertsPerRingCount)  
#            
         
#        
        if(self.config.opts["GenType"]=="Nanotube"):  
            self.ToggleTubeDualLatticePoints()
            self.ToggleCappedTubeDualLatticePoints()
            self.ToggleCapDualLatticePoints()
            self.ToggleCappedTubeCarbonAtoms() 
#             
        if(self.config.opts["GenType"]=="Fullerene"):
            dualLattice = self.Processor.fullerene.thomsonPoints 
            self.ToggleFullereneDualLatticePoints()
            self.ToggleFullereneCarbonAtoms()
#                  
        self.ToggleTriangulation()
        self.ToggleCarbonBonds()
        self.ToggleCarbonRings()
        self.ToggleBoundingBoxes()
        self.ToggleSchlegel()
        self.ToggleScreenInfo()
#        

        try:self.VTKFrame.centerCameraOnPointSet(carbonLattice)
        except:self.VTKFrame.centerCameraOnPointSet(dualLattice)
        
        printl("ending render update")

        
        self.config.opts["updatingRender"] = False 

    
    def ToggleLabels(self):    
        printl("ToggleLabels",self.config.opts["ShowFullereneDualLatticePointsLabels"],self.config.opts["ShowFullereneCarbonAtomsLabels"])
        if(self.config.opts["GenType"]=="Fullerene"):   
            try:
                if(self.config.opts["ShowFullereneDualLatticePointsLabels"]):
                    self.ObjectActors.addLabels(self.ObjectActors.FullereneDualLatticePoints)
                else:self.ObjectActors.removeLabels(self.ObjectActors.FullereneDualLatticePoints)
            except:pass
            try:
                if(self.config.opts["ShowFullereneCarbonAtomsLabels"]):
                    printl("adding ShowFullereneCarbonAtomsLabels")
                    self.ObjectActors.addLabels(self.ObjectActors.FullereneCarbonAtomsPoints)
                else:self.ObjectActors.removeLabels(self.ObjectActors.FullereneCarbonAtomsPoints)
            except:pass
            
        if(self.config.opts["GenType"]=="Nanotube"):   
            try:
                if(self.config.opts["ShowCappedTubeCarbonAtomsLabels"]):
                    self.ObjectActors.addLabels(self.ObjectActors.CappedNanotubeTubeCarbonAtomsPoints)
                else:self.ObjectActors.removeLabels(self.ObjectActors.CappedNanotubeTubeCarbonAtomsPoints)
            except:pass   
            try:
                if(self.config.opts["ShowCappedTubeDualLatticePointsLabels"]):
                    self.ObjectActors.addLabels(self.ObjectActors.CappedNanotubeTubeDualLatticePoints)
                else:self.ObjectActors.removeLabels(self.ObjectActors.CappedNanotubeTubeDualLatticePoints)
            except:pass 
            try:
                if(self.config.opts["ShowCapDualLatticePointsLabels"]):
                    self.ObjectActors.addLabels(self.ObjectActors.CapDualLatticePoints)
                    self.ObjectActors.addLabels(self.ObjectActors.ReflectedCapDualLatticePoints)
                else:
                    self.ObjectActors.removeLabels(self.ObjectActors.CapDualLatticePoints)
                    self.ObjectActors.removeLabels(self.ObjectActors.ReflectedCapDualLatticePoints)
            except:pass   

            try:
                if(self.config.opts["ShowTubeDualLatticePointsLabels"]):
                    self.ObjectActors.addLabels(self.ObjectActors.NanotubeTubeDualLatticePoints)
                else:self.ObjectActors.removeLabels(self.ObjectActors.NanotubeTubeDualLatticePoints)
            except:pass 
            try:
                if(self.config.opts["ShowTubeCarbonAtomsLabels"]):
                    self.ObjectActors.addLabels(self.ObjectActors.NanotubeTubeCarbonAtomsPoints)
                else:self.ObjectActors.removeLabels(self.ObjectActors.NanotubeTubeCarbonAtomsPoints)
            except:pass 
    
    def ToggleNanotubeCarbonAtoms(self):
        if(self.config.opts["ShowTubeCarbonAtoms"]):
            self.ObjectActors.addPointSetToRenderer(self.ObjectActors.NanotubeTubeCarbonAtomsPoints)          
        else:
            self.ObjectActors.removePointSetFromRenderer(self.ObjectActors.NanotubeTubeCarbonAtomsPoints) 
        
        
    def ToggleFullereneDualLatticePoints(self):
        if(self.config.opts["ShowFullereneDualLatticePoints"]):
            self.ObjectActors.addPointSetToRenderer(self.ObjectActors.FullereneDualLatticePoints)
        else:
            self.ObjectActors.removePointSetFromRenderer(self.ObjectActors.FullereneDualLatticePoints)
    
    def ToggleFullereneCarbonAtoms(self):
        if(self.config.opts["ShowFullereneCarbonAtoms"]):
            self.ObjectActors.addPointSetToRenderer(self.ObjectActors.FullereneCarbonAtomsPoints)
        else:
            self.ObjectActors.removePointSetFromRenderer(self.ObjectActors.FullereneCarbonAtomsPoints)
    
    def ToggleTubeDualLatticePoints(self):
        if(self.config.opts["ShowTubeDualLatticePoints"]):
            self.ObjectActors.addPointSetToRenderer(self.ObjectActors.NanotubeTubeDualLatticePoints)          
        else:
            self.ObjectActors.removePointSetFromRenderer(self.ObjectActors.NanotubeTubeDualLatticePoints) 

    
    def ToggleCappedTubeDualLatticePoints(self):
        if(self.config.opts["ShowCappedTubeDualLatticePoints"]):
            self.ObjectActors.addPointSetToRenderer(self.ObjectActors.CappedNanotubeTubeDualLatticePoints)          
        else:
            self.ObjectActors.removePointSetFromRenderer(self.ObjectActors.CappedNanotubeTubeDualLatticePoints) 
            
                
    def ToggleCappedTubeCarbonAtoms(self):
        if(self.config.opts["ShowCappedTubeCarbonAtoms"]):
            self.ObjectActors.addPointSetToRenderer(self.ObjectActors.CappedNanotubeTubeCarbonAtomsPoints)          
        else:
            self.ObjectActors.removePointSetFromRenderer(self.ObjectActors.CappedNanotubeTubeCarbonAtomsPoints) 

    
    def ToggleCapDualLatticePoints(self):
        printl("ToggleCapDualLatticePoints",self.config.opts["ShowCapDualLatticePoints"])
        if(self.config.opts["ShowCapDualLatticePoints"]):
            self.ObjectActors.addPointSetToRenderer(self.ObjectActors.CapDualLatticePoints)  
            self.ObjectActors.addPointSetToRenderer(self.ObjectActors.ReflectedCapDualLatticePoints)  
        else:
            self.ObjectActors.removePointSetFromRenderer(self.ObjectActors.CapDualLatticePoints) 
            self.ObjectActors.removePointSetFromRenderer(self.ObjectActors.ReflectedCapDualLatticePoints) 

    
    def ToggleSchlegel(self): 
        if(self.config.opts["CalcSchlegel"]):  
            if(self.config.opts["GenType"]=="Fullerene"):
                if(self.config.opts["ShowFullereneDualLatticePoints"]):
                    self.ObjectActors.addPointSetToSchlegelRenderer(self.ObjectActors.FullereneSchlegelDualLatticePoints)  
                if(self.config.opts["ShowFullereneCarbonAtoms"]):
                    self.ObjectActors.addPointSetToSchlegelRenderer(self.ObjectActors.FullereneSchlegelCarbonAtomsPoints)  
                    
            if(self.config.opts["GenType"]=="Nanotube"):
                if(self.config.opts["ShowCappedTubeDualLatticePoints"]):
                    self.ObjectActors.addPointSetToSchlegelRenderer(self.ObjectActors.NanotubeSchlegelDualLatticePoints)  
                if(self.config.opts["ShowCappedTubeCarbonAtoms"]):
                    self.ObjectActors.addPointSetToSchlegelRenderer(self.ObjectActors.NanotubeSchlegelCarbonAtomsPoints)  
                if(self.config.opts["ShowTubeDualLatticePoints"]):    
                    self.ObjectActors.addPointSetToSchlegelRenderer(self.ObjectActors.NanotubeTubeSchlegelDualLatticePoints)  
            
            if(self.config.opts["ShowCarbonRings"]):
                self.ObjectActors.schlegelcarbonRings.AddToRenderer(self.ObjectActors.SchlegelVTKFrame.VTKRenderer) 
            else:
                self.ObjectActors.schlegelcarbonRings.RemoveFromRenderer(self.ObjectActors.SchlegelVTKFrame.VTKRenderer)   

        else:
            try:
                if(self.config.opts["GenType"]=="Fullerene"):
                    self.ObjectActors.removePointSetFromSchlegelRenderer(self.ObjectActors.FullereneSchlegelDualLatticePoints)
                    self.ObjectActors.removePointSetFromSchlegelRenderer(self.ObjectActors.FullereneSchlegelCarbonAtomsPoints)
                
                if(self.config.opts["GenType"]=="Nanotube"):
                    self.ObjectActors.removePointSetFromSchlegelRenderer(self.ObjectActors.NanotubeSchlegelDualLatticePoints)
                    self.ObjectActors.removePointSetFromSchlegelRenderer(self.ObjectActors.NanotubeSchlegelCarbonAtomsPoints)
                    self.ObjectActors.removePointSetFromSchlegelRenderer(self.ObjectActors.NanotubeTubeSchlegelDualLatticePoints)
            except:pass
                    
  
            
    def ToggleScreenInfo(self):            
        if(self.config.opts["ShowScreenInfo"]):  
            lines = []     
            if(self.config.opts["GenType"]=="Fullerene"):
                carbonAtoms = self.Processor.fullerene.carbonAtoms
                thomsonPoints = self.Processor.fullerene.thomsonPoints
            if(self.config.opts["GenType"]=="Nanotube"):
                carbonAtoms = self.Processor.nanotube.cappedTubeCarbonAtoms
                thomsonPoints = self.Processor.nanotube.cappedTubeThomsonPoints
            try:
                String = "Rings: "
                for i in range(3,self.Processor.MaxVerts):
                    if(i==5):String+=str(i)+":"+str(self.Processor.ringCount[i])+"(IP:"+str(self.Processor.isolatedPentagons)+") "  
                    else:String+=str(i)+":"+str(self.Processor.ringCount[i])+" "
                String+=" "+str("%3.2f" % self.Processor.percHex)+"% Hex"  
                lines.append(String)
            except:pass
            try:
                String = "Carbon atoms: "+str(carbonAtoms.npoints)
                lines.append(String)
            except:pass
            try:
                String = "Dual Lattice points: "+str(thomsonPoints.npoints)
                lines.append(String)
            except:pass
            try:
                Energy = "Dual Lattice Energy: "+str(thomsonPoints.FinalEnergy)
                lines.append(Energy)
            except:pass
            try:
                Energy = "Carbon Lattice Energy: "+str(carbonAtoms.FinalEnergy)+" eV "
                EnergyPA = "Carbon Lattice Energy Per Atom: "+str(carbonAtoms.FinalEnergy/carbonAtoms.npoints)+" eV "
                Scale = "Carbon Lattice Scale: "+str(carbonAtoms.FinalScale)
                lines.append(Energy)
                lines.append(EnergyPA)
                lines.append(Scale)
            except:pass
            self.ObjectActors.updateScreenInfo(lines)
            self.ObjectActors.addScreenInfo()    
        else:
            self.ObjectActors.removeScreenInfo()    
              
            
        printl("ShowScreenInfo",self.config.opts["ShowScreenInfo"])
    
    def ToggleTriangulation(self):
        if(self.config.opts["ShowTriangulation"]):
            self.VTKFrame.VTKRenderer.AddActor(self.ObjectActors.triangleMesh)
        else:
            self.VTKFrame.VTKRenderer.RemoveActor(self.ObjectActors.triangleMesh)    
            
        self.VTKFrame.refreshWindow()
    
    def ToggleCarbonRings(self):
        if(self.config.opts["ShowCarbonRings"]):
            self.ObjectActors.carbonRings.AddToRenderer(self.VTKFrame.VTKRenderer) 
        else:
            self.ObjectActors.carbonRings.RemoveFromRenderer(self.VTKFrame.VTKRenderer) 
            
        self.VTKFrame.refreshWindow()
    
    def ToggleCarbonBonds(self):
        if(self.config.opts["ShowCarbonBonds"]):
            self.VTKFrame.VTKRenderer.AddActor(self.ObjectActors.carbonBonds)
        else:
            self.VTKFrame.VTKRenderer.RemoveActor(self.ObjectActors.carbonBonds)    
            
        self.VTKFrame.refreshWindow()
            
    def ToggleBoundingBoxes(self):
        printl("ToggleBoundingBoxes")
        

        if(self.config.opts["GenType"]=="Fullerene"):   
            try:
                if(self.config.opts["ShowFullereneDualLatticePointsBox"]):
                    self.ObjectActors.addBoundingBox(self.ObjectActors.FullereneDualLatticePoints)
                else:self.ObjectActors.removeBoundingBox(self.ObjectActors.FullereneDualLatticePoints)
            except:pass
            try:
                if(self.config.opts["ShowFullereneCarbonAtomsBox"]):
                    self.ObjectActors.addBoundingBox(self.ObjectActors.FullereneCarbonAtomsPoints)
                else:self.ObjectActors.removeBoundingBox(self.ObjectActors.FullereneCarbonAtomsPoints)
            except:pass
            
        if(self.config.opts["GenType"]=="Nanotube"):   
            try:
                if(self.config.opts["ShowCappedTubeCarbonAtomsBox"]):
                    self.ObjectActors.addBoundingBox(self.ObjectActors.CappedNanotubeTubeCarbonAtomsPoints)
                else:self.ObjectActors.removeBoundingBox(self.ObjectActors.CappedNanotubeTubeCarbonAtomsPoints)
            except:pass   
            try:
                if(self.config.opts["ShowCappedTubeDualLatticePointsBox"]):
                    self.ObjectActors.addBoundingBox(self.ObjectActors.CappedNanotubeTubeDualLatticePoints)
                else:self.ObjectActors.removeBoundingBox(self.ObjectActors.CappedNanotubeTubeDualLatticePoints)
            except:pass 
            try:
                if(self.config.opts["ShowCapDualLatticePointsBox"]):
                    self.ObjectActors.addBoundingBox(self.ObjectActors.CapDualLatticePoints)
                    self.ObjectActors.addBoundingBox(self.ObjectActors.ReflectedCapDualLatticePoints)
                else:
                    self.ObjectActors.removeBoundingBox(self.ObjectActors.CapDualLatticePoints)
                    self.ObjectActors.removeBoundingBox(self.ObjectActors.ReflectedCapDualLatticePoints)
            except:pass   

            try:
                if(self.config.opts["ShowTubeDualLatticePointsBox"]):
                    self.ObjectActors.addBoundingBox(self.ObjectActors.NanotubeTubeDualLatticePoints)
                else:self.ObjectActors.removeBoundingBox(self.ObjectActors.NanotubeTubeDualLatticePoints)
            except:pass 
            try:
                if(self.config.opts["ShowTubeCarbonAtomsBox"]):
                    self.ObjectActors.addBoundingBox(self.ObjectActors.NanotubeTubeCarbonAtomsPoints)
                else:self.ObjectActors.removeBoundingBox(self.ObjectActors.NanotubeTubeCarbonAtomsPoints)
            except:pass 
    
    def getQtColour(self,icol):
        rgb = numpy.array(icol)*255
        qCol = QtGui.QColor(rgb[0],rgb[1],rgb[2])    
        col = QtGui.QColorDialog().getColor(qCol)
        if col.isValid():return col
        else:return qCol
        
    def changeTubeDualLatticePointColour(self,button):
        col = self.getQtColour(self.ObjectActors.NanotubeTubeDualLatticePoints.col)
        self.config.opts["TubeDualLatticePointColourRGB"] = ( col.red()/255.0, col.green()/255.0, col.blue()/255.0)
        button.setStyleSheet("QPushButton { background-color: %s ; border-radius: 5px }" % col.name())
        self.ObjectActors.NanotubeTubeDualLatticePoints.col=self.config.opts["TubeDualLatticePointColourRGB"]
        self.ObjectActors.NanotubeTubeDualLatticePoints.update() 
        self.VTKFrame.refreshWindow()
            
    def changeFullereneCarbonAtomsColour(self,button):
        col = self.getQtColour(self.ObjectActors.FullereneCarbonAtomsPoints.col)
        self.config.opts["FullereneCarbonAtomColourRGB"] = ( col.red()/255.0, col.green()/255.0, col.blue()/255.0)
        button.setStyleSheet("QPushButton { background-color: %s ; border-radius: 5px }" % col.name())
        self.ObjectActors.FullereneCarbonAtomsPoints.col=self.config.opts["FullereneCarbonAtomColourRGB"]
        self.ObjectActors.FullereneCarbonAtomsPoints.update() 
        self.VTKFrame.refreshWindow()
        
    def changeFullereneDualLatticePointColour(self,button):
        col = self.getQtColour(self.ObjectActors.FullereneDualLatticePoints.col)
        self.config.opts["FullereneDualLatticePointColourRGB"] = ( col.red()/255.0, col.green()/255.0, col.blue()/255.0)
        button.setStyleSheet("QPushButton { background-color: %s ; border-radius: 5px }" % col.name())
        self.ObjectActors.FullereneDualLatticePoints.col=self.config.opts["FullereneDualLatticePointColourRGB"]
        self.ObjectActors.FullereneDualLatticePoints.update() 
        self.VTKFrame.refreshWindow()
    
    def changeCappedTubeDualLatticePointColour(self,button):
        col = self.getQtColour(self.ObjectActors.CappedNanotubeTubeDualLatticePoints.col)
        self.config.opts["CappedTubeDualLatticePointColourRGB"] = ( col.red()/255.0, col.green()/255.0, col.blue()/255.0)
        button.setStyleSheet("QPushButton { background-color: %s ; border-radius: 5px }" % col.name())
        self.ObjectActors.CappedNanotubeTubeDualLatticePoints.col=self.config.opts["CappedTubeDualLatticePointColourRGB"]
        self.ObjectActors.CappedNanotubeTubeDualLatticePoints.update() 
        self.VTKFrame.refreshWindow()
        
    def changeCapDualLatticePointColour(self,button):
        col = self.getQtColour(self.ObjectActors.CapDualLatticePoints.col)
        self.config.opts["CapDualLatticePointColourRGB"] = ( col.red()/255.0, col.green()/255.0, col.blue()/255.0)
        button.setStyleSheet("QPushButton { background-color: %s ; border-radius: 5px }" % col.name())
        self.ObjectActors.CapDualLatticePoints.col=self.config.opts["CapDualLatticePointColourRGB"]
        self.ObjectActors.CapDualLatticePoints.update() 
        self.ObjectActors.ReflectedCapDualLatticePoints.col=self.config.opts["CapDualLatticePointColourRGB"]
        self.ObjectActors.ReflectedCapDualLatticePoints.update() 
        self.VTKFrame.refreshWindow()

    def changeCappedTubeCarbonAtomColour(self,button):
        col = self.getQtColour(self.ObjectActors.CappedNanotubeTubeCarbonAtomsPoints.col)
        self.config.opts["CappedTubeCarbonAtomColourRGB"] = ( col.red()/255.0, col.green()/255.0, col.blue()/255.0)
        button.setStyleSheet("QPushButton { background-color: %s ; border-radius: 5px }" % col.name())
        self.ObjectActors.CappedNanotubeTubeCarbonAtomsPoints.col=self.config.opts["CappedTubeCarbonAtomColourRGB"]
        self.ObjectActors.CappedNanotubeTubeCarbonAtomsPoints.update() 
        self.VTKFrame.refreshWindow()
        
    def changeTubeCarbonAtomColour(self,button):
        col = self.getQtColour(self.ObjectActors.NanotubeTubeCarbonAtomsPoints.col)
        self.config.opts["TubeCarbonAtomColourRGB"] = ( col.red()/255.0, col.green()/255.0, col.blue()/255.0)
        button.setStyleSheet("QPushButton { background-color: %s ; border-radius: 5px }" % col.name())
        self.ObjectActors.NanotubeTubeCarbonAtomsPoints.col=self.config.opts["TubeCarbonAtomColourRGB"]
        self.ObjectActors.NanotubeTubeCarbonAtomsPoints.update() 
        self.VTKFrame.refreshWindow()

            
    def setTubeDualLatticePointRad(self,val):
        self.config.opts["TubeDualLatticePointRadius"] = val
        self.ObjectActors.NanotubeTubeDualLatticePoints.rad = val
        self.ObjectActors.NanotubeTubeDualLatticePoints.update() 
        self.VTKFrame.refreshWindow()
    
    def setCappedTubeDualLatticePointRad(self,val):
        self.config.opts["CappedTubeDualLatticePointRadius"] = val
        self.ObjectActors.CappedNanotubeTubeDualLatticePoints.rad = val
        self.ObjectActors.CappedNanotubeTubeDualLatticePoints.update() 
        self.VTKFrame.refreshWindow()
    
    def setCapDualLatticePointRad(self,val):
        self.config.opts["CapDualLatticePointRadius"] = val
        self.ObjectActors.CapDualLatticePoints.rad = val
        self.ObjectActors.CapDualLatticePoints.update() 
        self.ObjectActors.ReflectedCapDualLatticePoints.rad = val
        self.ObjectActors.ReflectedCapDualLatticePoints.update() 
        self.VTKFrame.refreshWindow()
        
    def setCappedTubeCarbonAtomRad(self,val):
        self.config.opts["CappedTubeCarbonAtomRadius"] = val
        self.ObjectActors.CappedNanotubeTubeCarbonAtomsPoints.rad = val
        self.ObjectActors.CappedNanotubeTubeCarbonAtomsPoints.update() 
        self.VTKFrame.refreshWindow()
    
                
    def setTubeCarbonAtomRad(self,val):
        self.config.opts["TubeCarbonAtomRadius"] = val
        self.ObjectActors.NanotubeTubeCarbonAtomsPoints.rad = val
        self.ObjectActors.NanotubeTubeCarbonAtomsPoints.update() 
        self.VTKFrame.refreshWindow()
    
    def setFullereneDualLatticePointRad(self,val):
        self.config.opts["FullereneDualLatticePointRadius"] = val
        self.ObjectActors.FullereneDualLatticePoints.rad = val
        self.ObjectActors.FullereneDualLatticePoints.update() 
        self.VTKFrame.refreshWindow()     
        
    def setFullereneCarbonAtomRad(self,val):
        self.config.opts["FullereneCarbonAtomRadius"] = val  
        self.ObjectActors.FullereneCarbonAtomsPoints.rad = val
        self.ObjectActors.FullereneCarbonAtomsPoints.update() 
        self.VTKFrame.refreshWindow()
        
         