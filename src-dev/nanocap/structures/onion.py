'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Feb 10 2014
Copyright Marc Robinson 2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

Onion base class.

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
'''
from nanocap.core import globals
from nanocap.core.globals import *
import os,sys,math,copy,random,time,ctypes
import numpy
import nanocap.core.points as points
from nanocap.structures import fullerene
from nanocap.core import triangulation
from nanocap.core import ringcalculator 
from nanocap.core import minimisation 
from nanocap.core.util import *
from nanocap.clib import clib_interface
clib = clib_interface.clib


class Onion(object):
    def __init__(self, NShells):
        self.NShells = NShells
        
        self.fullerenes = []
        
    def set_shell(self,i,natoms,dual_pos=None,carbon_pos=None,
                  drad=1.0,dcol=(1,0,0),crad=1.0,ccol=(0,0,0)):
        
        new_fullerene = fullerene.Fullerene()
        NTp = (natoms+4) / 2
        
        if(carbon_pos==None and dual_pos==None):
            print "no atoms or dual lattice points passed to onion"
            return
        
        if(dual_pos!=None):
            nfix = 0
            fixPole = False
            new_fullerene.setupThomsonPoints(NTp,drad,dcol,1.0,inputpoints=dual_pos,
                                              seed=seed,nfixequator=nfix,fixpole = fixPole)    
        
        
        if(carbon_pos!=None):
            new_fullerene.setupCarbonAtoms(natoms,crad,ccol,1.0,inputpoints=carbon_pos,
                                           nfixequator=0,fixpole=False)
            
            
        #else:
            #could retriangulate
        new_fullerene.calculateCarbonRings()
        new_fullerene.calcInfo()
        
           
        
        try:
            self.fullerenes[i] = new_fullerene
            
        except:
            self.fullerenes.append(new_fullerene)
        
        
        
        print self.fullerenes
        
    def __repr__(self):
        twidth = 80
        
        out = ""
        sepformat = "{0:=^"+str(twidth)+"} \n"
        sepformat2 = "{0:+^"+str(twidth)+"} \n"
        
        col1 = "{0:<"+str(twidth)+"} \n"
        col1h = "{0:-^"+str(twidth)+"} \n"
        col2 = "{0:<"+str(int(twidth/2))+"} {1:<"+str(int(twidth/2))+"}\n"
        col3 = "{0:<"+str(int(twidth/3))+"} {1:<"+str(int(twidth/3))+"} {2:<"+str(int(twidth/3))+"}\n"
        col4 = "{0:<"+str(int(twidth/4))+"} {1:<"+str(int(twidth/4))+"} {2:<"+str(int(twidth/4))+"} {3:<"+str(int(twidth/4))+"}\n" 
        
        out += sepformat.format("C"+str(self.carbonAtoms.npoints)+"_Onion")
        out += col2.format("N_carbon_atoms",self.carbonAtoms.npoints)
        try:
            out += col2.format("carbon_lattice_energy",str(self.carbonAtoms.FinalEnergy)+" eV")
            out += col2.format("carbon_lattice_energy_per_atom",str(self.carbonAtoms.FinalEnergy/self.carbonAtoms.npoints)+" eV")
        except:pass
        
        self.deconstruct()
        
        
        for f in self.fullerenes:
            f.calculateCarbonRings()
            f.calcInfo()
            
        
        out += col2.format("average_radius",str(self.fullerenes[-1].radius)+" +- "+str(self.fullerenes[-1].radius_std))
        out += col2.format("min_radius",self.fullerenes[-1].radius_min)
        out += col2.format("max_radius",self.fullerenes[-1].radius_max)
        try:out += col2.format("constrained_average_radius",str(self.fullerenes[-1].constrained_radius)+" +- "+str(self.fullerenes[-1].constrained_radius_std))
        except:pass
        
        out += col2.format("surface_area",self.fullerenes[-1].surfaceArea)
        out += col2.format("volume",self.fullerenes[-1].volume)
        out += col2.format("sphericity",self.fullerenes[-1].sphericity)
        
#        try:out += col2.format("unconstrained_average_radius",str(self.unconstrained_radius)+" +- "+str(self.unconstrained_radius_std))
#        except:pass
        try:
            out += col1h.format("ring_stats")
            for i in range(3,len(self.fullerenes[-1].ringCount)):
                sr,ip = 0,0
                ph = []
                for f in self.fullerenes:
                    sr+=f.ringCount[i]
                    ip+=f.isolatedPentagons
                    ph.append(f.percHex)
                    
                if(i==5):
                    out += col2.format("number_of_"+str(i)+"-agons ",str(sr)+" IP "+str(ip))
                else:
                    out += col2.format("number_of_"+str(i)+"-agons ",sr)                    
               
            out += col2.format("%_6-agons",numpy.average(ph))    
        except:
            pass
        
        out += sepformat.format("")
        
        out += sepformat2.format("SHELLS")
        for f in self.fullerenes:
            out += f.__repr__()
        out += sepformat2.format("")
        return out 

    
    
        
    def minimise(self,rot=True,ftol=1e-10,minsteps=100):
        
        minimiser  = minimisation.carbonLatticeMinimiser(FFID="EDIP")
        minimiser.minimise_onion(self,rot=rot,ftol=ftol,minsteps=minsteps)
        
        
    def minimise_fullerenes(self,ftol=1e-10,minsteps=100):    
        minimiser  = minimisation.carbonLatticeMinimiser(FFID="EDIP")
        self.sum_fullerene_energy=0
        for i,f in enumerate(self.fullerenes):
            minimiser.minimise(f.carbonAtoms)
            print "shell energy",i,f.carbonAtoms.FinalEnergy
            self.sum_fullerene_energy+=f.carbonAtoms.FinalEnergy
            
    
    def get_single_line_description(self):
        des="Onion"
            
        des+="_Nc_"+str(self.carbonAtoms.npoints)
        des+="_Shells"
        for f in self.fullerenes:
            des+="_C"+str(f.carbonAtoms.npoints)
        try:des+="_Energy_"+str(self.carbonAtoms.FinalEnergy)
        except:pass
        try:
            IPperc = float(self.isolatedPentagons)/float(self.ringCount[5])*100.0
            des+="_IP%_"+str(IPperc)
        except:pass
        
        return des
        
    #def write_info(self,filename):
        

        
    def rotate_x(self,shell,theta):
        
        self.deconstruct()
        f = self.fullerenes[shell]
        x,y,z = f.carbonAtoms.pos[0::3],f.carbonAtoms.pos[1::3],f.carbonAtoms.pos[2::3]
        #print "rotating shell ", shell,y[0],theta
        
        yp = y*math.cos(theta) - z*math.sin(theta)
        zp = y*math.sin(theta) + z*math.cos(theta)
        
        #for i in range(0,f.carbonAtoms.npoints):
        #    print theta,y[i],yp[i],z[i],zp[i]
        f.carbonAtoms.pos[1::3],f.carbonAtoms.pos[2::3] = yp,zp
        #print "rotate shell ", shell,yp[0],theta
        self.construct()
    
    def rotate_y(self,shell,theta):
        self.deconstruct()
        f = self.fullerenes[shell]
        x,y,z = f.carbonAtoms.pos[0::3],f.carbonAtoms.pos[1::3],f.carbonAtoms.pos[2::3]
        
        xp = x*math.cos(theta) + z*math.sin(theta)
        zp = -x*math.sin(theta) + z*math.cos(theta)
        
        f.carbonAtoms.pos[0::3],f.carbonAtoms.pos[2::3] = xp,zp
        self.construct()
        
    def rotate_z(self,shell,theta):
        self.deconstruct()
        f = self.fullerenes[shell]
        x,y,z = f.carbonAtoms.pos[0::3],f.carbonAtoms.pos[1::3],f.carbonAtoms.pos[2::3]
        
        xp = x*math.cos(theta) - y*math.sin(theta)
        yp = x*math.sin(theta) + y*math.cos(theta)
        
        
        f.carbonAtoms.pos[0::3],f.carbonAtoms.pos[1::3] = xp,yp
        self.construct()
    
    def deconstruct(self,drad=1.0,dcol=(1,0,0),crad=1.0,ccol=(0,0,0)):
        
        tnatoms = 0
        for i in range(0,self.NShells):
            new_fullerene = fullerene.Fullerene()

            natoms = self.fullerenes[i].carbonAtoms.npoints
            #print natoms, len(self.carbonAtoms.pos[tnatoms*3:(tnatoms+natoms)*3]),tnatoms*3,":",(tnatoms+natoms)*3
            new_fullerene.setupCarbonAtoms(natoms,crad,ccol,1.0,
                                           inputpoints=numpy.copy(self.carbonAtoms.pos[tnatoms*3:(tnatoms+natoms)*3]),
                                           nfixequator=0,fixpole=False)
            #new_fullerene.calculateCarbonRings()
            #new_fullerene.calcInfo()
            self.fullerenes[i] = new_fullerene
            tnatoms+=natoms
            
    def construct(self):
        self.carbonAtoms = points.Points("Onion Carbon Atoms")
        natoms = 0 
        natoms = numpy.sum([f.carbonAtoms.npoints for f in self.fullerenes])
        #print "natoms",natoms
        #for f in self.fullerenes:
            
        self.carbonAtoms.initArrays(natoms)
        
        self.carbonAtoms.pos = self.fullerenes[0].carbonAtoms.pos
        
        for i in range(1,self.NShells):
            self.carbonAtoms.pos = numpy.append(self.carbonAtoms.pos,self.fullerenes[i].carbonAtoms.pos)
            #print "shell separation ",i-1,i, self.fullerenes[i-1].radius - self.fullerenes[i].radius
            
            
        #print "self.carbonAtoms.pos",self.carbonAtoms.pos[0]
#         print "self.fullerenes[i].carbonAtoms.pos",self.fullerenes[0].carbonAtoms.pos[0]
#         self.carbonAtoms.pos[0]+=1
#         print "self.carbonAtoms.pos",self.carbonAtoms.pos[0]
#         print "self.fullerenes[i].carbonAtoms.pos",self.fullerenes[0].carbonAtoms.pos[0]

    def write(self,fname):
        write_xyz(fname,self.carbonAtoms)
        
    
    
        
        
        
        
    