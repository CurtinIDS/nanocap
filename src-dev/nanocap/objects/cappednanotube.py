'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Dec 18 2013
Copyright Marc Robinson 2013
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

Cap base class. Contains instances of Points
Routines for setting up carbon atoms, dual lattice 

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
'''

from nanocap.core.globals import *
import os,sys,math,copy,random,time
import numpy
import nanocap.objects.points as points
from nanocap.core.util import *
from nanocap.objects import nanotube 
from nanocap.objects import cap 
from nanocap.core import ringcalculator 
from nanocap.clib import clib_interface
clib = clib_interface.clib

class CappedNanotube(object):
    def __init__(self):
#        self.thomsonPoints = points.Points("Capped Nanotube Dual Lattice Points")
#        self.thomsonPoints.initArrays(0)
#        self.thomsonPoints.freeflags = numpy.ones(0,NPI)
#        self.thomsonPoints.freeflagspos = numpy.ones(0,NPF)
#        
#        self.thomsonPoints.dampflags = numpy.zeros(0,NPI)
#        self.thomsonPoints.dampflagspos = numpy.zeros(0,NPF)
#        
#        self.thomsonPoints.realflags = numpy.ones(0,NPI)
#        self.thomsonPoints.realflags = numpy.ones(0,NPF)
        
        self.thomsonPoints = None
        self.carbonAtoms = None
        self.nanotube = nanotube.Nanotube()
        self.cap = None
        self.reflectedCap = None
        
    def __repr__(self):
        twidth = 80
        
        out = ""
        sepformat = "{0:=^"+str(twidth)+"} \n"
        
        col1 = "{0:<"+str(twidth)+"} \n"
        col1h = "{0:-^"+str(twidth)+"} \n"
        col2 = "{0:<"+str(int(twidth/2))+"} {1:<"+str(int(twidth/2))+"}\n"
        col3 = "{0:<"+str(int(twidth/3))+"} {1:<"+str(int(twidth/3))+"} {2:<"+str(int(twidth/3))+"}\n"
        col4 = "{0:<"+str(int(twidth/4))+"} {1:<"+str(int(twidth/4))+"} {2:<"+str(int(twidth/4))+"} {3:<"+str(int(twidth/4))+"}\n" 
        
        out += sepformat.format("("+str(self.nanotube.n)+","+str(self.nanotube.m)+")_Capped_Nanotube")

        
        out += col2.format("N_dual_lattice_points",self.thomsonPoints.npoints)   
        out += col2.format("N_dual_lattice_energy",self.thomsonPoints.FinalEnergy)
         
        out += col2.format("N_carbon_atoms",self.carbonAtoms.npoints)
        try:
            out += col2.format("carbon_lattice_scale",self.carbonAtoms.FinalScale)
            out += col2.format("carbon_lattice_scaled_energy",str(self.carbonAtoms.FinalScaleEnergy)+" eV")
            out += col2.format("carbon_lattice_energy",str(self.carbonAtoms.FinalEnergy)+" eV")
            out += col2.format("carbon_lattice_energy_per_atom",str(self.carbonAtoms.FinalEnergy/self.carbonAtoms.npoints)+" eV")
        except:pass
        
        out += col2.format("average_cap_radius",str(self.radius)+" +- "+str(self.radius_std))
        out += col2.format("min_radius",self.radius_min)
        out += col2.format("max_radius",self.radius_max)
        try:out += col2.format("constrained_average_cap_radius",str(self.constrained_radius)+" +- "+str(self.constrained_radius_std))
        except:pass
        
        b  = self.carbonAtoms.getBounds()
        zlength = b[5]-b[2]
        out += col2.format("length",zlength)
        out += col2.format("surface_area",self.surfaceArea)
        out += col2.format("volume",self.volume)
        #out += col2.format("sphericity",self.sphericity)
        
        out += col1h.format("nanotube")
        out += col2.format("N_dual_lattice_points",self.nanotube.thomsonPoints.npoints)   
        out += col2.format("N_carbon_atoms",self.nanotube.carbonAtoms.npoints)
        out += col2.format("chirality",str(self.nanotube.n)+" "+str(self.nanotube.m))
        out += col2.format("radius",self.nanotube.rad)
        out += col2.format("circumference",self.nanotube.circumference)
        out += col2.format("length",self.nanotube.length)
        out += col2.format("surface_area",self.nanotube.surfaceArea)
        out += col2.format("cap_mapping_angle",math.degrees(self.nanotube.rotationAngle))
        
        out += col1h.format("cap")
        out += col2.format("N_dual_lattice_points",self.cap.thomsonPoints.npoints)   
        #out += col2.format("N_carbon_atoms",self.cap.carbonAtoms.npoints)
        
        
 #       f.write("n "+str(self.cappedNanotube.nanotube.n)+"\n")
#            f.write("m "+str(self.cappedNanotube.nanotube.m)+"\n")
#            f.write("Rad "+str(self.cappedNanotube.nanotube.rad)+"\n")
#            f.write("Circumference "+str(self.cappedNanotube.nanotube.circumference)+"\n")
#            f.write("Length "+str(self.cappedNanotube.nanotube.length + (2.0/self.cappedNanotube.nanotube.scale) )+"\n")
#            f.write("Surface_area "+str(self.cappedNanotube.nanotube.surfaceArea + 4*math.pi*(1.0/self.cappedNanotube.nanotube.scale))+"\n")
        
        
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
        
        print out
        
        return out    
    
    def get_single_line_description(self,carbonAtoms=True,dualLattice=True,carbonEnergy=True):
        scale = self.nanotube.scale
        IPperc = float(self.isolatedPentagons)/float(self.ringCount[5])*100.0
        
        des   = "CappedNanotube_n_"+str(self.nanotube.n)+"_m_"+str(self.nanotube.m)
        des+="_Length_"+str(self.nanotube.length+(2.0/self.nanotube.scale))
        des+="_IP%_"+str(IPperc)
        if(carbonAtoms):des+="_Nccap_"+str(self.cap.thomsonPoints.npoints*2 - 2)
        if(dualLattice):des+="_Ntcap_"+str(self.cap.thomsonPoints.npoints)
        if(carbonEnergy):
            try:des+="_Energy_"+str(self.carbonAtoms.FinalEnergy)
            except:des+="_Energy_"+str(self.thomsonPoints.FinalEnergy)
        else:des+="_Energy_"+str(self.thomsonPoints.FinalEnergy)
        
        return des
    
    def calcInfo(self):
        self.nanotube.calcInfo()
        
        printl("calculating capped nanotube info")
        
        try:
            self.radius,self.radius_std,self.radius_min,self.radius_max = self.calcAverageCapRadius(self.carbonAtoms.npoints,self.carbonAtoms.pos)
            printl("cap average radius",self.radius,"+-",self.radius_std)
        except:pass
        
        try:
            self.constrained_radius,self.constrained_radius_std,min,max = self.calcAverageCapRadius(self.carbonAtoms.npoints,self.carbonAtoms.constrained_pos)
            printl("cap constrained average radius",self.constrained_radius,"+-",self.constrained_radius_std)
        except:pass
        
#        try:
#            self.unconstrained_radius,self.unconstrained_radius_std,min,max = self.calcAverageCapRadius(self.carbonAtoms.npoints,self.carbonAtoms.unconstrained_pos)
#            printl("cap unconstrained average radius",self.unconstrained_radius,"+-",self.unconstrained_radius_std)
#        except:pass
        
        self.calculateSurfaceAreaVolume()
        
        #printl("max Z", numpy.max(self.carbonAtoms.pos[2::3]))
        
        
    
    def calcAverageCapRadius(self,npoints,pos):    
        xc = pos[0::3]
        yc = pos[1::3]
        zc = pos[2::3] 
        
        indexes = numpy.where(zc<0)[0]
        #printl("indexes",indexes)
              
        com = numpy.array([0,0,0],NPF)
        
        xd = xc[indexes]-com[0]
        yd = yc[indexes]-com[1]
        zd = zc[indexes]-com[2]
        
        #printl("xd",xd)
        #printl("yd",yd)
        #printl("zd",zd)
        
        radii = numpy.sqrt(xd*xd + yd*yd + zd*zd)
        
        #printl("radii",radii)
        return numpy.average(radii),numpy.std(radii),numpy.min(radii),numpy.max(radii)
    
    def construct(self):
        self.thomsonPoints = points.joinPointSets((self.cap.thomsonPoints,self.nanotube.thomsonPoints,
                                                                      self.reflectedCap.thomsonPoints))   
                                        
        self.thomsonPoints.PointSetLabel = "Capped Nanotube Dual Lattice Points"
        
        
        
    
    def resetSecondaryCap(self):
        try:self.cap
        except:
            printl("cap not constructed yet")
            return
        if(self.cap==None):
            printl("cap not constructed yet")
            return
        self.reflectedCap = cap.Cap()
        printh("resetting cap with ",self.cap.thomsonPoints.npoints,"dual lattice points")
        self.reflectedCap.setup(self.cap.thomsonPoints.npoints,
                                real=False,
                                free=False)
        
        for i in range(0,self.reflectedCap.thomsonPoints.npoints):
            self.reflectedCap.thomsonPoints.pos[i*3] = self.cap.thomsonPoints.pos[i*3]
            self.reflectedCap.thomsonPoints.pos[i*3+1] = self.cap.thomsonPoints.pos[i*3+1]
            self.reflectedCap.thomsonPoints.pos[i*3+2] = self.cap.thomsonPoints.pos[i*3+2]
            
            #self.reflectedCap.thomsonPoints.pos[i*3] *=-1.0
            self.reflectedCap.thomsonPoints.pos[i*3+1] *=-1.0
            self.reflectedCap.thomsonPoints.pos[i*3+2] *=-1.0
            
            x = self.reflectedCap.thomsonPoints.pos[i*3]*math.cos(self.nanotube.mappingAngle) - self.reflectedCap.thomsonPoints.pos[i*3+1]*math.sin(self.nanotube.mappingAngle)
            y = self.reflectedCap.thomsonPoints.pos[i*3]*math.sin(self.nanotube.mappingAngle) + self.reflectedCap.thomsonPoints.pos[i*3+1]*math.cos(self.nanotube.mappingAngle)
            z = self.reflectedCap.thomsonPoints.pos[i*3+2]
            self.reflectedCap.thomsonPoints.pos[i*3] = x + 2*self.nanotube.thomsonPointsCOM[0]
            self.reflectedCap.thomsonPoints.pos[i*3+1] = y + 2*self.nanotube.thomsonPointsCOM[1]
            self.reflectedCap.thomsonPoints.pos[i*3+2] +=  2*self.nanotube.thomsonPointsCOM[2] 
    
    def updateCaps(self):
        try:self.cap
        except:
            printl("cap not constructed yet")
            return
        if(self.cap==None):
            printl("cap not constructed yet")
            return
        
        printl("update caps",self.reflectedCap.thomsonPoints.npoints,
               self.thomsonPoints.npoints,
               self.cap.thomsonPoints.npoints,self.nanotube.thomsonPoints.npoints)
        
        for i in range(0,self.reflectedCap.thomsonPoints.npoints):
            self.cap.thomsonPoints.pos[i*3] = self.thomsonPoints.pos[i*3]
            self.cap.thomsonPoints.pos[i*3+1] = self.thomsonPoints.pos[i*3+1]
            self.cap.thomsonPoints.pos[i*3+2] = self.thomsonPoints.pos[i*3+2]    
            
            self.reflectedCap.thomsonPoints.pos[i*3] = self.thomsonPoints.pos[i*3]
            self.reflectedCap.thomsonPoints.pos[i*3+1] = self.thomsonPoints.pos[i*3+1]
            self.reflectedCap.thomsonPoints.pos[i*3+2] = self.thomsonPoints.pos[i*3+2]
            
            #self.reflectedCap.thomsonPoints.pos[i*3] *=-1.0
            self.reflectedCap.thomsonPoints.pos[i*3+1] *=-1.0
            self.reflectedCap.thomsonPoints.pos[i*3+2] *=-1.0
            
            x = self.reflectedCap.thomsonPoints.pos[i*3]*math.cos(self.nanotube.mappingAngle) - self.reflectedCap.thomsonPoints.pos[i*3+1]*math.sin(self.nanotube.mappingAngle)
            y = self.reflectedCap.thomsonPoints.pos[i*3]*math.sin(self.nanotube.mappingAngle) + self.reflectedCap.thomsonPoints.pos[i*3+1]*math.cos(self.nanotube.mappingAngle)
            z = self.reflectedCap.thomsonPoints.pos[i*3+2]
            self.reflectedCap.thomsonPoints.pos[i*3] = x + 2*self.nanotube.thomsonPointsCOM[0]
            self.reflectedCap.thomsonPoints.pos[i*3+1] = y + 2*self.nanotube.thomsonPointsCOM[1]
            self.reflectedCap.thomsonPoints.pos[i*3+2] +=  2*self.nanotube.thomsonPointsCOM[2]  
            
        offset = self.cap.thomsonPoints.npoints+self.nanotube.thomsonPoints.npoints
        for i in range(0,self.reflectedCap.thomsonPoints.npoints):
            self.thomsonPoints.pos[(i+offset)*3] = self.reflectedCap.thomsonPoints.pos[i*3]
            self.thomsonPoints.pos[(i+offset)*3+1] = self.reflectedCap.thomsonPoints.pos[i*3+1]
            self.thomsonPoints.pos[(i+offset)*3+2] = self.reflectedCap.thomsonPoints.pos[i*3+2]   
    
    def resetCap(self):
        self.cap = cap.Cap()
    
    def setupCap(self,Nd,seed=None):
        self.cap.setup(Nd,seed=seed)
    
    def resetNanotube(self): 
        self.nanotube = nanotube.Nanotube()
        self.cap = None
        self.reflectedCap = None
        
    
    def setupNanotube(self,n,m,l=None):
        self.nanotube.setup(n,m,l=l)
        
    
    def setZcutoff(self,cutoff):
        self.nanotube.cutoff=cutoff
    
    def setZcutoffFromCapPoints(self,cappoints):
        '''
        need to have this only in capped nanotube class
        '''
        self.nanotube.setZcutoff(cappoints)
        
    
    def calculateSurfaceAreaVolume(self):        
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
        
        
        printl("C nanotube surfaceArea",self.surfaceArea,"volume", self.volume)
        printl("C time for vol calc",time.time()-stime)
        #        stime = time.time()
#        self.surfaceArea = 0
#        self.volume = 0
#        for i in range(0,self.nrings):
#            #print "ring",i,"verts",self.VertsPerRingCount[i]
#
#            v1,v2,v3 = self.Rings[i*self.MaxVerts],self.Rings[i*self.MaxVerts+1],self.Rings[i*self.MaxVerts+2]      
#              
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
#            #check outward
#            
#            dp = numpy.dot(p1,norm)
#            if(dp<0):
#                norm = normalise(numpy.cross(p3-p2,p3-p1))
#                dp = numpy.dot(p1,norm)
#                print "corrected",dp
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
#                dp = numpy.dot(p1,cp)
#                if(dp<0):
#                    cp = numpy.cross(p2,p1)
#                    dp = numpy.dot(p1,cp)
#                    print "corrected",dp
#                
#                center+= p1/self.VertsPerRingCount[i]
#                
#                print jindex0,jindex1,p1,p2,cp
#                totxyz+=cp
#            
#            
#            
#            area = (numpy.dot(totxyz,norm)/2.0)
#            
#            print center,area
#            
#            self.surfaceArea += area
#            
#            self.volume += (center[0] * norm[0] * area)
#            
#            #print "area of ring",abs(area/2.0)
#                
#        #self.surfaceArea,self.volume = 1,1
#        printl("fullerene surfaceArea",self.surfaceArea,"volume", self.volume)
#        printl("time for vol calc",time.time()-stime)
        
    def calculateCarbonRings(self, MaxNebs = 3,MaxVerts= 9):
        outdict = ringcalculator.calculate_rings(self.carbonAtoms,MaxNebs = MaxNebs,MaxVerts=MaxVerts)
        
        for key, val in outdict.items():
            #print key,outdict[key],"self."+key+" = outdict[key]"
            exec "self."+key+" = outdict[key]"
        
        return outdict
        
    def getCapDualLatticeEstimate(self,n,m):
        printl("getting cap estimates")
        
        self.nanotube.setup_params(n,m)
        
#        Nc = self.nanotube.NperU
#        Nd = self.nanotube.Nhex
#        length = self.nanotube.magT
#        circumference = 2.0*math.pi*self.nanotube.rad
#        surfaceArea = circumference*length
#        lengthScaled = length*self.nanotube.scale
#        circumferenceScaled = circumference*self.nanotube.scale
#        surfaceAreaScaled = lengthScaled*circumferenceScaled
#        
#        
#        self.tubeDualLatticeDensity = float(self.nanotube.Nhex)/surfaceAreaScaled
#        self.tubeCarbonAtomDensity = float(Nc)/surfaceAreaScaled
#        
#        #self.capThomsonPointEstimate = int(math.ceil(self.nanotube.tubeDualLatticeDensity*2.0*math.pi))
#        #self.capCarbonAtomEstimate = int(math.ceil(self.nanotube.tubeCarbonAtomDensity*2.0*math.pi))
#        
#        #based on C60
#        
#        dualRho  = 0.22
#        
#        self.capThomsonPointEstimate  = int(math.ceil(dualRho*(4.0*math.pi*self.nanotube.rad*self.nanotube.rad)/2.0))
#        #self.capCarbonAtomEstimate = 2*self.capThomsonPointEstimate- 2
#
#        printl("nanotube dual lattice density",self.tubeDualLatticeDensity,self.nanotube.rad,
#               dualRho*(4.0*math.pi*self.nanotube.rad*self.nanotube.rad),
#               "npoints in cap estimate",self.capThomsonPointEstimate)
        
        #based on C60
        dualRho  = 0.22
        estimate = int(math.ceil(dualRho*(4.0*math.pi*self.nanotube.rad*self.nanotube.rad)/2.0))
        
        return estimate
            
        