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
 
from nanocap.core.util import *

from nanocap.clib import clib_interface
clib = clib_interface.clib

class fullerene(object):
    def __init__(self):
        self.thomsonPoints = points.Points("Fullerene Dual Lattice Points")
        self.thomsonPoints.initArrays(0)
        self.thomsonPoints.freeflags = numpy.ones(0,NPI)
        self.thomsonPoints.freeflagspos = numpy.ones(0,NPF)
        
        self.thomsonPoints.dampflags = numpy.zeros(0,NPI)
        self.thomsonPoints.dampflagspos = numpy.zeros(0,NPF)
        self.carbonAtoms = None

     
    def calcInfo(self):
        
        self.radius,self.radius_std = self.calcAverageRadius(self.carbonAtoms.npoints,self.carbonAtoms.pos)
       
        
        printl("fullerene average radius",self.radius,"+-",self.radius_std)
        
        try:
            self.constrained_radius,self.constrained_radius_std = self.calcAverageRadius(self.carbonAtoms.npoints,self.carbonAtoms.constrained_pos)
            printl("fullerene constrained average radius",self.constrained_radius,"+-",self.constrained_radius_std)
        except:pass
        try:
            self.unconstrained_radius,self.unconstrained_radius_std = self.calcAverageRadius(self.carbonAtoms.npoints,self.carbonAtoms.unconstrained_pos)
            printl("fullerene unconstrained average radius",self.unconstrained_radius,"+-",self.unconstrained_radius_std)
        except:pass
        
            
        
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
        return numpy.average(radii),numpy.std(radii)
     
            
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