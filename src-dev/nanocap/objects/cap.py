'''
Created on Aug 24, 2011

@author: Marc
'''
from nanocap.core.globals import *
import os,sys,math,copy,random,time
import numpy
import nanocap.objects.points as points
from nanocap.core.util import *

from nanocap.clib import clib_interface
clib = clib_interface.clib

class cap(object):
    def __init__(self):
        self.thomsonPoints = points.Points("Cap Dual Lattice Points")
        self.thomsonPoints.initArrays(0)
        self.thomsonPoints.freeflags = numpy.ones(0,NPI)
        self.thomsonPoints.freeflagspos = numpy.ones(0,NPF)
        
        self.thomsonPoints.dampflags = numpy.zeros(0,NPI)
        self.thomsonPoints.dampflagspos = numpy.zeros(0,NPF)
        
        self.thomsonPoints.realflags = numpy.ones(0,NPI)
        self.thomsonPoints.realflags = numpy.ones(0,NPF)

    def setup(self,npoints,free = True, real=True,seed=None,):    
        self.thomsonPoints = points.Points("Cap Dual Lattice Points")
        
        self.thomsonPoints.initArrays(npoints)
        
        if(free==True):
            self.thomsonPoints.freeflags = numpy.ones(npoints,NPI)
            self.thomsonPoints.freeflagspos = numpy.ones(npoints*3,NPF)
        else:
            self.thomsonPoints.freeflags = numpy.zeros(npoints,NPI)
            self.thomsonPoints.freeflagspos = numpy.zeros(npoints*3,NPF)
            
        if(real==True):    
            self.thomsonPoints.realflags = numpy.ones(npoints,NPI)
            self.thomsonPoints.realflagspos = numpy.ones(npoints*3,NPF)
        else:
            self.thomsonPoints.realflags = numpy.zeros(npoints,NPI)
            self.thomsonPoints.realflags = numpy.zeros(npoints*3,NPF)
            
        self.thomsonPoints.dampflags = numpy.zeros(npoints,NPI)
        self.thomsonPoints.dampflagspos = numpy.zeros(npoints*3,NPF)
 
        if(seed==None):
            seed = random.randint(1,100000)      
        random.seed(seed)
        sphere_rad = 1.0
        clib.setup_random_points_on_sphere(ctypes.c_int(npoints),
                                        ctypes.c_int(seed),
                                        ctypes.c_int(1),
                                        ctypes.c_double(sphere_rad),
                                        self.thomsonPoints.pos.ctypes.data_as(ctypes.POINTER(ctypes.c_double)))
    
        #set up free atoms on the sphere cap (moved during minimisation)
        # z = -1 to 0 with nanotube from 0 to l 

        self.thomsonPoints.pos0 = numpy.copy(self.thomsonPoints.pos)   
        printl("cap thomson density",self.thomsonPoints.npoints,self.thomsonPoints.npoints/(2*math.pi))
          