'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Aug 29 2012
Copyright Marc Robinson 2013
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

Main Object Actors (points, triangles etc)

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
'''

from nanocap.core.globals import *
from nanocap.core.util import *
import os,sys,math,copy,random,time
import numpy
from nanocap.rendering.renderwidgets import vtkZPlane,vtkRenderWindowText
import nanocap.rendering.pointset as pointset
import nanocap.rendering.bonds as bonds
import nanocap.rendering.polygon as polygon


from vtk import vtkDoubleArray,vtkPoints,vtkLookupTable,vtkPolyData,vtkProgrammableGlyphFilter, \
                vtkSphereSource,vtkPolyDataMapper,vtkActor,vtkFollower,vtkVectorText,vtkTubeFilter, \
                vtkFloatArray,vtkLineSource

class ObjectActors(object):
    def __init__(self,config,VTKFrame,SchlegelVTKFrame):
        self.triangleMesh = None
        self.VTKFrame = VTKFrame
        self.SchlegelVTKFrame = SchlegelVTKFrame
        self.config = config
        
        self.NanotubeCutoffPlane = vtkZPlane(0) 
        self.ScreenInfo = []
        self.carbonBonds = bonds.bondSet(0,thickness=self.config.opts["CarbonBondThickness"]) 
        self.carbonRings = polygon.polygonSet(MaxVerts=0,
                                  EdgeThickness = self.config.opts["CarbonBondThickness"])
        self.schlegelcarbonRings = polygon.polygonSet(MaxVerts=0,
                                  EdgeThickness = self.config.opts["CarbonBondThickness"])
        self.triangleMesh = polygon.polygon(0)
        
        self.FullereneDualLatticePoints = pointset.PointSet(self.config.opts["FullereneDualLatticePointRadius"],
                                                            self.config.opts["FullereneDualLatticePointColourRGB"])
        
        self.FullereneCarbonAtomsPoints = pointset.PointSet(self.config.opts["FullereneCarbonAtomRadius"],
                                                            self.config.opts["FullereneCarbonAtomColourRGB"])
        
        self.NanotubeTubeDualLatticePoints = pointset.PointSet(self.config.opts["TubeDualLatticePointRadius"],
                                                            self.config.opts["TubeDualLatticePointColourRGB"])
        
        self.NanotubeTubeCarbonAtomsPoints = pointset.PointSet(self.config.opts["TubeCarbonAtomRadius"],
                                                            self.config.opts["TubeCarbonAtomColourRGB"])
        
        self.CappedNanotubeTubeDualLatticePoints = pointset.PointSet(self.config.opts["CappedTubeDualLatticePointRadius"],
                                                            self.config.opts["CappedTubeDualLatticePointColourRGB"])
        
        self.CappedNanotubeTubeCarbonAtomsPoints = pointset.PointSet(self.config.opts["CappedTubeCarbonAtomRadius"],
                                                            self.config.opts["CappedTubeCarbonAtomColourRGB"])
        
        self.CapDualLatticePoints = pointset.PointSet(self.config.opts["CapDualLatticePointRadius"],
                                                      self.config.opts["CapDualLatticePointColourRGB"])
        
        self.ReflectedCapDualLatticePoints = pointset.PointSet(self.config.opts["CapDualLatticePointRadius"],
                                                      self.config.opts["CapDualLatticePointColourRGB"])
        
        
        self.FullereneSchlegelDualLatticePoints = pointset.PointSet(self.config.opts["FullereneDualLatticePointRadius"],
                                                      self.config.opts["FullereneDualLatticePointColourRGB"])
        
        
        self.FullereneSchlegelCarbonAtomsPoints = pointset.PointSet(self.config.opts["FullereneCarbonAtomRadius"],
                                                      self.config.opts["FullereneCarbonAtomColourRGB"])
                
        self.NanotubeSchlegelDualLatticePoints = pointset.PointSet(self.config.opts["CappedTubeDualLatticePointRadius"],
                                                      self.config.opts["CappedTubeDualLatticePointColourRGB"])
        
        
        self.NanotubeSchlegelCarbonAtomsPoints = pointset.PointSet(self.config.opts["CappedTubeCarbonAtomRadius"],
                                                      self.config.opts["CappedTubeCarbonAtomColourRGB"])
        
        self.NanotubeTubeSchlegelDualLatticePoints = pointset.PointSet(self.config.opts["TubeDualLatticePointRadius"],
                                                      self.config.opts["TubeCarbonAtomColourRGB"])
        
        

    
    
    def updateScreenInfo(self,lines):
        while(len(lines)<len(self.ScreenInfo)):
            self.ScreenInfo.pop()
        yoffset=20
            
        y = yoffset
        for i,line in enumerate(lines):
            try:self.ScreenInfo[i].change_input(line)
            except:self.ScreenInfo.append(vtkRenderWindowText(line,14,10,y,0,0,0))
            y+=yoffset        
    
    def removeScreenInfo(self):
        for line in self.ScreenInfo:
            self.VTKFrame.VTKRenderer.RemoveActor2D(line)
            self.SchlegelVTKFrame.VTKRenderer.RemoveActor2D(line)
        self.VTKFrame.refreshWindow()
        self.SchlegelVTKFrame.refreshWindow()
    def addScreenInfo(self):        
        for line in self.ScreenInfo:
            self.VTKFrame.VTKRenderer.AddActor2D(line)
            self.SchlegelVTKFrame.VTKRenderer.AddActor2D(line)
        self.VTKFrame.refreshWindow()
        self.SchlegelVTKFrame.refreshWindow()
    
    def moveNanotubeCutoffPlane(self,cutoff):
        self.NanotubeCutoffPlane.move(cutoff)
        self.VTKFrame.refreshWindow()   
        
    def addNanotubeCutoffPlane(self,cutoff):
        try:
            self.NanotubeCutoffPlane
            try:self.VTKFrame.VTKRenderer.AddActor(self.NanotubeCutoffPlane)
            except:pass 
        except:
            self.NanotubeCutoffPlane = vtkZPlane(cutoff)  
            self.VTKFrame.VTKRenderer.AddActor(self.NanotubeCutoffPlane)    
        
        print "self.NanotubeCutoffPlane adding",cutoff
        self.VTKFrame.refreshWindow()   
        
    def removeNanotubeCutoffPlane(self):   
        try:self.VTKFrame.VTKRenderer.RemoveActor(self.NanotubeCutoffPlane)
        except:pass 
        self.VTKFrame.refreshWindow()    
    
    def removeAllActors(self):
        self.VTKFrame.VTKRenderer.RemoveAllViewProps()
        self.SchlegelVTKFrame.VTKRenderer.RemoveAllViewProps()
        
    def addPointSetToRenderer(self,pointSet):
        pointSet.addToRenderer(self.VTKFrame.VTKRenderer,pointSet.col) 
        self.VTKFrame.refreshWindow()
        
    def removePointSetFromRenderer(self,pointSet):
        pointSet.removeFromRenderer(self.VTKFrame.VTKRenderer)
        self.VTKFrame.refreshWindow()
    
    def addPointSetToSchlegelRenderer(self,pointSet):
        pointSet.addToRenderer(self.SchlegelVTKFrame.VTKRenderer,pointSet.col) 
        self.SchlegelVTKFrame.refreshWindow()
        
    def removePointSetFromSchlegelRenderer(self,pointSet):
        pointSet.removeFromRenderer(self.SchlegelVTKFrame.VTKRenderer)
        self.SchlegelVTKFrame.refreshWindow()
    
    def addLabels(self,pointSet):
        pointSet.addLabels(self.VTKFrame.VTKRenderer)
        self.VTKFrame.refreshWindow()
    
    def removeLabels(self,pointSet):
        pointSet.removeLabels(self.VTKFrame.VTKRenderer)
        self.VTKFrame.refreshWindow()
        
    def addBoundingBox(self,pointSet):
        pointSet.addBoundingBox(self.VTKFrame.VTKRenderer)
        self.VTKFrame.refreshWindow()
    
    def removeBoundingBox(self,pointSet):
        pointSet.removeBoundingBox(self.VTKFrame.VTKRenderer)
        self.VTKFrame.refreshWindow()
    
    def setupBondActors(self,nbonds,bondarray):   
        self.bondarray =  numpy.copy(bondarray)
        try:
            self.carbonBonds.setBonds(nbonds,self.bondarray)
        except: 
            self.carbonBonds = bonds.bondSet(nbonds,thickness=self.config.opts["CarbonBondThickness"]) 
            self.carbonBonds.setBonds(nbonds,self.bondarray) 

    
        #move me to render operatons      
    def setupRingActors(self,pointSet,maxVerts,Rings,VertsPerRingCount):   
        #time.sleep(1)
        self.MaxVerts,self.Rings,self.VertsPerRingCount = maxVerts,numpy.copy(Rings),numpy.copy(VertsPerRingCount)
        try:
            self.carbonRings.RemoveFromRenderer(self.gui.vtkframe.VTKRenderer)
        except:
            pass
        
        self.carbonRings = polygon.polygonSet(MaxVerts=self.MaxVerts,
                                  EdgeThickness = self.config.opts["CarbonBondThickness"])
        
        self.carbonRings.setVerts(pointSet,self.Rings,self.VertsPerRingCount)
     
    def setupSchlegelRingActors(self,pointSet,maxVerts,Rings,VertsPerRingCount):   
        #time.sleep(1)
        self.schlegelMaxVerts,self.schlegelRings,self.schlegelVertsPerRingCount = maxVerts,numpy.copy(Rings),numpy.copy(VertsPerRingCount)
        
        try:
            self.schlegelcarbonRings.RemoveFromRenderer(self.gui.vtkframe.VTKRenderer)
        except:
            pass
        
        self.schlegelcarbonRings = polygon.polygonSet(MaxVerts=self.schlegelMaxVerts,
                                  EdgeThickness = self.config.opts["CarbonBondThickness"])
        
        self.schlegelcarbonRings.setVerts(pointSet,self.schlegelRings,self.schlegelVertsPerRingCount)        
    
    
        
    def setupTriangleMesh(self,pointSet,ntriangles,verts):
        self.ntriangles = ntriangles
        self.verts = numpy.copy(verts)
        try:
            self.triangleMesh.reset(numpy.sum(self.ntriangles*3))
        
        except:
            self.triangleMesh = polygon.polygon(self.ntriangles*3)#+self.thomsonPoints.npoints)

        printl("Npoints in triangles",self.ntriangles*3) 
                
        count = 0
        for i in range(0,self.ntriangles):                
            self.triangleMesh.addPoint(count,pointSet.getPoint(self.verts[i*3+0]))
            self.triangleMesh.addPoint(count+1,pointSet.getPoint(self.verts[i*3+1]))
            self.triangleMesh.addPoint(count+2,pointSet.getPoint(self.verts[i*3+2]))                           
            self.triangleMesh.addCell((count,count+1,count+2))
            count+=3
            
        self.triangleMesh.setScalars(numpy.zeros(self.ntriangles,NPF))
                    
        self.triangleMesh.update()
        printl("end Delauny Triangulation")