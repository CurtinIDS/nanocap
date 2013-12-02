'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Sep 20 2013
Copyright Marc Robinson 2013
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

ForceField base class - abstract class for getting energy and forces for a configuration
Current FF:
EDIP - Environmental Dependent Interatomic Potential for Carbon. Implemented in Fortran in the ext/ dir
Thomson - The 1/r potential for constructing the dual lattices

Also holds some generic routines 
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
'''

from nanocap.core.globals import *
import nanocap.core.globals as globals
import os,sys,math,copy,random,time,threading,Queue,ctypes

import numpy

from nanocap.core.util import *
from nanocap.clib import clib_interface
clib = clib_interface.clib
from nanocap.ext.edip import interface as edipinterface

clib.do_force_no_rdf.restype = None
clib.scale_rad.restype = None

ecount = 0 
fcount = 0
efcount = 0

'''
parent class
'''

class ForceField(object):
    def __init__(self,ID,args=None):
        self.ID = ID
        self.args = args
    
    def set_args(self,args):
        self.args = args
        
    
    def get_energy(self,pointSet):
        #reimplement
        #return scalar energy, vector force
        pass
    
    def __str__(self):
        return "Force Field: "+str(self.ID)+"args: "+" ".join(map(str,self.args))
    
    def check_numerical_forces(self,pointSet,h):
            
        HVec = h*normalise(randvec(pointSet.pos))
        
        energy,force  = self.get_energy(pointSet)

        pointSet.pos+=HVec
        
        fenergy,fforce = self.get_energy(pointSet)
        
        pointSet.pos-=2*HVec

        benergy,bforce = self.get_energy(pointSet)
                
        numerical = -1*(fenergy-benergy)/(2.0*h)
        analytical = numpy.dot(force, normalise(HVec))
        error = numerical - analytical
        ratio = analytical/numerical
        printl("NUMERICAL FORCE ", numerical," ANALYTICAL FORCE ",analytical, " ERROR ",error," RATIO ",ratio)

class EDIPForceField(ForceField):
    def __init__(self):
        ForceField.__init__(self,"EDIP",[50000,50000,50000])      

    def get_energy(self,pointSet):
        box = numpy.array([self.args[0],
                                self.args[1],
                                self.args[2]],
                                NPF)
        
       #printl("box",box)
        energy=[0]
        energy[0],force = edipinterface.get_energy_force(pointSet.npoints,box,pointSet.pos)
             
        pointSet.force = force#*pointSet.freeflagspos 
        pointSet.energy = energy
        
        #printl(self.ID,"force field energy call",sum(energy),magnitude(force))
        return sum(energy),force  
    

class ThomsonForceField(ForceField):
    def __init__(self):
        ForceField.__init__(self,"Thomson",[1.0,99999999.0,99999999.0])      

    def get_energy(self,pointSet):
        pos = pointSet.pos
        freeflagspos = pointSet.freeflagspos
        force = numpy.zeros(len(pos),dtype=NPF)
        vel = numpy.zeros(len(pos),dtype=NPF)
        energy = numpy.zeros(len(pos)/3,dtype=NPF)

        clib.thomson_force_call(ctypes.c_int(pointSet.npoints),
                                 force.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                                 pos.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                                 energy.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                                 vel.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                                 freeflagspos.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                                 ctypes.c_double(self.args[0]),
                                 ctypes.c_double(self.args[1]),
                                 ctypes.c_double(self.args[2]))

             
        pointSet.force = force#*pointSet.freeflagspos 
        pointSet.energy = energy
        
        #printl("force field energy call",sum(energy),magnitude(force),numpy.sum(force[2::3]),self.args)
             
        return sum(energy),force    



FFS = {}
FFS['Thomson'] = ThomsonForceField()        
FFS['EDIP'] = EDIPForceField()     


def remove_radial_component_of_force(npoints,pos,force):
    clib.remove_radial_component__of_force(ctypes.c_int(npoints),
                             force.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                             pos.ctypes.data_as(ctypes.POINTER(ctypes.c_double)))
    
    

def force_on_cap_atoms_in_tube(ncap,pos,force,energy,k):
    clib.force_on_cap_atoms_in_tube(ctypes.c_int(ncap),
                         force.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                         pos.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                         energy.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                         ctypes.c_double(k))
    
    #printl("force_on_cap_atoms_in_tube")
    
def get_gauss_energy_and_force(npoints,pos,gpos,gwidth,gheight):
    force = numpy.zeros(len(pos),dtype=NPF)
    
    if(gwidth==0.0 or gheight==0.0):
        return 0,force
    
    #gaussenergy = 0
    #for gpos in self.gaussianArray:
    clib.do_gauss_force.restype = ctypes.c_double
    gaussenergy = clib.do_gauss_force(ctypes.c_int(npoints),
                        force.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                        pos.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                        gpos.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                        ctypes.c_double(gwidth),
                        ctypes.c_double(gheight))
    #gaussenergy+= tempenergy
    
    return gaussenergy,force        