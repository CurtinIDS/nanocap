'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: July 24 2012
Copyright Marc Robinson 2013
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

Fullerene base class.

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
'''
from nanocap.core import globals
from nanocap.core.globals import *
import os,sys,math,copy,random,time,ctypes
import numpy
import nanocap.objects.points as points
from nanocap.core import triangulation
from nanocap.core import ringcalculator 
 
from nanocap.core.util import *

from nanocap.clib import clib_interface
clib = clib_interface.clib

class Fullerene(object):
    def __init__(self):
        self.thomsonPoints = points.Points("Fullerene Dual Lattice Points")
        self.thomsonPoints.initArrays(0)
        self.thomsonPoints.freeflags = numpy.ones(0,NPI)
        self.thomsonPoints.freeflagspos = numpy.ones(0,NPF)
        
        self.thomsonPoints.dampflags = numpy.zeros(0,NPI)
        self.thomsonPoints.dampflagspos = numpy.zeros(0,NPF)
        self.carbonAtoms = None

    
    def __repr__(self):
        twidth = 80
        
        out = ""
        sepformat = "{0:=^"+str(twidth)+"} \n"
        
        col1 = "{0:<"+str(twidth)+"} \n"
        col1h = "{0:-^"+str(twidth)+"} \n"
        col2 = "{0:<"+str(int(twidth/2))+"} {1:<"+str(int(twidth/2))+"}\n"
        col3 = "{0:<"+str(int(twidth/3))+"} {1:<"+str(int(twidth/3))+"} {2:<"+str(int(twidth/3))+"}\n"
        col4 = "{0:<"+str(int(twidth/4))+"} {1:<"+str(int(twidth/4))+"} {2:<"+str(int(twidth/4))+"} {3:<"+str(int(twidth/4))+"}\n" 
        
        out += sepformat.format("C"+str(self.carbonAtoms.npoints)+"_Fullerene")

        
        out += col2.format("N_dual_lattice_points",self.thomsonPoints.npoints)   
        out += col2.format("N_dual_lattice_energy",self.thomsonPoints.FinalEnergy)
         
        out += col2.format("N_carbon_atoms",self.carbonAtoms.npoints)
        try:
            out += col2.format("carbon_lattice_scale",self.carbonAtoms.FinalScale)
            out += col2.format("carbon_lattice_scaled_energy",str(self.carbonAtoms.FinalScaleEnergy)+" eV")
            out += col2.format("carbon_lattice_energy",str(self.carbonAtoms.FinalEnergy)+" eV")
            out += col2.format("carbon_lattice_energy_per_atom",str(self.carbonAtoms.FinalEnergy/self.carbonAtoms.npoints)+" eV")
        except:pass
        
        out += col2.format("average_radius",str(self.radius)+" +- "+str(self.radius_std))
        out += col2.format("min_radius",self.radius_min)
        out += col2.format("max_radius",self.radius_max)
        try:out += col2.format("constrained_average_radius",str(self.constrained_radius)+" +- "+str(self.constrained_radius_std))
        except:pass
        
        out += col2.format("surface_area",self.surfaceArea)
        out += col2.format("volume",self.volume)
        out += col2.format("sphericity",self.sphericity)
        
#        try:out += col2.format("unconstrained_average_radius",str(self.unconstrained_radius)+" +- "+str(self.unconstrained_radius_std))
#        except:pass
    
        out += col1h.format("ring_stats")
        for i in range(3,len(self.ringCount)):
            if(i==5):
                out += col2.format("number_of_"+str(i)+"-agons ",str(self.ringCount[i])+" IP "+str(self.isolatedPentagons))
            else:
                out += col2.format("number_of_"+str(i)+"-agons ",self.ringCount[i])                    
           
        out += col2.format("%_6-agons",self.percHex)    
        
        
        
        out += sepformat.format("")
        return out 
     
    def calcInfo(self):
        
        self.radius,self.radius_std,self.radius_min,self.radius_max = self.calcAverageRadius(self.carbonAtoms.npoints,self.carbonAtoms.pos)
       
        
        printl("fullerene average radius",self.radius,"+-",self.radius_std)
        
        try:
            self.constrained_radius,self.constrained_radius_std,min,max = self.calcAverageRadius(self.carbonAtoms.npoints,self.carbonAtoms.constrained_pos)
            printl("fullerene constrained average radius",self.constrained_radius,"+-",self.constrained_radius_std)
        except:pass
        
#        try:
#            self.unconstrained_radius,self.unconstrained_radius_std = self.calcAverageRadius(self.carbonAtoms.npoints,self.carbonAtoms.unconstrained_pos)
#            printl("fullerene unconstrained average radius",self.unconstrained_radius,"+-",self.unconstrained_radius_std)
#        except:pass
        
        self.calculateSurfaceAreaVolume()
        
        self.sphericity = (math.pow(math.pi,1.0/3.0) * math.pow((6.0*self.volume),2.0/3.0))/self.surfaceArea
        
        printl("fullerene sphericity",self.sphericity)
        
    
    def calculateCarbonRings(self, MaxNebs = 3,MaxVerts= 9):
        outdict = ringcalculator.calculate_rings(self.carbonAtoms,MaxNebs = MaxNebs,MaxVerts=MaxVerts)
        
        for key, val in outdict.items():
            #print key,outdict[key],"self."+key+" = outdict[key]"
            exec "self."+key+" = outdict[key]"
        
        return outdict
            
    def calculateSurfaceAreaVolume(self):
        #self.verts, self.ntriangles, self.surfaceArea, self.volume =  triangulation.triangulationVolume(self.carbonAtoms)
        #self.verts = self.verts[0:self.ntriangles*3]
        
        
        #printl("self.ntriangles",self.ntriangles)
        
        printl("using nrings",self.nrings,"to determine area and volume")
        '''
        was going to retriangulate the carbon atoms, but there is no need since the
        rings have been calculated. Use these along with the normals to determine the
        volume using Gauss' thereom.    
        '''
        stime = time.time()
        self.surfaceArea,self.volume = ringcalculator.calculate_volume_from_rings(self.carbonAtoms,
                                                                                  self.nrings,
                                                                                  self.MaxVerts,
                                                                                  self.Rings,
                                                                                  self.VertsPerRingCount)
        
        
        printl("C fullerene surfaceArea",self.surfaceArea,"volume", self.volume)
        printl("C time for vol calc",time.time()-stime)
        
#        stime = time.time()
#        self.surfaceArea = 0
#        self.volume = 0
#        for i in range(0,self.nrings):
#            #print "ring",i,"verts",self.VertsPerRingCount[i]
#
#            v1,v2,v3 = self.Rings[i*self.MaxVerts],self.Rings[i*self.MaxVerts+1],self.Rings[i*self.MaxVerts+2]        
#            p1 = numpy.array([self.carbonAtoms.pos[v1*3],
#                              self.carbonAtoms.pos[v1*3+1],
#                              self.carbonAtoms.pos[v1*3+2]])    
#            p2 = numpy.array([self.carbonAtoms.pos[v2*3],
#                              self.carbonAtoms.pos[v2*3+1],
#                              self.carbonAtoms.pos[v2*3+2]])    
#            p3 = numpy.array([self.carbonAtoms.pos[v3*3],
#                              self.carbonAtoms.pos[v3*3+1],
#                              self.carbonAtoms.pos[v3*3+2]])    
#            
#            
#            #norm = unit_normal(p1,p2,p3)
#            
#            #norm = normalise(numpy.cross(p1-p3,p2-p3))
#            norm = normalise(numpy.cross(p3-p1,p3-p2))
#                        
#            totxyz = numpy.zeros(3,NPF)
#            
#            center = numpy.zeros(3,NPF)
#            for j in range(0,self.VertsPerRingCount[i]): 
#                #print "v",j,self.Rings[i*self.MaxVerts +j]
#                
#                jindex0 = j
#                jindex1 = ((j+1) % self.VertsPerRingCount[i])
#                v1,v2 = self.Rings[i*self.MaxVerts+jindex0],self.Rings[i*self.MaxVerts+jindex1]
#                        
#                p1 = numpy.array([self.carbonAtoms.pos[v1*3],
#                                  self.carbonAtoms.pos[v1*3+1],
#                                  self.carbonAtoms.pos[v1*3+2]])    
#                
#                p2 = numpy.array([self.carbonAtoms.pos[v2*3],
#                                  self.carbonAtoms.pos[v2*3+1],
#                                  self.carbonAtoms.pos[v2*3+2]])    
#                
#                cp = numpy.cross(p1,p2)
#                
#                center+= p1/self.VertsPerRingCount[i]
#                
#                #print jindex0,jindex1,p1,p2,cp
#                totxyz+=cp
#            
#            
#            area = abs(numpy.dot(totxyz,norm)/2.0)
#            
#            self.surfaceArea += area
#            
#            self.volume += abs(center[0] * norm[0] * area)
#            
#            #print "area of ring",abs(area/2.0)
#                
#        #self.surfaceArea,self.volume = 1,1
#        printl("fullerene surfaceArea",self.surfaceArea,"volume", self.volume)
#        printl("time for vol calc",time.time()-stime)
            
    def calcAverageRadius(self,npoints,pos):    
        xc = pos[0::3]
        yc = pos[1::3]
        zc = pos[2::3] 
        np = npoints
         
        com = numpy.array([numpy.sum(xc)/np,numpy.sum(yc)/np,numpy.sum(zc)/np])
        
        xd = xc-com[0]
        yd = yc-com[1]
        zd = zc-com[2]
        
        
        radii = numpy.sqrt(xd*xd + yd*yd + zd*zd)
        return numpy.average(radii),numpy.std(radii),numpy.min(radii),numpy.max(radii)
     
            
    def setupCarbonAtoms(self,npoints,point_rad,point_col,sphere_rad,
                           inputpoints=None,seed=None,nfixequator=0,fixpole=False):
            
        self.carbonAtoms = points.Points("Fullerene Carbon Atoms")
        
        self.carbonAtoms.initArrays(npoints)
        self.carbonAtoms.freeflags = numpy.ones(npoints,NPI)
        self.carbonAtoms.freeflagspos = numpy.ones(npoints*3,NPF)
        
        self.carbonAtoms.dampflags = numpy.zeros(npoints,NPI)
        self.carbonAtoms.dampflagspos = numpy.zeros(npoints*3,NPF)
                
        if(inputpoints==None):
            clib.setup_random_points_on_sphere(ctypes.c_int(npoints),
                                        ctypes.c_int(seed),
                                        ctypes.c_int(0),
                                        ctypes.c_double(sphere_rad),
                                        self.carbonAtoms.pos.ctypes.data_as(ctypes.POINTER(ctypes.c_double)))
            
            
            self.carbonAtoms.pos[0*3] = sphere_rad
            self.carbonAtoms.pos[0*3+1] = 0.0   
            self.carbonAtoms.pos[0*3+2] = 0.0  
            
            nfixedtoequator = 1+nfixequator
            for i in range(0,nfixedtoequator):    
                self.carbonAtoms.freeflagspos[i*3+2] = 0
                self.carbonAtoms.pos[i*3+2] = self.carbonAtoms.pos[0*3+2] 
        else:
            #for i in range(0,npoints):
            self.carbonAtoms.pos = numpy.copy(inputpoints)
            
        nfixedtoequator = 1+nfixequator    
        for i in range(0,nfixedtoequator):    
                self.carbonAtoms.freeflagspos[i*3+2] = 0    
        
        if(fixpole):
            self.carbonAtoms.freeflags[0] = 0
            self.carbonAtoms.freeflagspos[0*3] = 0
            self.carbonAtoms.freeflagspos[0*3+1] = 0    
            self.carbonAtoms.freeflagspos[0*3+2] = 0  
   
        
            
        self.carbonAtoms.initial_pos = numpy.copy(self.carbonAtoms.pos)   
         
    def setupThomsonPoints(self,npoints,point_rad,point_col,sphere_rad,
                           inputpoints=None,seed=None,nfixequator=0,fixpole=False):   
        
        printl("setup Thomson points seed" ,seed) 
        self.thomsonPoints = points.Points("Fullerene Dual Lattice Points")
        
        self.thomsonPoints.initArrays(npoints)
        self.thomsonPoints.freeflags = numpy.ones(npoints,NPI)
        self.thomsonPoints.freeflagspos = numpy.ones(npoints*3,NPF)
        
        self.thomsonPoints.dampflags = numpy.zeros(npoints,NPI)
        self.thomsonPoints.dampflagspos = numpy.zeros(npoints*3,NPF)
                
        if(inputpoints==None):
            clib.setup_random_points_on_sphere(ctypes.c_int(npoints),
                                        ctypes.c_int(seed),
                                        ctypes.c_int(0),
                                        ctypes.c_double(sphere_rad),
                                        self.thomsonPoints.pos.ctypes.data_as(ctypes.POINTER(ctypes.c_double)))
            
            
            self.thomsonPoints.pos[0*3] = 0.0
            self.thomsonPoints.pos[0*3+1] = 0.0   
            self.thomsonPoints.pos[0*3+2] = sphere_rad 
            
            nfixedtoequator = 1+nfixequator
            for i in range(0,nfixedtoequator):    
                self.thomsonPoints.freeflagspos[i*3+2] = 0
                self.thomsonPoints.pos[i*3+2] = self.thomsonPoints.pos[0*3+2] 
            
            printl("fullerene thomson point 0",self.thomsonPoints.pos[0],self.thomsonPoints.pos[1],
                   self.thomsonPoints.pos[2] )    
        else:
            #for i in range(0,npoints):
            self.thomsonPoints.pos = numpy.copy(inputpoints)
            
        nfixedtoequator = 1+nfixequator    
        for i in range(0,nfixedtoequator):    
                self.thomsonPoints.freeflagspos[i*3+2] = 0    
        
        if(fixpole):
            self.thomsonPoints.freeflags[0] = 0
            self.thomsonPoints.freeflagspos[0*3] = 0
            self.thomsonPoints.freeflagspos[0*3+1] = 0    
            self.thomsonPoints.freeflagspos[0*3+2] = 0  
   
        
            
        self.thomsonPoints.initial_pos = numpy.copy(self.thomsonPoints.pos)     