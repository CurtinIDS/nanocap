'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: July 24 2012
Copyright Marc Robinson 2013
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

Fullerene base class.

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
'''
#from nanocap.core import globals
from nanocap.core.globals import *
import os,sys,math,copy,random,time,ctypes
import numpy
import nanocap.core.points as points
from nanocap.structures.structure import Structure
from nanocap.core import triangulation,constructdual,calculateschlegel,ringcalculator
 
from nanocap.core.util import *

from nanocap.clib import clib_interface
clib = clib_interface.clib

class Fullerene(Structure):
    def __init__(self):
        
        Structure.__init__(self,STRUCTURE_TYPES[FULLERENE])
        self.fix_pole = False
        self.nfixed_equator = 0
        #self.type = StructureType(FULLERENE,"FULLERENE","Fullerene")
        
    def __repr__(self):
        out = super(Fullerene, self).__repr__()
        out += self.col1h.format('structural_info')
        self.calculate_rings()
        self.calculate_structural_info()
        
        out += self.col2.format("average_radius",str(self.radius)+" +- "+str(self.radius_std))
        out += self.col2.format("min_radius",self.radius_min)
        out += self.col2.format("max_radius",self.radius_max)
        try:out += col2.format("constrained_average_radius",str(self.constrained_radius)+" +- "+str(self.constrained_radius_std))
        except:pass
        
        out += self.col2.format("surface_area",self.surface_area)
        out += self.col2.format("volume",self.volume)
        out += self.col2.format("sphericity",self.sphericity)
        
        try:
            out += self.col1h.format("ring_stats")
            for i in range(3,len(self.ring_info['ringCount'])):
                if(i==5):
                    out += self.col2.format("number_of_"+str(i)+"-agons ",str(self.ring_info['ringCount'][i])+" IP "+str(self.ring_info['isolatedPentagons']))
                else:
                    out += self.col2.format("number_of_"+str(i)+"-agons ",self.ring_info['ringCount'][i])                    
               
            out += self.col2.format("%_6-agons",self.ring_info['percHex'])    
        except:
            pass
        
        out += self.sepformat.format("")
        return out 
    
    def calculate_structural_info(self):
        self.radius,self.radius_std,self.radius_min,self.radius_max = self.calc_average_radius(self.carbon_lattice.npoints,self.carbon_lattice.pos)
        printl("fullerene average radius",self.radius,"+-",self.radius_std)
        try:
            self.constrained_radius,self.constrained_radius_std,min,max = self.calc_average_radius(self.carbon_lattice.npoints,self.carbon_lattice.constrained_pos)
            printl("fullerene constrained average radius",self.constrained_radius,"+-",self.constrained_radius_std)
        except:pass

        self.calculate_surface_area_volume()
        
        if(self.surface_area>0 and self.volume>0):
            self.sphericity = (math.pow(math.pi,1.0/3.0) * math.pow((6.0*self.volume),2.0/3.0))/self.surface_area
        else:
            self.sphericity =  0
        printl("fullerene sphericity",self.sphericity)
        

    def construct_dual_lattice(self,N_carbon=None,N_dual=None,input_points=None,radius=1.0,seed=None):
        '''
        initiliase the fullerene dual lattice using either carbon 
        or dual lattice points 
        
        input: NCarbon or NDual (int)
                if carbon atoms are passed, then the number of dual lattice points are determined. 
               inputpoints (3N array of positions)
                if inputpoints are passed, use these points do not create new points
        '''
        
        if(N_carbon==None and N_dual==None):
            printe("Must pass either NCarbon or NDual to initialise fullerence dual lattice")
            return
        if(N_carbon!=None and N_dual!=None):
            printe("Must pass either NCarbon or NDual to initialise fullerence dual lattice")      
            return
        
        if(N_carbon!=None):
            N_dual = NDual_from_NAtoms(N_carbon,surface="sphere")
        if(N_dual!=None):
            N_carbon = NAtoms_from_NDual(N_dual,surface="sphere")
        
        printl("initialising N_dual {} N_carbon {} fullerene".format(N_dual,N_carbon))
        
        self.dual_lattice = points.Points("Fullerene Dual Lattice Points")
         
        self.dual_lattice.initArrays(N_dual)
        self.dual_latticeRadius = radius
                 
        if(input_points==None):
            if(seed==None):
                seed = int(time.time()*random.random())
                
            self.seed = seed    
            clib.setup_random_points_on_sphere(ctypes.c_int(N_dual),
                                                ctypes.c_int(seed),
                                                ctypes.c_int(0),
                                                ctypes.c_double(radius),
                                                self.dual_lattice.pos.ctypes.data_as(ctypes.POINTER(ctypes.c_double)))
 
        else:
            self.dual_lattice.pos = numpy.copy(inputpoints)
    
        #printl(self.dual_lattice.pos) 
        self.dual_lattice.initial_pos = numpy.copy(self.dual_lattice.pos)
        self.fix_dual_lattice_point_to_pole()
        self.fix_dual_lattice_points_to_equator()
        
    def fix_dual_lattice_point_to_pole(self):
        if(self.fix_pole):
            printl("fixing dual lattice point to pole")
            self.dual_lattice.freeflags[0] = 0
            self.dual_lattice.freeflagspos[0*3] = 0
            self.dual_lattice.freeflagspos[0*3+1] = 0    
            self.dual_lattice.freeflagspos[0*3+2] = 0  
            self.dual_lattice.pos[0*3] = 0.0
            self.dual_lattice.pos[0*3+1] = 0.0   
            self.dual_lattice.pos[0*3+2] = self.dual_latticeRadius 
        else:
            self.dual_lattice.freeflags[0] = 1
            self.dual_lattice.freeflagspos[0*3] = 1
            self.dual_lattice.freeflagspos[0*3+1] = 1    
            self.dual_lattice.freeflagspos[0*3+2] = 1  
    
    def fix_dual_lattice_points_to_equator(self):
        if(self.fix_pole):
            for i in range(1,self.nfixed_equator):  
                self.dual_lattice.freeflagspos[i*3+0] = 0        
                yz = normalise(numpy.array([self.dual_lattice.pos[i*3+1],self.dual_lattice.pos[i*3+2]]))
                self.dual_lattice.pos[i*3+0] = 0
                self.dual_lattice.pos[i*3+1] = yz[0]
                self.dual_lattice.pos[i*3+2] = yz[1]
        else:
            for i in range(0,self.nfixed_equator):  
                self.dual_lattice.freeflagspos[i*3+0] = 0      
                yz = normalise(numpy.array([self.dual_lattice.pos[i*3+1],self.dual_lattice.pos[i*3+2]]))
                self.dual_lattice.pos[i*3+0] = 0
                self.dual_lattice.pos[i*3+1] = yz[0]
                self.dual_lattice.pos[i*3+2] = yz[1]
                
        #printl(self.dual_lattice.pos,self.nfixed_equator)     
        
    def set_fix_pole(self,flag):
        self.fix_pole = flag
        self.fix_dual_lattice_point_to_pole()
        
    def set_nfixed_to_equator(self,N):
        self.nfixed_equator = N 
        self.fix_dual_lattice_points_to_equator()
        

    def calc_average_radius(self,npoints,pos):
        if(npoints==0):return 0,0,0,0
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
     
            
    def construct_carbon_lattice_manual(self,npoints,point_rad,point_col,sphere_rad,
                                        inputpoints=None,seed=None,nfixequator=0,fixpole=False):
            
        self.carbon_lattice = points.Points("Fullerene Carbon Atoms")
        
        self.carbon_lattice.initArrays(npoints)
        self.carbon_lattice.freeflags = numpy.ones(npoints,NPI)
        self.carbon_lattice.freeflagspos = numpy.ones(npoints*3,NPF)
        
        self.carbon_lattice.dampflags = numpy.zeros(npoints,NPI)
        self.carbon_lattice.dampflagspos = numpy.zeros(npoints*3,NPF)
                
        if(inputpoints==None):
            clib.setup_random_points_on_sphere(ctypes.c_int(npoints),
                                        ctypes.c_int(seed),
                                        ctypes.c_int(0),
                                        ctypes.c_double(sphere_rad),
                                        self.carbon_lattice.pos.ctypes.data_as(ctypes.POINTER(ctypes.c_double)))
            
            
            self.carbon_lattice.pos[0*3] = sphere_rad
            self.carbon_lattice.pos[0*3+1] = 0.0   
            self.carbon_lattice.pos[0*3+2] = 0.0  
            
            nfixedtoequator = 1+nfixequator
            for i in range(0,nfixedtoequator):    
                self.carbon_lattice.freeflagspos[i*3+2] = 0
                self.carbon_lattice.pos[i*3+2] = self.carbon_lattice.pos[0*3+2] 
        else:
            #for i in range(0,npoints):
            self.carbon_lattice.pos = numpy.copy(inputpoints)
            
        nfixedtoequator = 1+nfixequator    
        for i in range(0,nfixedtoequator):    
                self.carbon_lattice.freeflagspos[i*3+2] = 0    
        
        if(fixpole):
            self.carbon_lattice.freeflags[0] = 0
            self.carbon_lattice.freeflagspos[0*3] = 0
            self.carbon_lattice.freeflagspos[0*3+1] = 0    
            self.carbon_lattice.freeflagspos[0*3+2] = 0  
   
        self.carbon_lattice.initial_pos = numpy.copy(self.carbon_lattice.pos)   
