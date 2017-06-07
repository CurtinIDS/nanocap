'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Apr 15, 2014
Copyright Marc Robinson  2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

VTK Actors for points, bonds, rings, 
triangles for each structure


-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
'''

import os,time,platform,random,math,copy
from nanocap.core.globals import *
from nanocap.gui.settings import * 
from nanocap.core.util import *
from nanocap.rendering.renderwidgets import vtkZPlane,RenderWindowText
import nanocap.rendering.pointset as pointset
import nanocap.rendering.bonds as bonds
import nanocap.rendering.polygon as polygon
from nanocap.rendering.defaults import *

class StructureActors(object):
    def __init__(self,structure):
        #self.structureEnsemble = structureEnsemble
        self.structure = structure
        self.type=self.structure.type
        #self.schlegelframe=self.structureEnsemble.schlegelframe
        #self.vtkframe=self.structureEnsemble.vtkframe
        
        self.vtkframe = {}
        self.vtkframe["3D"] =self.structure.render_window.vtkframe
        self.vtkframe["Schlegel"] =self.structure.render_window.schlegelframe
        
        self.pointKeys = POINTKEYS
        
        self.pointActors={}
        self.pointRadius={}
        self.pointColors={}
        self.pointBox={}
        self.pointLabels={}        
        
        for key in self.pointKeys:
            self.pointActors[key] = pointset.PointSet(RADIUS[key],
                                                      COLORS[key])
            
            self.pointActors[key].initArrays(self.structure.get_points(key))
            
            self.pointRadius[key] = RADIUS[key]
            self.pointColors[key] = COLORS[key]
            self.pointBox[key] = False
            self.pointLabels[key] = False
            
            self.pointActors[key+"_S"] = pointset.PointSet(RADIUS[key],
                                                      COLORS[key])
            self.pointActors[key+"_S"].initArrays(self.structure.get_points(key+"_S"))
            self.pointLabels[key+"_S"] = False
            
#             self.pointRadius[key+"_S"] = RADIUS[key]
#             self.pointColors[key+"_S"] = COLORS[key]
#             self.pointBox[key+"_S"] = False
#             self.pointLabels[key+"_S"] = False
            
            
        self.triangleMesh = polygon.polygon(0)
        self.carbonBonds = bonds.bondSet(0,thickness=BOND_THICKNESS) 
        self.carbonRings = polygon.polygonSet(MaxVerts=0,EdgeThickness=BOND_THICKNESS) 
        self.carbonRings_S = polygon.polygonSet(MaxVerts=0,EdgeThickness=BOND_THICKNESS) 
        
        self.setup_triangles()
        self.setup_carbon_bonds()
        self.setup_carbon_rings()
        self.setup_carbon_rings_S()
        
    def update_actors(self):
        for key in self.pointKeys:
            self.pointActors[key].initArrays(self.structure.get_points(key))
            self.pointActors[key].update()
            self.pointActors[key+"_S"].initArrays(self.structure.get_points(key+"_S"))
            self.pointActors[key+"_S"].update()
            
        self.setup_triangles()
        self.setup_carbon_bonds()
        self.setup_carbon_rings()
        self.setup_carbon_rings_S()
        for key,frame in self.vtkframe.items():
            frame.refreshWindow()
            
    def setup_carbon_rings_S(self):
        if not (self.structure.has_carbon_rings):
            printl("structure does not have carbon rings")
            return
        if not (self.structure.has_schlegel):
            printl("structure does not have schlegel carbon rings")
            return
        
        
        self.MaxVerts_S = self.structure.schlegel_ring_info['MaxVerts']
        self.Rings_S = numpy.copy(self.structure.schlegel_ring_info['Rings'])
        self.VertsPerRingCount_S = numpy.copy(self.structure.schlegel_ring_info['VertsPerRingCount'])
        
        added = self.carbonRings_S.added
        try:
            self.carbonRings_S.RemoveFromRenderer(self.vtkframe['Schlegel'].VTKRenderer)
            self.vtkframe['Schlegel'].refreshWindow()
        except:
            pass
        
        self.carbonRings_S = polygon.polygonSet(MaxVerts=self.MaxVerts_S,
                                  EdgeThickness = BOND_THICKNESS)
        

        
        self.carbonRings_S.setVerts(self.structure.schlegel_carbon_lattice_full,self.Rings_S,self.VertsPerRingCount_S)

        if(added):
            self.carbonRings_S.AddToRenderer(self.vtkframe['Schlegel'].VTKRenderer) 
                
    def setup_carbon_rings(self):
        if not (self.structure.has_carbon_rings):
            printl("structure does not have carbon rings")
            return
        
        self.MaxVerts = self.structure.ring_info['MaxVerts']
        self.Rings = numpy.copy(self.structure.ring_info['Rings'])
        self.VertsPerRingCount = numpy.copy(self.structure.ring_info['VertsPerRingCount'])


        added = self.carbonRings.added
        try:
            self.carbonRings.RemoveFromRenderer(self.vtkframe['3D'].VTKRenderer)
            self.vtkframe['3D'].refreshWindow()
        except:
            pass
        
        self.carbonRings = polygon.polygonSet(MaxVerts=self.MaxVerts,
                                  EdgeThickness = BOND_THICKNESS)
        
        self.carbonRings.setVerts(self.structure.carbon_lattice,self.Rings,self.VertsPerRingCount)    
        
        if(added):
            self.carbonRings.AddToRenderer(self.vtkframe['3D'].VTKRenderer) 
        
    def setup_carbon_bonds(self):
        if not (self.structure.has_carbon_bonds):
            printl("structure does not have carbon bonds")
        self.structure.calculate_carbon_bonds()
            #return
        self.bonds =  numpy.copy(self.structure.bonds)
        self.nbonds = self.structure.nbonds
        try:
            self.carbonBonds.setBonds(self.nbonds,self.bonds,self.structure.carbon_lattice)
        except: 
            self.carbonBonds = bonds.bondSet(self.nbonds,thickness=BOND_THICKNESS) 
            self.carbonBonds.setBonds(self.nbonds,self.bonds,self.structure.carbon_lattice) 
        
        
    def setup_triangles(self):
        if not (self.structure.has_triangles):
            printl("structure has not been triangualed, cannot render")
            return
        pointSet = self.structure.dual_lattice
        
        
        
        self.ntriangles = self.structure.ntriangles
        self.verts = numpy.copy(self.structure.vertlist)
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
    
    
    
    def toggle_carbon_rings(self,flag):
        if not (self.structure.has_carbon_rings):
            printl("structure does not have carbon bonds, they must be calculated")
        if(flag):self.carbonRings.AddToRenderer(self.vtkframe['3D'].VTKRenderer) 
        else: self.carbonRings.RemoveFromRenderer(self.vtkframe['3D'].VTKRenderer) 
        
        if(flag):self.carbonRings_S.AddToRenderer(self.vtkframe['Schlegel'].VTKRenderer) 
        else: self.carbonRings_S.RemoveFromRenderer(self.vtkframe['Schlegel'].VTKRenderer) 
        self.vtkframe['Schlegel'].refreshWindow()
        self.vtkframe['3D'].refreshWindow()
        
    def toggle_carbon_bonds(self,flag):
        if not (self.structure.has_carbon_bonds):
            printl("structure does not have carbon bonds, they must be calculated")
        if(flag):self.vtkframe['3D'].VTKRenderer.AddActor(self.carbonBonds)
        else: self.vtkframe['3D'].VTKRenderer.RemoveActor(self.carbonBonds)
        self.vtkframe['3D'].refreshWindow()
    
    def set_carbon_bond_thickness(self,w):
        self.carbonBonds.setBondThickness(w)
        self.vtkframe['3D'].refreshWindow()
        
    def toggle_triangles(self,flag):
        if(flag):self.vtkframe['3D'].VTKRenderer.AddActor(self.triangleMesh)
        else: self.vtkframe['3D'].VTKRenderer.RemoveActor(self.triangleMesh)
        self.vtkframe['3D'].refreshWindow()   
    
#     def toggle_point_labels(self,flag,key,frame="3D"):
#         if(flag): self.pointActors[key].addLabels(self.vtkframe[frame].VTKRenderer)
#         else: self.pointActors[key].removeLabels(self.vtkframe[frame].VTKRenderer)
#         self.vtkframe[frame].refreshWindow()
#     
#     def toggle_point_box(self,flag,key,frame="3D"):
#         if(flag): self.pointActors[key].addBoundingBox(self.vtkframe[frame].VTKRenderer)
#         else: self.pointActors[key].removeBoundingBox(self.vtkframe[frame].VTKRenderer)
#         self.vtkframe[frame].refreshWindow()
#         
#     def set_point_color(self,r,g,b,key,frame="3D"):
#         self.pointActors[key].col=(float(r)/255.,float(g)/255.,float(b)/255.)            
#         self.pointActors[key].update() 
#         self.vtkframe[frame].refreshWindow()
#         
#     def set_point_radius(self,rad,key,frame="3D"):
#         self.pointActors[key].rad=rad
#         self.pointActors[key].update() 
#         self.vtkframe[frame].refreshWindow()
#     
#     def toggle_points(self,flag,key,frame="3D"):
#         if(flag):self.add_points(key,frame=frame)
#         else:self.remove_points(key,frame=frame)
#         
#     def add_points(self,key,frame="3D"):
#         printl(key,self.structure.object.get_points(key))
#         self.pointActors[key].initArrays(self.structure.object.get_points(key))
#         self.pointActors[key].addToRenderer(self.vtkframe[frame].VTKRenderer)
#         self.vtkframe[frame].refreshWindow()
#         
#     def remove_points(self,key,frame="3D"):
#         self.pointActors[key].removeFromRenderer(self.vtkframe[frame].VTKRenderer)    
#         self.vtkframe[frame].refreshWindow()    

    def toggle_point_labels(self,flag,key,frame="3D"):
        if(flag):self.add_labels(key,frame=frame)
        else:self.remove_labels(key,frame=frame)
#         if(flag): self.pointActors[key].addLabels(self.vtkframe[frame].VTKRenderer)
#         else: self.pointActors[key].removeLabels(self.vtkframe[frame].VTKRenderer)
#         self.vtkframe[frame].refreshWindow()
    def add_labels(self,key,frame="3D"):
        printl(key,self.structure.get_points(key),frame)
        self.pointActors[key].addLabels(self.vtkframe[frame].VTKRenderer)
        self.vtkframe[frame].refreshWindow()
        
    def remove_labels(self,key,frame="3D"):
        self.pointActors[key].removeLabels(self.vtkframe[frame].VTKRenderer)
        self.vtkframe[frame].refreshWindow() 
    
    def toggle_point_box(self,flag,key,frame="3D"):
        if(flag):self.add_box(key,frame=frame)
        else:self.remove_box(key,frame=frame)
#         if(flag): self.pointActors[key].addLabels(self.vtkframe[frame].VTKRenderer)
#         else: self.pointActors[key].removeLabels(self.vtkframe[frame].VTKRenderer)
#         self.vtkframe[frame].refreshWindow()
    def add_box(self,key,frame="3D"):
        printl(key,self.structure.get_points(key),frame)
        self.pointActors[key].addBoundingBox(self.vtkframe[frame].VTKRenderer)
        self.vtkframe[frame].refreshWindow()
        
    def remove_box(self,key,frame="3D"):
        self.pointActors[key].removeBoundingBox(self.vtkframe[frame].VTKRenderer)
        self.vtkframe[frame].refreshWindow() 
#     
#     def toggle_point_box(self,flag,key):
#         self.pointBox[key] = flag
#         self.update_pointActors()
        
#         if(flag): self.pointActors[key].addBoundingBox(self.vtkframe[frame].VTKRenderer)
#         else: self.pointActors[key].removeBoundingBox(self.vtkframe[frame].VTKRenderer)
#         self.vtkframe[frame].refreshWindow()
        
    def set_point_color(self,r,g,b,key):
        self.pointColors[key] = (float(r)/255.,float(g)/255.,float(b)/255.)  
        self.update_color()

    def set_point_radius(self,rad,key):
        self.pointRadius[key] = rad
        self.update_radius()
    
    def update_color(self):
        for key in self.pointKeys:
            self.pointActors[key].col = self.pointColors[key]
            self.pointActors[key].update()
            self.pointActors[key+"_S"].col = self.pointColors[key]
            self.pointActors[key+"_S"].update()
        for key,frame in self.vtkframe.items():
            frame.refreshWindow()
        
    def update_radius(self):
        for key in self.pointKeys:
            self.pointActors[key].rad = self.pointRadius[key]
            self.pointActors[key].update()
            self.pointActors[key+"_S"].rad = self.pointRadius[key]
            self.pointActors[key+"_S"].update()
        for key,frame in self.vtkframe.items():
            frame.refreshWindow()
        
    def toggle_points(self,flag,key,frame="3D"):
        if(flag):self.add_points(key,frame=frame)
        else:self.remove_points(key,frame=frame)
            
    def add_points(self,key,frame="3D"):
        printl(key,self.structure.get_points(key),frame)
        self.pointActors[key].addToRenderer(self.vtkframe[frame].VTKRenderer)
        self.vtkframe[frame].refreshWindow()
        
    def remove_points(self,key,frame="3D"):
        self.pointActors[key].removeFromRenderer(self.vtkframe[frame].VTKRenderer)    
        self.vtkframe[frame].refreshWindow()   
        
        
        