'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Aug 25 2013
Copyright Marc Robinson 2013
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

Polygon Actor (direct from Numpy)

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
'''
from nanocap.core.globals import *
from nanocap.core.util import *
import os,sys,math,copy,random,time
import numpy
from vtk import vtkDoubleArray,vtkPoints,vtkLookupTable,vtkPolyData,vtkProgrammableGlyphFilter, \
                vtkSphereSource,vtkPolyDataMapper,vtkActor,vtkFollower,vtkVectorText,vtkTubeFilter, \
                vtkFloatArray,vtkLineSource,vtkCellArray,vtkUnstructuredGrid,vtkGeometryFilter,\
                vtkPolyDataNormals,vtkExtractEdges,vtkDataSetMapper

 
class polygonSet(object):
    def __init__(self,MaxVerts=9,EdgeThickness=0.001):
        self.Points = vtkPoints()
        self.Cells = vtkCellArray()

        self.VTKCoords = vtkDoubleArray()
        self.VTKCoords.SetNumberOfComponents(3)
        
        self.RingOpacity = 1.0
        self.EdgeThickness = EdgeThickness
        self.EdgeColour = (0,0,0)
        
        self.RingColour = [0]*10
        self.RingColour[3] = (1,1,0)
        self.RingColour[4] = (1,0,1)
        self.RingColour[5] = (0,0,1)
        self.RingColour[6] = (0,1,0)
        self.RingColour[7] = (1,0,0)
        self.RingColour[8] = (0,1,1) 
        
        
        self.Actors = []
        self.EdgeActors = []
        self.MaxVerts = MaxVerts
    
        self.added=False
        
        self.Actors = [0]*self.MaxVerts
        self.EdgeActors = [0]*self.MaxVerts
        self.Edges = [0]*self.MaxVerts     
        
        for i in range(0,self.MaxVerts):
            self.Actors[i] = vtkActor()
            self.EdgeActors[i] = vtkActor()
            self.Edges[i] = vtkTubeFilter()
            
    def setVerts(self,pointSet,Rings,VertsPerRingCount):
        
        self.NumpyCoords = numpy.zeros(pointSet.npoints*3,NPF)
        self.VTKCoords.SetVoidArray(pointSet.pos, len(self.NumpyCoords), 1) 
        self.Points.SetData(self.VTKCoords)
        printl("Setting verts")
        
        
        self.Rings = Rings
        self.VertsPerRingCount = VertsPerRingCount
        for i in range(3,self.MaxVerts):
            actor = vtkActor()
            
            rings = numpy.where((self.VertsPerRingCount==i))[0]            
            if(len(rings)==0):continue
            cellArray = numpy.zeros(len(rings)*(i+1),NPI)
            cellArray[0::i+1] = i
            
            for j in range(0,i):
                cellArray[j+1::i+1] = self.Rings[rings*self.MaxVerts +j]
            
            Grid = vtkUnstructuredGrid()
            GeometryFilter = vtkGeometryFilter()
            Normals = vtkPolyDataNormals()
            Mapper = vtkPolyDataMapper()   
            Grid.SetPoints(self.Points)
            Cells = vtkCellArray()
            
            self.cellArray = cellArray
            
            for j in range(0,len(rings)):
                Cells.InsertNextCell(i)  
                for k in range(0,i):
                    v = self.cellArray[j*(i+1) + k+1]
                    Cells.InsertCellPoint(v)
            
            Grid.SetCells(7,Cells)
    
            GeometryFilter.SetInput(Grid)
            GeometryFilter.MergingOff() 
    
            Normals.SetInputConnection(GeometryFilter.GetOutputPort())
            Normals.ComputePointNormalsOn()    
            Normals.ComputeCellNormalsOn()
    
    
            Mapper.SetInputConnection(Normals.GetOutputPort())    
            actor.SetMapper(Mapper) 
            
            actor.GetProperty().SetColor(float(self.RingColour[i][0]),
                                             float(self.RingColour[i][1]),
                                              float(self.RingColour[i][2]))
            
            actor.GetProperty().SetOpacity(self.RingOpacity)
            
            Edges = vtkExtractEdges()
            Edges.SetInput(Grid)
            self.Edges[i] = vtkTubeFilter()
            self.Edges[i].SetInputConnection(Edges.GetOutputPort())
            self.Edges[i].SetRadius(self.EdgeThickness)
            self.Edges[i].SetNumberOfSides(5)
            self.Edges[i].UseDefaultNormalOn()
            self.Edges[i].SetDefaultNormal(.577, .577, .577)
            
            EdgeActor = vtkActor()
            
            EdgesMapper = vtkDataSetMapper() 
            EdgesMapper.SetInputConnection(self.Edges[i].GetOutputPort()) 
    
            EdgeActor.SetMapper(EdgesMapper)
            EdgeActor.GetProperty().SetColor(float(self.EdgeColour[0]),
                                              float(self.EdgeColour[1]),
                                              float(self.EdgeColour[2]))
            self.Actors[i] = actor
            self.EdgeActors[i] = EdgeActor
            
    def setEdgeThickness(self,thick):
        self.EdgeThickness = thick
        for i in range(3,self.MaxVerts):
            self.Edges[i].SetRadius(self.EdgeThickness)
             
    def AddToRenderer(self,ren):
        
        for Actor in self.Actors:
            ren.AddActor(Actor)
        for Actor in self.EdgeActors:
            ren.AddActor(Actor)
        self.added=True    
    def RemoveFromRenderer(self,ren):
        for Actor in self.Actors:
            ren.RemoveActor(Actor)
        for Actor in self.EdgeActors:
            ren.RemoveActor(Actor)
        self.added=False
    
    def setPoints(self,pointSet):
        self.NumpyCoords = numpy.zeros(pointSet.npoints*3,NPF)
        self.VTKCoords.SetVoidArray(pointSet.pos, len(self.NumpyCoords), 1) 
        self.Points.SetData(self.VTKCoords)
        
 
class polygon(vtkActor):
    def __init__(self,npoints):
        self.polygonGrid = vtkUnstructuredGrid()
        self.polygonGeometryFilter = vtkGeometryFilter()
        self.polygonNormals = vtkPolyDataNormals()
        self.polygonMapper = vtkPolyDataMapper()
        self.pointsVTK = vtkPoints()
        self.points= numpy.zeros(npoints*3,float)
        self.polys = vtkCellArray()   
        self.scalarsVTK = vtkDoubleArray()
         
        
        self.polygonGrid.SetPoints(self.pointsVTK)
        self.polygonGrid.SetCells(7,self.polys)

        self.polygonGeometryFilter.SetInput(self.polygonGrid)
        self.polygonGeometryFilter.MergingOff() 


        self.polygonNormals.SetInputConnection(self.polygonGeometryFilter.GetOutputPort())

        self.polygonNormals.ComputePointNormalsOn()    
        self.polygonNormals.ComputeCellNormalsOn()


        self.polygonMapper.SetInputConnection(self.polygonNormals.GetOutputPort())    
        self.SetMapper(self.polygonMapper) 
        self.GetProperty().SetEdgeVisibility(1)
    
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
        self.polygonMapper.SetScalarRange(range)
    
    def setScalars(self,scalars):
        
        self.initLUT(ncolors = 11,range=(0,10))
        self.LookupTable.SetTableValue(0,1.0,1.0,1.0,1.0)
        self.LookupTable.SetTableValue(1,0.5,1.0,0.0,1.0)
        self.LookupTable.SetTableValue(2,0.5,1.0,0.0,1.0)
        self.LookupTable.SetTableValue(3,1.0,1.0,1.0,1.0)
        self.LookupTable.SetTableValue(4,0.5,1.0,0.5,1.0)
        self.LookupTable.SetTableValue(5,0.0,0.0,1.0,1.0)
        self.LookupTable.SetTableValue(6,0.0,1.0,0.0,1.0)
        self.LookupTable.SetTableValue(7,1.0,0.0,0.0,1.0)
        self.LookupTable.SetTableValue(8,1.0,0.0,1.0,1.0)
        self.LookupTable.SetTableValue(9,1.0,1.0,0.5,1.0)
        self.LookupTable.SetTableValue(10,1.0,1.0,0.5,1.0)
        
        
        self.scalars = numpy.copy(scalars.astype(NPF))
        #print "scalars",self.scalars
        self.scalarsVTK.SetVoidArray(self.scalars, self.scalars.size, 1) 
        self.polygonMapper.SetLookupTable(self.LookupTable) 
        
        self.polygonGrid.GetCellData().SetScalars(self.scalarsVTK)
        
    
    def reset(self,npoints):
        self.points= numpy.zeros(npoints*3,float)
        self.pointsVTK = vtkPoints()
        self.polys = vtkCellArray() 
        
    def setPoints(self,points):
        self.points = points
        self.polygonGrid.SetPoints(self.points)
    
    def addPoint(self,n,point):
        #print n, len(self.points)/3
        self.points[n*3] = point[0]
        self.points[n*3 + 1] = point[1]
        self.points[n*3 + 2] = point[2]
        self.pointsVTK.InsertPoint(n,point[0],point[1],point[2])
    
    def addCell(self,verts):
        #print "adding cell",len(verts)
        self.polys.InsertNextCell(len(verts))  
        for vert in verts:
            self.polys.InsertCellPoint(vert)
#        self.polys.InsertCellPoint(verts[1])
#        self.polys.InsertCellPoint(verts[2])
        #print "added"
    
    def update(self):
        self.polygonGrid.SetPoints(self.pointsVTK)
        self.polygonGrid.SetCells(7,self.polys)
        self.SetMapper(self.polygonMapper) 
        
    def setPolys(self,polys):     
        self.polys = polys    
        self.polygonGrid.SetCells(7,self.polys)