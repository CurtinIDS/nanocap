'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Oct 10 2013
Copyright Marc Robinson 2013
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

General Render Widgets

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
'''
from nanocap.core.globals import *
from nanocap.core.util import *
import os,sys,math,copy,random,time
import numpy
from vtk import vtkDoubleArray,vtkPoints,vtkLookupTable,vtkPolyData,vtkProgrammableGlyphFilter, \
                vtkSphereSource,vtkPolyDataMapper,vtkActor,vtkFollower,vtkVectorText,vtkTubeFilter, \
                vtkFloatArray,vtkLineSource,vtkTextActor,vtkPlaneSource

class CellMatrixActor(object):
    def __init__(self):        
        self.DimTexts = []
        self.LengthTexts = []
        self.LineActors = []
        
        self.col = (0,0,0)
        self.DimensionsOffset = 2.0
        for i in range(0,12):
            self.addLine((0,0,0),(0.1,0.1,0.1))
        
        for i in range(0,4):
            self.DimTexts.append(FollowerText("",0,[0,0,0],0))    
        for i in range(0,3):
            self.LengthTexts.append(FollowerText("",0,[0,0,0],0)) 
         
    def set(self,CM,Orign,R,G,B, units= ""):
        self.units = units
        self.a=numpy.array([CM[0],CM[1],CM[2]])
        self.b=numpy.array([CM[3],CM[4],CM[5]])
        self.c=numpy.array([CM[6],CM[7],CM[8]])
        self.Origin = Orign
        self.col = (R,G,B)
        #self.scale=int((numpy.max((magnitude(a),magnitude(b),magnitude(c)))/500) +1.0)
        self.scale=numpy.max((magnitude(self.a),
                              magnitude(self.b),
                              magnitude(self.c)))/40
                              
                              
        
        self.DimensionsOffset*=self.scale
        #printl("setting cell",self.a,self.b,self.c)
        #printl("setting scale",self.scale)
        #printl("setting Origin",self.Origin)
        points = []
        
        points.append((Orign,self.a+Orign))
        points.append((Orign,self.b+Orign))
        points.append((Orign,self.c+Orign))
        points.append(((self.a+self.b+self.c)+Orign,(self.a+self.b)+Orign))
        points.append(((self.a+self.b+self.c)+Orign,(self.a+self.c)+Orign))
        points.append(((self.a+self.b+self.c)+Orign,(self.c+self.b)+Orign))
        points.append((self.b+Orign,self.c+self.b+Orign))
        points.append((self.b+Orign,self.a+self.b+Orign))
        points.append((self.a+Orign,self.c+self.a+Orign))
        points.append((self.a+Orign,self.a+self.b+Orign))
        points.append((self.c+Orign,self.c+self.b+Orign))
        points.append((self.c+Orign,self.a+self.c+Orign))     
        i = 0
        for Actor in self.LineActors:
            Actor.set_pos(points[i][0],points[i][1])
            if(i==0):Actor.set_col((1,0,0))
            elif(i==1):Actor.set_col((0,1,0))
            elif(i==2):Actor.set_col((0,0,1))
            else:Actor.set_col(self.col)
            i+=1
        
        for i in range(0,4):
            self.DimTexts[i].Actor.SetScale(self.scale,self.scale,self.scale)  
        for i in range(0,3):
            self.LengthTexts[i].Actor.SetScale(self.scale,self.scale,self.scale)  
        
        self.setupDimActors()    
        self.setupLengthActors() 
        
    def setupLengthActors(self):
        ThisText = self.LengthTexts[0]
        string = str("%.2f %s" % (magnitude(self.a),self.units))
        p1 = self.b + self.c + self.Origin
        p2 = self.a + self.b + self.c + self.Origin
        mp = (p2-p1)/2.0 + p1
        ThisText.updateText(string)  
        ThisText.updatePosition(mp,(0,self.DimensionsOffset,self.DimensionsOffset))  

        ThisText = self.LengthTexts[1]
        string = str("%.2f %s" % (magnitude(self.b),self.units))
        p1 = self.c + self.a + self.Origin
        p2 = self.a + self.b + self.c + self.Origin
        mp = (p2-p1)/2.0 + p1
        ThisText.updateText(string)  
        ThisText.updatePosition(mp,(self.DimensionsOffset,0,self.DimensionsOffset))    
        
        ThisText = self.LengthTexts[2]
        string = str("%.2f %s" % (magnitude(self.c),self.units))
        p1 = self.b + self.a + self.Origin
        p2 = self.a + self.b + self.c + self.Origin
        mp = (p2-p1)/2.0 + p1
        ThisText.updateText(string)  
        ThisText.updatePosition(mp,(self.DimensionsOffset,self.DimensionsOffset,0))  
                   
    def setupDimActors(self):
        OriginText = self.DimTexts[0]
        string = str("%.2f,%.2f,%.2f" % (self.Origin[0],self.Origin[1],self.Origin[2]))
        OriginText.updateText(string)    
        OriginText.updatePosition(self.Origin,(-self.DimensionsOffset,-self.DimensionsOffset,-self.DimensionsOffset))     
        #printl(string)
        #printl(self.Origin)
        for i in range(0,3):
            ThisText = self.DimTexts[i+1]
            if(i==0):
                string = str("%.2f,%.2f,%.2f" % (self.a[0]+self.Origin[0],
                                                 self.a[1]+self.Origin[1],
                                                 self.a[2]+self.Origin[2]))
                pos = self.a+self.Origin
                r,g,b = 1,0,0
            if(i==1):
                string = str("%.2f,%.2f,%.2f" % (self.b[0]+self.Origin[0],
                                                 self.b[1]+self.Origin[1],
                                                 self.b[2]+self.Origin[2]))
                pos = self.b+self.Origin
                r,g,b = 0,1,0
            if(i==2):
                string = str("%.2f,%.2f,%.2f" % (self.c[0]+self.Origin[0],
                                                 self.c[1]+self.Origin[1],
                                                 self.c[2]+self.Origin[2]))
                pos = self.c+self.Origin
                r,g,b = 0,0,1
            ThisText.updateText(string)  
            ThisText.updatePosition(pos,(-self.DimensionsOffset,-self.DimensionsOffset,-self.DimensionsOffset))      
            ThisText.updateColour(r,g,b)
            #printl(string)
            #printl(pos)

    def removeFromRenderer(self,ren):
        for Actor in self.LineActors:
            ren.RemoveActor(Actor)
        for Text in self.DimTexts:
            Text.removeFromRenderer(ren)
        for Text in self.LengthTexts:
            Text.removeFromRenderer(ren)   
                
    def addToRenderer(self,ren,showDimensions,showLengths):   
        #printl("addToRenderer",showDimensions)      
        for Actor in self.LineActors:
            ren.AddActor(Actor)   
        if(showDimensions==True):
            self.setupDimActors()    
            
            for Text in self.DimTexts:
                #printl(Text)
                Text.addToRenderer(ren)
            
        if(showLengths==True):    
            self.setupLengthActors() 
            for Text in self.LengthTexts:
                Text.addToRenderer(ren)   
                 
    def removeLengthScalesFromRenderer(self,ren):
        for Text in self.LengthTexts:
            Text.addToRenderer(ren)   
            
    def removeDimensionsFromRenderer(self,ren):
        for Text in self.DimTexts:
            Text.addToRenderer(ren)
                        
    def addLine(self,a,b):    
        lineactor = LineActor(a,b,self.col)   
        self.LineActors.append(lineactor)
        printd("self.LineActors",self.LineActors)

class FollowerText(object):
    def __init__(self,text,scale,pos,offset):
        self.Actor = vtkFollower()
        self.Actor.SetScale(scale,scale,scale)  
        
        p = (pos[0]+offset,
               pos[1]+offset,
               pos[2]+offset)
        
        self.Actor.GetProperty().SetDiffuseColor(0,0,0)       
        self.Actor.SetPosition(p)
        self.Label = vtkVectorText()
        self.Label.SetText(text)
        self.Mapper = vtkPolyDataMapper()
        self.Mapper.SetInputConnection(self.Label.GetOutputPort())
        self.Actor.SetMapper(self.Mapper)
    
    def updateColour(self,r,g,b):
        self.Actor.GetProperty().SetDiffuseColor(r,g,b)
        
    def updateText(self,text):
        self.Label.SetText(text)
        self.Mapper = vtkPolyDataMapper()
        self.Mapper.SetInputConnection(self.Label.GetOutputPort())
        self.Actor.SetMapper(self.Mapper)
    
    def updatePosition(self,pos,offset):
        p = (pos[0]+offset[0],
               pos[1]+offset[1],
               pos[2]+offset[2])
        self.Actor.SetPosition(p)
        
    def removeFromRenderer(self,ren):
        ren.RemoveActor(self.Actor)   
         
    def addToRenderer(self,ren):
        
        printl("adding follower text",self.Label.GetText())
        self.Actor.SetCamera(ren.GetActiveCamera())
        ren.AddActor(self.Actor)       



class RenderWindowText(vtkTextActor):
    def __init__(self,inputtext,Size,x,y,r,g,b):
        self.Input =  inputtext
        self.Size =  Size
        self.x =  x
        self.y =  y    
        self.SetDisplayPosition(self.x, self.y)
        self.SetInput(self.Input)
        #textActor.UseBorderAlignOn
        self.GetPosition2Coordinate().SetCoordinateSystemToNormalizedViewport()
        #textActor.GetPosition2Coordinate().SetValue(0.6, 0.4)
        tprop = self.GetTextProperty()
        tprop.SetFontSize(self.Size)
        tprop.SetFontFamilyToArial()
        tprop.SetFontFamilyToTimes()
        tprop.SetJustificationToLeft()
        tprop.SetVerticalJustificationToTop()
        tprop.BoldOn()
        #tprop.ItalicOn()
        #tprop.ShadowOn()
        #tprop.SetShadowOffset(2,2)
        tprop.SetColor(r,g,b)
    def change_input(self,inputtext1):
        self.Input = inputtext1
        self.SetInput(self.Input)
    def change_pos(self,x,y):
        self.x =  x
        self.y =  y    
        self.SetDisplayPosition(self.x, self.y)

class LineActor(vtkActor):
    def __init__(self,p0,p1,col):
        self.p0 = p0
        self.p1 = p1
        self.source = vtkLineSource()
        self.source.SetPoint1(p0)
        self.source.SetPoint2(p1)

        self.col = col
        self.mapper = vtkPolyDataMapper()
        self.TubeFilter = vtkTubeFilter()
        self.TubeFilter.SetInputConnection(self.source.GetOutputPort())
        self.TubeFilter.SetRadius(0.01)
        self.TubeFilter.SetNumberOfSides(20)
        self.TubeFilter.CappingOn()

        self.mapper.SetInput(self.source.GetOutput())

        self.SetMapper(self.mapper)
        self.GetProperty().SetColor(self.col)
        
    def set_pos(self,p0,p1):
        self.p0 = p0
        self.p1 = p1
        self.source.SetPoint1(self.p0)
        self.source.SetPoint2(self.p1)

    def set_col(self,col):
        self.col = col
        self.GetProperty().SetColor(col)
        
class Plane(vtkActor):    
    def __init__(self,origin,p1,p2,n,center,col):    
        self.SlicePlaneSource = vtkPlaneSource()
        self.SlicePlaneSource.SetOrigin(origin)    
        self.SlicePlaneSource.SetPoint1(p1)    
        self.SlicePlaneSource.SetPoint2(p1)
        self.SlicePlaneSource.SetNormal(n)
        self.SlicePlaneSource.SetCenter(center)
        self.SlicePlaneSource.SetXResolution(100)
        self.SlicePlaneSource.SetYResolution(100)
        
        self.SliceMapper = vtkPolyDataMapper()
        self.SliceMapper.SetInputConnection(self.SlicePlaneSource.GetOutputPort())

        self.SetMapper(self.SliceMapper)
        self.GetProperty().SetColor(col)
        #self.SlicePlane.GetProperty().SetSpecular(.4)
        #self.SlicePlane.GetProperty().SetSpecularPower(10)
        self.GetProperty().SetOpacity(0.7)
        #self.SlicePlane.GetProperty().SetLineWidth(2.0)
        
    def move(self,center):
        self.SlicePlaneSource.SetCenter(center)

class vtkZPlane(vtkActor):    
    def __init__(self,z,width=1.5):    
        self.SlicePlaneSource = vtkPlaneSource()
        self.SlicePlaneSource.SetOrigin(-width,-width,z)    
        self.SlicePlaneSource.SetPoint1(width,-width,z)    
        self.SlicePlaneSource.SetPoint2(-width,width,z)
        self.SlicePlaneSource.SetNormal(0,0,1)
        self.SlicePlaneSource.SetCenter(0,0,z)
        self.SlicePlaneSource.SetXResolution(100)
        self.SlicePlaneSource.SetYResolution(100)
        
        self.SliceMapper = vtkPolyDataMapper()
        self.SliceMapper.SetInputConnection(self.SlicePlaneSource.GetOutputPort())

        self.SetMapper(self.SliceMapper)
        self.GetProperty().SetColor(1,0,0)
        #self.SlicePlane.GetProperty().SetSpecular(.4)
        #self.SlicePlane.GetProperty().SetSpecularPower(10)
        self.GetProperty().SetOpacity(0.7)
        #self.SlicePlane.GetProperty().SetLineWidth(2.0)
    def move(self,z):
        self.SlicePlaneSource.SetCenter(0,0,z)
