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
import os,sys,math,copy,random,time,threading,Queue,ctypes
import numpy

from nanocap.core.globals import *
from nanocap.core.util import *
from nanocap.clib import clib_interface
clib = clib_interface.clib
from nanocap.ext.edip import interface as edipinterface

clib.do_force_no_rdf.restype = None
clib.scale_rad.restype = None

ecount = 0 
fcount = 0
efcount = 0

class ForceField(object):
    '''
    The parent class which holds generic functions
    
    The most important is get_energy which returns
    the energy and force for the current 
    forcefield
        
    '''
    def __init__(self,ID,args=None):
        self.ID = ID
        self.args = args
        self.analytical_force = True
        self.options = ""
        self.energy_units = ""
    def set_args(self,args):
        self.args = args
        
    
    def get_energy(self,pointSet):
        #reimplement
        #return scalar energy, vector force
        pass
    
    def set_cutoff(self,cutoff):
        pass
    
    def __str__(self):
        return "Force Field: "+str(self.ID)+"args: "+" ".join(map(str,self.args))
    
    
    def setup(self,pointSet):
        pass
    
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


class RSSBondForceField(ForceField):
    '''
    I simply return the residual sum of squares error in
    bondlengths compared to required C-C bond length
    '''
    def __init__(self):
        ForceField.__init__(self,"RSSBond",[1.421])      
        self.analytical_force = False
    
    def get_energy(self,pointSet):
       
        BondLengths = numpy.zeros(pointSet.npoints*3,NPF)
        
        clib.get_bond_lengths_three(ctypes.c_int(pointSet.npoints),
                                     pointSet.pos.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                                     BondLengths.ctypes.data_as(ctypes.POINTER(ctypes.c_double)))
        
        res = numpy.sum(numpy.power(BondLengths - self.args[0],2))
             
        pointSet.force = 0.0#*pointSet.freeflagspos 
        pointSet.energy = res
        
        return res,0.0 

class EDIPForceField(ForceField):
    '''
    The Environmental Dependent Interatomic Potential
    Binary .so should be in /ext/edip 
    '''
    def __init__(self):
        ForceField.__init__(self,"EDIP",[50000,50000,50000])      
        self.energy_units = "eV"
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
    
    def setup(self,pointSet):
        bounds = pointSet.getBounds()
        self.args[0] = (bounds[3]-bounds[0])*2000.0
        self.args[1] = (bounds[4]-bounds[1])*2000.0
        self.args[2] = (bounds[5]-bounds[2])*2000.0
        printl("end setup_force_field")
    
class NullForceField(ForceField):
    '''
    A Null force field.
    '''
    def __init__(self):
        ForceField.__init__(self,"NULL")      
    def get_energy(self,pointSet):
        return 0,numpy.zeros_like(pointSet.pos)
        
            
class ThomsonForceField(ForceField):
    '''
    The dual lattice forcefield.
    
        The FF is init with 3 args;
        1) the exponent in r^-a,
        2) the neighbour cutoff 
        3) the cutoff along Z which is only used for capped nanotubes. 

    '''
    def __init__(self):
        ForceField.__init__(self,"Thomson",[1.0,99999999.0,99999999.0])      
    
    def set_cutoff(self,cutoff):
        self.args[2] = cutoff
    
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
        
        #printd("force field energy call",sum(energy),magnitude(force),numpy.sum(force[2::3]),self.args)
             
        return sum(energy),force    



FFS = {}
FFS['Thomson'] = ThomsonForceField()        
FFS['EDIP'] = EDIPForceField()     
FFS['Scaled Topology'] = RSSBondForceField()    
FFS['Unit Radius Topology'] = NullForceField()   

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