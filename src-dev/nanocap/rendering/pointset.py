'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Aug 29 2012
Copyright Marc Robinson 2013
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

Pointset Actor (direct from Numpy)

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
'''
from nanocap.core.globals import *
import os,sys,math,copy,random,time

import copy
from nanocap.core.util import *
import nanocap.rendering.renderwidgets as  renderwidgets

from vtk import vtkDoubleArray,vtkPoints,vtkLookupTable,vtkPolyData,vtkProgrammableGlyphFilter, \
                vtkSphereSource,vtkPolyDataMapper,vtkActor,vtkFollower,vtkVectorText \


class PointSet(object):
    def __init__(self,rad,col,Alt=False):
        self.res = 10
        self.Alt = Alt
        self.rad = rad
        self.col = col
        self.LabelActors = [] 
        self.LabelText = []
        self.pos = None
        self.npoints = 0
        
        #self.PointSetLabel = points.PointSetLabel
        self.showLabels = False
        self.VTKScalars = vtkDoubleArray()
        self.VTKScalars.SetNumberOfComponents(1)
        self.NumpyScalars = None
#        self.VTKVectors = vtkDoubleArray()
#        self.VTKVectors.SetNumberOfComponents(3)
#        self.NumpyVectors = None
        self.VTKCoords = vtkDoubleArray()
        self.VTKCoords.SetNumberOfComponents(3)
        self.NumpyCoords = None
        
        self.LookupTable = vtkLookupTable()
        self.VTKPoints = vtkPoints()
        
        self.PolyData = vtkPolyData()
        self.PolyData.SetPoints(self.VTKPoints)
        self.PolyData.GetPointData().SetScalars(self.VTKScalars)
        #self.PolyData.GetPointData().SetVectors(self.VTKVectors) 
        
        self.Glyph3D = vtkProgrammableGlyphFilter()
        self.Glyph3D.SetInput(self.PolyData)  
        
        self.GlyphSource= vtkSphereSource()   
        self.Glyph3D.SetGlyphMethod(self.glyphMethod)  
        self.Glyph3D.SetSource(self.GlyphSource.GetOutput())
        
        
        self.Mapper = vtkPolyDataMapper()
        self.Mapper.SetLookupTable(self.LookupTable)
        self.Mapper.SetInputConnection(self.Glyph3D.GetOutputPort())
        
        self.Actor = vtkActor()
        
    
        self.boundaryActor = renderwidgets.CellMatrixActor()
        #self.boundaryActor.set(cellMatrix, origin, 0,0,0)
    
    def setBoundaryActor(self):
        x0,y0,z0,x1,y1,z1 = self.getBounds()
        self.CM = numpy.array([x1-x0,0,0,
                          0,y1-y0,0,
                          0,0,z1-z0])
        self.Origin = numpy.array([x0,y0,z0])
        #self.boundaryActor = rendering.CellMatrixActor()
        self.boundaryActor.set(self.CM,self.Origin, 0,0,0)
        
        
    def glyphMethod(self,*args,**kargs):
        PointId = self.Glyph3D.GetPointId()
        Scalar = self.Glyph3D.GetPointData().GetScalars().GetTuple1(PointId)
        #Vector = self.Glyph3D.GetPointData().GetVectors().GetTuple3(PointId)
        Pos = self.Glyph3D.GetPoint()
        self.GlyphSource.SetPhiResolution(self.res)
        self.GlyphSource.SetThetaResolution(self.res)
        self.GlyphSource.SetRadius(self.rad)
        #print "glyph",self.rad
        self.GlyphSource.SetCenter(Pos)    
          
    def initArrays(self,points):
        printl("initArrays",points)
        #self.npoints = copy.deepcopy(points.npoints)
        #self.pos = numpy.copy(points.pos)
        if(points==None):return
        self.points = points
        self.npoints = points.npoints
        self.pos = points.pos
        #if(self.npoints==0):return
        
        self.NumpyScalars = numpy.zeros(self.npoints,NPF)
        if(self.Alt): self.NumpyScalars[1::2] = 1
        self.VTKScalars.SetVoidArray(self.NumpyScalars, self.NumpyScalars.size, 1) 
        self.initLUT(ncolors=2,range=(0,1))

        self.LookupTable.SetTableValue(0,self.col[0],
                                           self.col[1],
                                           self.col[2],1.0)
        self.LookupTable.SetTableValue(1,1.0,
                                           0.0,
                                           0.0,1.0)
        
        self.setupLabels()
    
    def reset(self):
        self.NumpyScalars = numpy.zeros(self.npoints*3,NPF)
        self.VTKScalars.SetVoidArray(self.NumpyScalars, self.NumpyScalars.size, 1) 
        self.setupLabels()
        self.setBoundaryActor()
    
    def toggleBoundingBox(self,flag):
        if(flag):self.addBoundingBox()
        else:self.removeBoundingBox()
        
    def addBoundingBox(self,ren=None):
        printl("addBoundingBox")
        self.setBoundaryActor()
        if(ren==None):self.boundaryActor.addToRenderer(self.ren,False,True)
        else:self.boundaryActor.addToRenderer(ren,False,True)
    
    def removeBoundingBox(self,ren=None):
        if(ren==None):self.boundaryActor.removeFromRenderer(self.ren)
        else:self.boundaryActor.removeFromRenderer(ren)
        
    def removeLabels(self,ren=None):
        #printl("removeLabels",self.points.PointSetLabel)#,ren)
        for actor in self.LabelActors: 
            if(ren==None):self.ren.RemoveActor(actor)
            else:ren.RemoveActor(actor)
        self.showLabels = False
        #self.ren = ren
    
    def addLabels(self,ren=None):
        #printl("addLabels",self.points.PointSetLabel)
        self.updateLabels()
        self.setBoundaryActor()
        for actor in self.LabelActors:
            actor.SetCamera(ren.GetActiveCamera())
            if(ren==None):self.ren.AddActor(actor)
            else:
                ren.AddActor(actor)
                self.label_ren = ren
        self.showLabels = True
        
        
    def setupLabels(self):
        if(self.pos==None):return
        if(numpy.ndim(self.pos)==0):return 
        #print self.points.PointSetLabel,self.pos,self.pos==None
        
        try:self.removeLabels(self.ren)
        except:pass
        try:self.removeLabels(self.label_ren)
        except:pass
        
        self.LabelActors = []
        self.LabelText = []
        for i in range(0,self.npoints):
            actor = vtkFollower()
            actor.SetScale(0.3, 0.3, 0.3)
            label = vtkVectorText()
            text = (" %d %3.3f %3.3f %3.3f" % (i,self.pos[i*3],self.pos[i*3+1],self.pos[i*3+2]))
            text = (" %d " % (i))
            label.SetText(text)
            
            labelMapper = vtkPolyDataMapper()
            labelMapper.SetInputConnection(label.GetOutputPort())
            actor.SetMapper(labelMapper)
            actor.SetPosition(self.pos[i*3],self.pos[i*3+1],self.pos[i*3+2])
            #printl("setting actor position",self.pos[i*3],self.pos[i*3+1],self.pos[i*3+2])
            actor.GetProperty().SetDiffuseColor(0,0,0)
            self.LabelActors.append(actor)
            self.LabelText.append(label)
#            actor.SetCamera(ren.GetActiveCamera())
#            self.labels.append(actor)
#            ren.AddActor(actor)
#            self.ren = ren        
    
    def getBounds(self):
        if(self.pos==None):return 0,0,0,0,0,0
        if(self.npoints==0):
            return 0,0,0,0,0,0
        if(numpy.ndim(self.pos)==0):return 0,0,0,0,0,0
        x,y,z = self.pos[0::3],self.pos[1::3],self.pos[2::3]
        return numpy.min(x),numpy.min(y),numpy.min(z),numpy.max(x),numpy.max(y),numpy.max(z)        
    
    
    def updateLabels(self):
        if(self.pos==None):return
        if(numpy.ndim(self.pos)==0):return 
        
        for i in range(0,self.npoints):
            #printl("updateLabels",self.LabelText[i])
            #self.LabelText[i].SetText(str(i))
            
            text = (" %d %3.3f %3.3f %3.3f" % (i,self.pos[i*3],self.pos[i*3+1],self.pos[i*3+2]))
            text = (" %d " % (i))
            self.LabelText[i].SetText(text)
            #printl("updateLabels",self.pos[i*3],self.pos[i*3+1],self.pos[i*3+2])
            self.LabelActors[i].SetPosition(self.pos[i*3],self.pos[i*3+1],self.pos[i*3+2])

        
        
    def initLUT(self,ncolors = 1024,hueRange=None,range=None,ramp=False,swapHue=False,monoChrome=False):           
        self.LookupTable = vtkLookupTable()
        self.LookupTable.SetNumberOfColors(ncolors)
        if(hueRange!=None):self.LookupTable.SetHueRange(hueRange)
        if(range!=None):self.LookupTable.SetRange(range)  
        if(ramp):self.LookupTable.SetRampToLinear()
        
        if(swapHue):self.LookupTable.SetHueRange(hueRange[1],hueRange[0])
        if(monoChrome):
            self.LookupTable.SetSaturationRange(0,0)
            if(swapHue):
                self.LookupTable.SetValueRange(1.0,0.2)
            else:
                self.LookupTable.SetValueRange(0.2,1.0) 
        self.LookupTable.Build()    
        self.Mapper.SetScalarRange(range)    
        self.Mapper.SetLookupTable(self.LookupTable)   
    
     
    def addToRenderer(self,ren=None,col=None):
        '''
        add the actor to the given renderer first
        before assigning the mapper. This associates the
        renderer with the actor for updates etc.
        '''
        #print("adding to renderer",self.pos)
        if(ren==None):
            try:self.ren.AddActor(self.Actor) 
            except:printl("Cannot add pointSet without renderer")
        else:
            ren.AddActor(self.Actor) 
            self.ren=ren
                
        if self.pos == None: return
        if len(self.pos) == 0:return
        
        if(col!=None):self.col = col
        self.LookupTable.SetTableValue(0,self.col[0],
                                           self.col[1],
                                           self.col[2],1.0)
        self.LookupTable.SetTableValue(1,1.0,
                                           0.0,
                                           0.0,1.0)
        
        
#        if(self.showLabels):
#            self.updateLabels()
#            self.addLabels(ren)
#        else:self.removeLabels(ren)
                
        self.VTKCoords.SetVoidArray(self.pos, self.pos.size, 1) 
        printl("set void array")
        self.VTKPoints.SetData(self.VTKCoords)
        self.PolyData.SetPoints(self.VTKPoints)
        self.PolyData.GetPointData().SetScalars(self.VTKScalars)         
        self.Glyph3D.SetInput(self.PolyData)
        printl("set Glyph3D")
        self.VTKPoints.Modified()                
        self.setBoundaryActor()
        self.Actor.SetMapper(self.Mapper)
        printl("AddActor")
#         if(ren==None):
#             try:self.ren.AddActor(self.Actor) 
#             except:printl("Cannot add pointSet without renderer")
#         else:
#             ren.AddActor(self.Actor) 
#             self.ren=ren
   
    def removeFromRenderer(self,ren=None):
        if(ren==None):
            try:self.ren.RemoveActor(self.Actor) 
            except:printl("Cannot remove pointSet without renderer")
        else:ren.RemoveActor(self.Actor)   
        #for actor in self.LabelActors:
        #    ren.RemoveActor(actor)
          
    def update(self):
        if(self.pos==None):return
        if(len(self.pos)==0):return
        self.PolyData.SetPoints(self.VTKPoints)
        self.PolyData.GetPointData().SetScalars(self.VTKScalars)
        #self.PolyData.GetPointData().SetVectors(self.VTKVectors) 
        

        self.Glyph3D.SetInput(self.PolyData)  
        
        self.GlyphSource= vtkSphereSource()   
        self.Glyph3D.SetGlyphMethod(self.glyphMethod)  
        self.Glyph3D.SetSource(self.GlyphSource.GetOutput())
        

        self.Mapper.SetLookupTable(self.LookupTable)
        self.Mapper.SetInputConnection(self.Glyph3D.GetOutputPort())
        
        self.Actor.SetMapper(self.Mapper)
        
        
        printl("Update:",self.rad,self.col)
        self.LookupTable.SetTableValue(0,self.col[0],
                                           self.col[1],
                                           self.col[2],1.0)
        self.VTKCoords.SetVoidArray(self.pos, self.pos.size, 1) 
        self.LookupTable.SetTableValue(1,1.0,
                                           0.0,
                                           0.0,1.0)
        
        self.VTKPoints.SetData(self.VTKCoords)
        self.VTKPoints.Modified()
        
        self.updateLabels()
        self.setBoundaryActor()
        #self.setupLabels()

        
class pointActor(vtkActor):
    def __init__(self,rad,res,x,y,z,r,g,b):
        self.pos = numpy.array([x,y,z])
        self.source = vtkSphereSource()
        self.source.SetRadius(rad)
        self.source.SetPhiResolution(res)
        self.source.SetThetaResolution(res)
        self.source.SetCenter(x,y,z)
        self.Mapper = vtkPolyDataMapper()
        self.Mapper.SetInput(self.source.GetOutput())
        self.SetMapper(self.Mapper)
        self.GetProperty().SetColor((r,g,b))
    def moveto(self,x,y,z):
        self.pos = numpy.array([x,y,z])
        self.source.SetCenter(x,y,z)        
    def setcolor(self,color):
        self.GetProperty().SetColor(color)
    def setrad(self,rad):
        self.source.SetRadius(rad)    
    def getPos(self):
        return self.pos
        
        
        
