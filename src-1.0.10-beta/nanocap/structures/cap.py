'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Aug 24 2011
Copyright Marc Robinson 2013
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

Cap base class. Contains instances of Points
Routines for setting up carbon atoms, dual lattice 

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
'''

from nanocap.core.globals import *
import os,sys,math,copy,random,time
import numpy
import nanocap.core.points as points
from nanocap.core.util import *

from nanocap.clib import clib_interface
from nanocap.structures.structure import Structure
clib = clib_interface.clib

class Cap(Structure):
    def __init__(self,secondary=False):
        if(secondary):
            Structure.__init__(self,STRUCTURE_TYPES[CAP_R])
            #self.type = StructureType(CAP_R,"CAP_R","Cap Secondary")
        else:
            Structure.__init__(self,STRUCTURE_TYPES[CAP])
            #self.type = StructureType(CAP,"CAP","Cap Primary")
    
    def __repr__(self):
        out = super(Cap, self).__repr__()       
        return out
    
    def set_carbon_lattice(self,npoints,pos):
        self.carbon_lattice = points.Points("Cap Carbon Lattice")
        self.carbon_lattice.initArrays(npoints)
        self.carbon_lattice.pos = numpy.copy(pos)
        
    
    def setup(self,npoints,free = True, real=True,seed=None,):    
        self.dual_lattice = points.Points("Cap Dual Lattice Points")
        
        self.dual_lattice.initArrays(npoints)
        
        if(free==True):
            self.dual_lattice.freeflags = numpy.ones(npoints,NPI)
            self.dual_lattice.freeflagspos = numpy.ones(npoints*3,NPF)
        else:
            self.dual_lattice.freeflags = numpy.zeros(npoints,NPI)
            self.dual_lattice.freeflagspos = numpy.zeros(npoints*3,NPF)
            
        if(real==True):    
            self.dual_lattice.realflags = numpy.ones(npoints,NPI)
            self.dual_lattice.realflagspos = numpy.ones(npoints*3,NPF)
        else:
            self.dual_lattice.realflags = numpy.zeros(npoints,NPI)
            self.dual_lattice.realflags = numpy.zeros(npoints*3,NPF)
            
        self.dual_lattice.dampflags = numpy.zeros(npoints,NPI)
        self.dual_lattice.dampflagspos = numpy.zeros(npoints*3,NPF)
 
        if(seed==None):
            seed = random.randint(1,100000) 
        self.seed = seed     
        random.seed(seed)
        sphere_rad = 1.0
        clib.setup_random_points_on_sphere(ctypes.c_int(npoints),
                                        ctypes.c_int(seed),
                                        ctypes.c_int(1),
                                        ctypes.c_double(sphere_rad),
                                        self.dual_lattice.pos.ctypes.data_as(ctypes.POINTER(ctypes.c_double)))
    
        #set up free atoms on the sphere cap (moved during minimisation)
        # z = -1 to 0 with nanotube from 0 to l 

        self.dual_lattice.pos0 = numpy.copy(self.dual_lattice.pos)   
        printl("cap thomson density",self.dual_lattice.npoints,self.dual_lattice.npoints/(2*math.pi))
        
        N_cap_carbon = NAtoms_from_NDual(npoints,surface="cap")
        self.set_carbon_lattice(N_cap_carbon,None)
          