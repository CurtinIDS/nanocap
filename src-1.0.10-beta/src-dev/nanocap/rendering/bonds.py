'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Aug 29 2012
Copyright Marc Robinson 2013
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

VTK Bond Actors

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
'''
from nanocap.core.globals import *
from nanocap.core.util import *
import os,sys,math,copy,random,time
import numpy
from vtk import vtkDoubleArray,vtkPoints,vtkLookupTable,vtkPolyData,vtkProgrammableGlyphFilter, \
                vtkSphereSource,vtkPolyDataMapper,vtkActor,vtkFollower,vtkVectorText,vtkTubeFilter, \
                vtkFloatArray,vtkLineSource

class bondSet(vtkActor):
    def __init__(self,nbonds,thickness  = 0.01):
        
        self.bondThickness = thickness
        self.nbonds = nbonds
        self.bondcoords = vtkFloatArray()
        self.bondScalars = vtkFloatArray()
        self.bondVectors = vtkFloatArray()
        self.bondcoords.SetNumberOfComponents(3)
        self.bondScalars.SetNumberOfComponents(1)
        self.bondcoords.SetNumberOfTuples(self.nbonds)
        self.bondScalars.SetNumberOfTuples(self.nbonds)
        self.bondVectors.SetNumberOfComponents(3)
        self.bondVectors.SetNumberOfTuples(self.nbonds)
           
        self.bondsMapper = vtkPolyDataMapper()    
        self.bondGlyphSource = vtkLineSource()
        self.bondPolyData = vtkPolyData()
        self.bondsTubes = vtkTubeFilter()
        self.bondGlyph3D = vtkProgrammableGlyphFilter()    
        self.bondpoints = vtkPoints()


    def setBondThickness(self,val):
        self.bondThickness = val
        self.bondsTubes.SetRadius(self.bondThickness)
        
    def bond_glyph(self,*args,**kargs):
        
        p= self.bondGlyph3D.GetPointId()
        #data = bondGlyph3D.GetPointData().GetScalars().GetTuple1(PointId)
        vector = self.bondGlyph3D.GetPointData().GetVectors().GetTuple3(p)
        pos = self.bondGlyph3D.GetPoint()
        self.bondGlyphSource.SetPoint1(pos)
        self.bondGlyphSource.SetPoint2(vector[0],vector[1],vector[2])
        
    
    def setBonds(self,nbonds,bonds,points):

        self.nbonds = nbonds
        self.bonds = numpy.copy(bonds)
        self.bondcoords = vtkFloatArray()
        self.bondScalars = vtkFloatArray()
        self.bondVectors = vtkFloatArray()
        self.bondcoords.SetNumberOfComponents(3)
        self.bondScalars.SetNumberOfComponents(1)
        self.bondcoords.SetNumberOfTuples(self.nbonds)
        self.bondScalars.SetNumberOfTuples(self.nbonds)
        self.bondVectors.SetNumberOfComponents(3)
        self.bondVectors.SetNumberOfTuples(self.nbonds)
        count = 0    
        #print bonds
        for i in range(0,self.nbonds):
            IDi,IDj = self.bonds[i*2], self.bonds[i*2+1]
            xi,yi,zi = points.pos[IDi*3],points.pos[IDi*3+1],points.pos[IDi*3+2]
            xj,yj,zj = points.pos[IDj*3],points.pos[IDj*3+1],points.pos[IDj*3+2]
            
            self.bondcoords.SetTuple3(count, xi,yi,zi)
            self.bondVectors.SetTuple3(count,xj,yj,zj)
            #print  posi,posj
            
            #bondScalars.SetTuple1(count,scalars[i])
            count+=1
        printl("bonds set",count)
        self.bondpoints.SetData(self.bondcoords)

        self.bondPolyData.SetPoints(self.bondpoints)
        #bondPolyData.GetPointData().SetScalars(bondScalars)
        self.bondPolyData.GetPointData().SetVectors(self.bondVectors)

        self.bondsTubes.SetInputConnection(self.bondGlyphSource.GetOutputPort())
        self.bondsTubes.SetRadius(self.bondThickness)
        self.bondsTubes.SetNumberOfSides(5)
        self.bondsTubes.UseDefaultNormalOn()
        self.bondsTubes.SetDefaultNormal(.577, .577, .577)
        #aLine.SetPoint1(x0, y0, z0)
        #aLine.SetPoint2(x1, y1, z1)

        self.bondGlyph3D.SetGlyphMethod(self.bond_glyph)
        self.bondGlyph3D.SetSource(self.bondsTubes.GetOutput())
        self.bondGlyph3D.SetInput(self.bondPolyData)

        self.bondsMapper.SetInputConnection(self.bondGlyph3D.GetOutputPort())
        #Mapper.SetLookupTable(lut)    
    
        self.SetMapper(self.bondsMapper)
        #Actor.GetProperty().SetOpacity(ColourTab.OpacitySpinBox.value()/100.0)
        self.GetProperty().SetLineWidth(self.bondThickness)
        self.GetProperty().SetColor(0,0,0)
        printl("end bonds set")
        