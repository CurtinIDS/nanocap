'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Apr 23, 2014
Copyright Marc Robinson  2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

cappednanotube class


-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
'''


from nanocap.core.globals import *
import os,sys,math,copy,random,time,ctypes,fractions
import numpy
import nanocap.core.points as points
from nanocap.structures.structure import Structure
from nanocap.core import triangulation,constructdual,calculateschlegel,ringcalculator
from nanocap.core import ringcalculator 
from nanocap.structures import nanotube 
from nanocap.structures import cap 
from nanocap.core.util import *

from nanocap.clib import clib_interface
clib = clib_interface.clib

class CappedNanotube(Structure):
    def __init__(self):
        Structure.__init__(self,STRUCTURE_TYPES[CAPPEDNANOTUBE])
        #self.type = StructureType(CAPPEDNANOTUBE,"CAPPEDNANOTUBE","Capped Nanotube")
        self.has_child_structures = True
        
        self.nanotube,self.cap,self.reflected_cap = nanotube.Nanotube(),cap.Cap(),cap.Cap(secondary=True)
        
        self.nanotube.parent_structure = self
        self.cap.parent_structure = self
        self.reflected_cap.parent_structure = self
        
        self.cap_carbon_lattice_indexes = []
        self.nanotube_carbon_lattice_indexes = []
        self.reflected_cap_carbon_lattice_indexes = []

    def __repr__(self):
        self.calculate_rings()
        #self.calculate_structural_info()
        
        out = super(CappedNanotube, self).__repr__()
        
        out += self.nanotube.__repr__()
        out += self.cap.__repr__()
        return out
    
    def get_GUI_description(self,carbon_lattice=True,dual_lattice=True,carbonEnergy=True):
        '''
        override this superclass method so we can display capped nanotube specific info
        '''
        if(self.get_dual_lattice_energy()==0):
            des = "C{} ({},{}) {}".format(self.carbon_lattice.npoints,self.nanotube.n,
                                          self.nanotube.m,self.type.label)
        else:
            des = "C{} ({},{}) {}: Dual Lattice Energy {} ".format(self.carbon_lattice.npoints,
                                                                   self.nanotube.n,self.nanotube.m,self.type.label,
                                                                  self.get_dual_lattice_energy())
        return des   
    
    def get_structure_data(self):
        self.data = super(CappedNanotube, self).get_structure_data()
        try:self.data['dual_lattices']['n_cap'] = self.cap.dual_lattice.npoints
        except:pass
        try:self.data['dual_lattices']['n_tube'] = self.nanotube.dual_lattice.npoints
        except:pass
        try:self.data['dual_lattices']['n'] = self.nanotube.n
        except:pass
        try:self.data['dual_lattices']['m'] = self.nanotube.m
        except:pass
        
        try:self.data['dual_lattices']['force_cutoff'] = self.cutoff
        except:pass
        
        try:self.data['carbon_lattices']['uncapped_length'] = self.nanotube.length
        except:pass
        
        try:self.data['carbon_lattices']['length'] = self.get_length()
        except:pass

        try:self.data['carbon_lattices']['ff_id'] = self.carbon_lattice_minimiser.FFID
        except:pass
        try:self.data['carbon_lattices']['n_cap'] = self.cap.carbon_lattice.npoints
        except:pass
        try:self.data['carbon_lattices']['n_tube'] = self.nanotube.carbon_lattice.npoints
        except:pass
        try:self.data['carbon_lattices']['n'] = self.nanotube.n
        except:pass
        try:self.data['carbon_lattices']['m'] = self.nanotube.m
        except:pass
        

        
        return self.data
    
    def get_child_structures(self):
        '''
        if capped nanotube, return the nanotube and cap
        
        '''
        return [self.nanotube,self.cap,self.reflected_cap]
    
        
    def setup_nanotube(self,n,m,l=None,dual_lattice_radius=1.0):
        #self.nanotube = nanotube.Nanotube()
        if(l==None):
            N_cap_dual = self.get_cap_dual_lattice_estimate(n, m)
            l = self.get_Z_cutoff(N_cap_dual)
        
        #self.nanotube.construct_dual_lattice(n,m,l)
        self.nanotube.construct(n,m,length=l,units=1,periodic=False)
        self.nanotube.scale_dual_lattice(dual_lattice_radius)
        
        
    def reset_cap(self):
        #self.cap = cap.Cap()
        pass
    
    def reset_secondary_cap(self):
        try:self.cap
        except:
            printl("cap not constructed yet")
            return
        if(self.cap==None):
            printl("cap not constructed yet")
            return
        #self.reflected_cap = cap.Cap()
        printh("resetting cap with ",self.cap.dual_lattice.npoints,"dual lattice points")
        self.reflected_cap.setup(self.cap.dual_lattice.npoints,
                                real=False,
                                free=False)
        self.reflected_cap.dual_lattice.pos = numpy.copy(self.cap.dual_lattice.pos)
        self.reflected_cap.dual_lattice.pos[2::3] -= self.nanotube.midpoint_z
        self.reflected_cap.dual_lattice.pos[1::3]*=-1
        self.reflected_cap.dual_lattice.pos[2::3]*=-1
        self.reflected_cap.dual_lattice.pos[2::3] += self.nanotube.midpoint_z
    

        
        
        
    def update_caps(self):
        try:self.cap
        except:
            printl("cap not constructed yet")
            return
        if(self.cap==None):
            printl("cap not constructed yet")
            return
        
        printl("update caps",self.reflected_cap.dual_lattice.npoints,
               self.dual_lattice.npoints,
               self.cap.dual_lattice.npoints,self.nanotube.dual_lattice.npoints)
        
        self.cap.dual_lattice.pos = numpy.copy(self.dual_lattice.pos[:self.cap.dual_lattice.npoints*3])
        self.reflected_cap.dual_lattice.pos = numpy.copy(self.dual_lattice.pos[:self.cap.dual_lattice.npoints*3])
        self.reflected_cap.dual_lattice.pos[2::3] -= self.nanotube.midpoint_z
        self.reflected_cap.dual_lattice.pos[1::3]*=-1
        self.reflected_cap.dual_lattice.pos[2::3]*=-1
        self.reflected_cap.dual_lattice.pos[2::3] += self.nanotube.midpoint_z
           
        offset = self.cap.dual_lattice.npoints+self.nanotube.dual_lattice.npoints
        
        self.dual_lattice.pos[offset*3:] = numpy.copy(self.reflected_cap.dual_lattice.pos)

    def setup_cap(self,Nd,seed=None):
        #self.cap = cap.Cap()
        self.cap.setup(Nd,seed=seed)
    
    def reset_nanotube(self): 
        #self.nanotube = nanotube.Nanotube()
        #self.cap = None
        #self.reflectedCap = None
        pass
    
    def construct_carbon_lattice(self):
        super(CappedNanotube, self).construct_carbon_lattice()
        
        self.calculate_child_carbon_lattices()
        #now we need to determine the cap carbon atoms...
       
    
#     def set_carbon_lattice(self,npoints,pos):
#         super(CappedNanotube, self).set_carbon_lattice(npoints,pos)
#         self.calculate_child_carbon_lattices()
            
    def update_child_structures(self):
        
        printl("self.cap_carbon_lattice_indexes",self.cap_carbon_lattice_indexes)
        
#         for i in self.cap_carbon_lattice_indexes:
#             print self.carbon_lattice.pos[i*3],self.carbon_lattice.pos[i*3+1],self.carbon_lattice.pos[i*3+2]
        
        cappos = numpy.dstack((self.carbon_lattice.pos[self.cap_carbon_lattice_indexes*3],
                               self.carbon_lattice.pos[self.cap_carbon_lattice_indexes*3+1],
                               self.carbon_lattice.pos[self.cap_carbon_lattice_indexes*3+2])).flatten()
        
        
        self.cap.set_carbon_lattice(self.cap.carbon_lattice.npoints,
                                    cappos)
        
        cappos = numpy.dstack((self.carbon_lattice.pos[self.reflected_cap_carbon_lattice_indexes*3],
                               self.carbon_lattice.pos[self.reflected_cap_carbon_lattice_indexes*3+1],
                               self.carbon_lattice.pos[self.reflected_cap_carbon_lattice_indexes*3+2])).flatten()
        
        
        self.reflected_cap.set_carbon_lattice(self.reflected_cap.carbon_lattice.npoints,
                                              cappos)
        
        npos = numpy.dstack((self.carbon_lattice.pos[self.nanotube_carbon_lattice_indexes*3],
                               self.carbon_lattice.pos[self.nanotube_carbon_lattice_indexes*3+1],
                               self.carbon_lattice.pos[self.nanotube_carbon_lattice_indexes*3+2])).flatten()
        
        #npos = self.nanotube.carbon_lattice.pos*self.nanotube.scale
        self.nanotube.set_carbon_lattice(self.nanotube.carbon_lattice.npoints,
                                              npos)
        
    def calculate_child_carbon_lattices(self):            
        #pos = self.carbon_lattice.pos*(1.0/self.nanotube.scale)
        printl("self.cap.carbon_lattice.npoints",self.cap.carbon_lattice.npoints)
        printl("self.nanotube.carbon_lattice.npoints",self.nanotube.carbon_lattice.npoints)
        printl("self.carbon_lattice.npoints",self.carbon_lattice.npoints)
        minr = numpy.zeros(self.carbon_lattice.npoints,NPF)
        
        
        
        zorder = numpy.argsort(self.carbon_lattice.pos[2::3])
        
        self.cap_carbon_lattice_indexes = zorder[:self.cap.carbon_lattice.npoints]
        self.nanotube_carbon_lattice_indexes = zorder[self.cap.carbon_lattice.npoints:self.cap.carbon_lattice.npoints+self.nanotube.carbon_lattice.npoints]
        self.reflected_cap_carbon_lattice_indexes = zorder[self.nanotube.carbon_lattice.npoints+self.cap.carbon_lattice.npoints:]

        
        self.update_child_structures()
            
                
    
    def construct_dual_lattice(self,N_cap_carbon=None,N_cap_dual=None,seed=None):
        
        if(N_cap_carbon==None and N_cap_dual==None):
            printe("Must pass either NCarbon or NDual to initialise cap of nanotube dual lattice")
            return
        if(N_cap_carbon!=None and N_cap_dual!=None):
            printe("Must pass either NCarbon or NDual to initialise cap of nanotube dual lattice")      
            return
        
        if(N_cap_carbon!=None):
            N_cap_dual = NDual_from_NAtoms(N_cap_carbon,surface="cap")
        if(N_cap_dual!=None):
            N_cap_carbon = NAtoms_from_NDual(N_cap_dual,surface="cap")
        
        printl("initialising N_dual {} N_carbon {} cap".format(N_cap_dual,N_cap_carbon))
        
        self.reset_cap()
        self.setup_cap(N_cap_dual, seed)
        self.reset_secondary_cap()
        
        self.dual_lattice = points.joinPointSets((self.cap.dual_lattice,
                                                  self.nanotube.dual_lattice,
                                                  self.reflected_cap.dual_lattice))   
                                        
        self.dual_lattice.PointSetLabel = "Capped Nanotube Dual Lattice Points"        
    
    def get_cap_dual_lattice_estimate(self,n,m):
        printl("getting cap estimates")
        
        self.nanotube.setup_properties(n,m)

        #based on C60
        dualRho  = 0.22
        estimate = int(math.ceil(dualRho*(4.0*math.pi*self.nanotube.radius*self.nanotube.radius)/2.0))
        return estimate
    
    def set_Z_cutoff(self,N_cap_dual=None,cutoff=None):
        
        if(N_cap_dual!=None):
            self.cutoff = self.get_Z_cutoff(N_cap_dual)
        else:
            self.cutoff = cutoff 
        
        if(self.cutoff>self.nanotube.scaled_length):
            printe("nanotube cutoff longer than nanotube length, resetting")
            self.setup_nanotube(self.nanotube.n, self.nanotube.m, self.cutoff/self.nanotube.scale)
            self.construct_dual_lattice(N_cap_dual=self.cap.dual_lattice.npoints,seed=self.cap.seed)
            
        printl("set Z cutoff",self.cutoff,self.nanotube.scaled_length)   
    
    def get_length(self):
        x0,y0,z0,x1,y1,z1 = self.carbon_lattice.getBounds()
        return float(z1-z0)
        
            
    def get_Z_cutoff(self,N_cap_dual):
        '''
        The force cutoff along the nanotube axis. Points past this cutoff do not
        contribute to dual lattice minimisation.
        '''
        a =  [0.948452364196,1.02360096456,0.251753131336] 
        cutoff = a[0]*math.exp(a[1]/((N_cap_dual/(2*math.pi))**a[2]))
        return cutoff

        
        