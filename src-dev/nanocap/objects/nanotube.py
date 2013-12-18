'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Aug 24 2011
Copyright Marc Robinson 2013
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

Nanotube base class. Contains instances of Points
Routines for setting up carbon atoms, dual lattice 
and symmetry points

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
'''

import os,sys,math,copy,random,time,ctypes,fractions
from nanocap.core.globals import *
import nanocap.core.globals as globals
import numpy
import nanocap.objects.points as points
from nanocap.core.util import *
from nanocap.clib import clib_interface
from nanocap.core import ringcalculator 
clib = clib_interface.clib
    
from decimal import *
import scipy.special


class Nanotube(object):
    def __init__(self):
        '''tube dual lattice points'''
        self.thomsonPoints = points.Points("Nanotube Dual Lattice Points")
        self.thomsonPoints.initArrays(0)
        '''additional damp flags for attaching spring forces if needed'''
        self.thomsonPoints.dampflags = numpy.zeros(0,NPI)
        self.thomsonPoints.dampflagspos = numpy.zeros(0,NPF)
        self.dampedlength = 0.5
        self.damping = False
        self.k = 10.0
        
        self.carbonAtoms = None
        #self.cappedTubeCarbonAtoms = None
        '''current the full system is the only the tube dual lattice'''
        #self.cappedthomsonPoints = self.thomsonPoints
        '''minimum length of nanotube = cutoffFactor*Zcutoff'''
        self.cutoffFactor = 1.5
    
    
#    def __repr__(self):
#        twidth = 80
#        
#        out = ""
#        sepformat = "{0:=^"+str(twidth)+"} \n"
#        
#        col1 = "{0:<"+str(twidth)+"} \n"
#        col1h = "{0:-^"+str(twidth)+"} \n"
#        col2 = "{0:<"+str(int(twidth/2))+"} {1:<"+str(int(twidth/2))+"}\n"
#        col3 = "{0:<"+str(int(twidth/3))+"} {1:<"+str(int(twidth/3))+"} {2:<"+str(int(twidth/3))+"}\n"
#        col4 = "{0:<"+str(int(twidth/4))+"} {1:<"+str(int(twidth/4))+"} {2:<"+str(int(twidth/4))+"} {3:<"+str(int(twidth/4))+"}\n" 
#        
#        out += sepformat.format(" C"+str(self.carbonAtoms.npoints)+" Nanotube ")
#
#        
#        out += col2.format("N_dual_lattice_points",self.thomsonPoints.npoints)   
#        out += col2.format("N_dual_lattice_energy",self.thomsonPoints.FinalEnergy)
#         
#        out += col2.format("N_carbon_atoms",self.carbonAtoms.npoints)
#        try:
#            out += col2.format("carbon_lattice_scale",self.carbonAtoms.FinalScale)
#            out += col2.format("carbon_lattice_scaled_energy",str(self.carbonAtoms.FinalScaleEnergy)+" eV")
#            out += col2.format("carbon_lattice_energy",str(self.carbonAtoms.FinalEnergy)+" eV")
#            out += col2.format("carbon_lattice_energy_per_atom",str(self.carbonAtoms.FinalEnergy/self.carbonAtoms.npoints)+" eV")
#        except:pass
#        
#        out += col2.format("average_radius",str(self.radius)+" +- "+str(self.radius_std))
#        out += col2.format("min_radius",self.radius_min)
#        out += col2.format("max_radius",self.radius_max)
#        try:out += col2.format("constrained_average_radius",str(self.constrained_radius)+" +- "+str(self.constrained_radius_std))
#        except:pass
#        
#        out += col2.format("surface_area",self.surfaceArea)
#        out += col2.format("volume",self.volume)
#        out += col2.format("sphericity",self.sphericity)
#        
##        try:out += col2.format("unconstrained_average_radius",str(self.unconstrained_radius)+" +- "+str(self.unconstrained_radius_std))
##        except:pass
#    
#        out += col1h.format("ring_stats")
#        for i in range(3,len(self.ringCount)):
#            if(i==5):
#                out += col2.format("number_of_"+str(i)+"-agons ",str(self.ringCount[i])+" IP "+str(self.isolatedPentagons))
#            else:
#                out += col2.format("number_of_"+str(i)+"-agons ",self.ringCount[i])                    
#           
#        out += col2.format("%_6-agons",self.percHex)    
#        
#        
#        
#        out += sepformat.format("")
#        return out
    
    
    def get_info(self):
        length = 80
        lines = [ ["Nanotube Information",],
                  ["Chirality:", "(n=",self.n,", m=",self.m,")"],
                  ["Length:", self.length],
                  ["Radius:", self.rad],
                  ["NCarbon Atoms:", self.Nc],
                  ["NDual Lattice:", self.Nd],
                  ["theta_A",math.degrees(self.theta_A)],
                  ["theta_a1_R",math.degrees(self.theta_a1_R)],
                  ["theta_Ch_R",math.degrees(self.theta_Ch_R)]
                  ]

        for key in ["A","B","D","I1","I2","I3"]:
            lines.append(["phi_"+key,math.degrees(eval("self.phi_"+key))])
        
        lines.append(["z_boundary",self.z_boundary])
        for key in ["A","B","D","I1","I2","I3"]:
            lines.append(["delta_"+key,math.degrees(eval("self.delta_"+key))])
        
        
        info= ""
        for line in lines:
            info += get_centered_string("-",length,line)
        return info
        
    def setZcutoff(self,cappoints):
        '''
        The force cutoff along the nanotube axis. Points past this cutoff do not
        contribute to dual lattice minimisation.
        '''
        a =  [0.948452364196,1.02360096456,0.251753131336] 
        self.cutoff = a[0]*math.exp(a[1]/((cappoints/(2*math.pi))**a[2]))
        try:
            zpos = self.thomsonPoints.pos[2::3]
            if(self.cutoff > numpy.max(zpos)):
                printl("***ERROR NANOTUBE TOO SHORT FOR CONSTRUCTION! INCREASE U***")
        except:
            pass
        printl("nanotube cutoff",self.cutoff)    
    
    def calcInfo(self):
        printl("calculating nanotube info")
        
        try:
            self.radius,self.radius_std = self.calcAverageCapRadius(self.carbonAtoms.npoints,self.carbonAtoms.pos)
            printl("cap average radius",self.constrained_radius,"+-",self.constrained_radius_std)
        except:pass
        
#        try:
#            self.constrained_radius,self.constrained_radius_std = self.calcAverageCapRadius(self.carbonAtoms.npoints,self.carbonAtoms.constrained_pos)
#            printl("cap constrained average radius",self.constrained_radius,"+-",self.constrained_radius_std)
#        except:pass
#        try:
#            self.unconstrained_radius,self.unconstrained_radius_std = self.calcAverageCapRadius(self.carbonAtoms.npoints,self.carbonAtoms.unconstrained_pos)
#            printl("cap unconstrained average radius",self.unconstrained_radius,"+-",self.unconstrained_radius_std)
#        except:pass
    
    def calcAverageCapRadius(self,npoints,pos):    
        xc = pos[0::3]
        yc = pos[1::3]
        zc = pos[2::3] 
        
        indexes = numpy.where(zc<0)[0]
        printl("indexes",indexes)
              
        com = numpy.array([0,0,0],NPF)
        
        xd = xc[indexes]-com[0]
        yd = yc[indexes]-com[1]
        zd = yc[indexes]-com[2]
        
        
        radii = numpy.sqrt(xd*xd + yd*yd + zd*zd)
        return numpy.average(radii),numpy.std(radii)
    
#    def calculateSurfaceAreaVolume(self):        
#        printl("using nrings",self.nrings,"to determine area and volume")
#        '''
#        was going to retriangulate the carbon atoms, but there is no need since the
#        rings have been calculated. Use these along with the normals to determine the
#        volume using Gauss' thereom.    
#        '''
#        stime = time.time()
#        self.surfaceArea,self.volume = ringcalculator.calculate_volume_from_rings(self.cappedTubeCarbonAtoms,
#                                                                                  self.nrings,
#                                                                                  self.MaxVerts,
#                                                                                  self.Rings,
#                                                                                  self.VertsPerRingCount)
#        
#        
#        printl("C nanotube surfaceArea",self.surfaceArea,"volume", self.volume)
#        printl("C time for vol calc",time.time()-stime)
#    
#    def calculateCarbonRings(self, MaxNebs = 3,MaxVerts= 9):
#        outdict = ringcalculator.calculate_rings(self.cappedTubeCarbonAtoms,MaxNebs = MaxNebs,MaxVerts=MaxVerts)
#        
#        for key, val in outdict.items():
#            #print key,outdict[key],"self."+key+" = outdict[key]"
#            exec "self."+key+" = outdict[key]"
#        
#        return outdict
    
    
#    def getCapEstimates(self,n,m):
#        printl("getting cap estimates")
#        
#        self.setup_params(n,m)
#        
#        Nc = self.NperU
#        Nd = self.Nhex
#        
#        length = self.magT
#        circumference = 2.0*math.pi*self.rad
#        surfaceArea = circumference*length
#        
#        lengthScaled = length*self.scale
#        circumferenceScaled = circumference*self.scale
#        surfaceAreaScaled = lengthScaled*circumferenceScaled
#        
#        self.tubeDualLatticeDensity = float(self.Nhex)/surfaceAreaScaled
#        self.tubeCarbonAtomDensity = float(Nc)/surfaceAreaScaled
#        
#        self.capThomsonPointEstimate = int(math.ceil(self.tubeDualLatticeDensity*2.0*math.pi))
#        self.capCarbonAtomEstimate = int(math.ceil(self.tubeCarbonAtomDensity*2.0*math.pi))
#        
#        #based on C60
#        
#        dualRho  = 0.22
#        
#        self.capThomsonPointEstimate  = int(math.ceil(dualRho*(4.0*math.pi*self.rad*self.rad)/2.0))
#        self.capCarbonAtomEstimate = 2*self.capThomsonPointEstimate- 2
#
#        printl("nanotube dual lattice density",self.tubeDualLatticeDensity,self.rad,dualRho*(4.0*math.pi*self.rad*self.rad),
#               "npoints in cap estimate",self.capThomsonPointEstimate)
        
    
    def setup_length(self,l=None):
        lengthScaled = self.magT*self.scale
        circumferenceScaled = 2.0*math.pi*self.rad*self.scale
        surfaceAreaScaled = lengthScaled*circumferenceScaled
        tubeDualLatticeDensity = float(self.Nhex)/surfaceAreaScaled
        capThomsonPointEstimate = int(math.ceil(tubeDualLatticeDensity*2.0*math.pi))
        
        self.setZcutoff(capThomsonPointEstimate)
        
        self.minimumLengthScaled = (self.cutoff*self.cutoffFactor)
        self.minimumLength = self.minimumLengthScaled/self.scale
        
        if(l==None):
            printl("no length detected, using minimumLength")
            u = math.ceil(self.minimumLength/magnitude(self.T))
            self.length = self.minimumLength
            printl("estimated nanotube unit cells:",u)
            
        elif(l<=self.minimumLength):
            printl("length less than minimumLength, using minimumLength")
            u = math.ceil(self.minimumLength/magnitude(self.T))
            self.length = self.minimumLength
            printl("estimated nanotube unit cells:",u)
            
        else:
            printl("length detected, estimating units",l)
            u = math.ceil(l/magnitude(self.T))
            printl("estimated nanotube unit cells:",u)   
            self.length = l

        self.u = int(u)
        self.Nc = self.NperU*self.u
        self.Nd = self.Nhex*self.u
    
    def setup_params(self,n,m):
        self.n = n
        self.m = m
        
        self.d = fractions.gcd(self.n, self.m)
        self.dR = fractions.gcd(2*self.n+self.m, 2*self.m+self.n)
        self.Nhex  = 2*(self.n*self.n + self.m*self.m + self.n*self.m)/self.dR
        #printl("NHex",self.Nhex)
        self.NperU = self.Nhex*2
        
        self.acc = 1.42
        self.a0 = math.sqrt(3)*self.acc
        self.a1 = (self.a0/2.0)*numpy.array([math.sqrt(3),1])
        self.a2 = (self.a0/2.0)*numpy.array([math.sqrt(3),-1])
        self.Ch = self.m*self.a2 + self.n*self.a1
        self.magCh = magnitude(self.Ch)
        self.ChTheta  = math.atan((math.sqrt(3) * float(self.m)) /float( 2*self.n+self.m))
        self.rad = self.magCh/(2*math.pi)
        self.scale = 1.0/self.rad 
         
        self.t1 = (2*self.m+self.n)/self.dR
        self.t2 = -(2*self.n+self.m)/self.dR
        
        self.T = self.t1*self.a1 + self.t2*self.a2
        self.magT = magnitude(self.T)
        
        if(self.t1 == 0): pstep  = 1
        else: pstep = self.t1
        
        for p in range(-numpy.abs(pstep),numpy.abs(pstep)+1):
            for q in range(-numpy.abs(self.t2),numpy.abs(self.t2)+1):
                eq1 = self.t1*q - self.t2*p
                eq2 = m*p - n*q
               # print p,q,eq1,eq2
                if(eq1==1 and eq1 <= self.Nhex and eq1 >0):
                    if(eq2 <= self.Nhex and eq2 >0):
                        #print "p,q",p,q
                        np=p
                        nq=q
        self.p=np
        self.q=nq
        
        '''
        symmetry vector R
        '''
        self.R = self.p*self.a1 + self.q*self.a2
        self.magR = magnitude(self.R)
    
    def setup_angles_and_offsets(self):
        
        self.theta_A = 2.0*math.pi/float(self.Nhex)
        
        self.theta_a1_R = math.atan((math.sqrt(3) * float(self.q)) /float( 2*self.p + self.q) )
        
        self.theta_Ch_R = self.ChTheta-self.theta_a1_R
        
        self.z_boundary = magnitude(self.T)/math.sin(self.theta_Ch_R)
        
        self.phi_A = 0.0
        self.phi_B = self.acc*math.cos((math.pi/6.0)-self.ChTheta) * (1.0/self.rad)
        self.phi_D = 2.0*self.phi_B
        self.phi_I1 = self.phi_B/2.0
        self.phi_I2 = self.phi_I1 + (math.sqrt(3.0)/2.0)*self.acc*math.cos(self.ChTheta) * (1.0/self.rad)
        self.phi_I3 = self.phi_I1 - (math.sqrt(3.0)/2.0)*self.acc*math.sin(self.ChTheta + (math.pi/6.0)) * (1.0/self.rad)
        
        self.delta_A = 0.0
        self.delta_B = self.acc*math.sin((math.pi/6.0)-self.ChTheta)
        self.delta_D = 2.0*self.delta_B
        self.delta_I1 = self.delta_B/2.0
        self.delta_I2 = self.delta_I1 - (math.sqrt(3.0)/2.0)*self.acc*math.sin(self.ChTheta)    
        self.delta_I3 = self.delta_I1 - (math.sqrt(3.0)/2.0)*self.acc*math.sin(math.pi/3.0 - self.ChTheta)

        printh("nanotube construction angles:")
        printh("theta_A",math.degrees(self.theta_A))
        printh("theta_a1_R",math.degrees(self.theta_a1_R))
        printh("theta_Ch_R",math.degrees(self.theta_Ch_R))
        for key in ["A","B","D","I1","I2","I3"]:
            printh("phi_"+key,math.degrees(eval("self.phi_"+key)))
        
        printh("nanotube construction offsets:")
        printh("z_boundary",self.z_boundary)
        for key in ["A","B","D","I1","I2","I3"]:
            printh("delta_"+key,eval("self.delta_"+key))

    
    
    def get_unit_cell_xyz(self,i,X):
        angle = eval("self.phi_"+X)
        offset = eval("self.delta_"+X)
        
        
        x = self.rad * math.cos(float(i)*self.theta_A + angle)
        y = self.rad * math.sin(float(i)*self.theta_A + angle)
        k = numpy.float(int(float(i)*self.magR/self.z_boundary))
        #z = Decimal((float(i)*self.magR  - float(k)*self.z_boundary) * math.sin(self.theta_Ch_R))
        z = (float(i)*self.magR  - float(k)*self.z_boundary) * math.sin(self.theta_Ch_R) - offset  
        #if(X=="D"):
        #    printl(angle,offset,x,y,k,z)
        return x,y,z        
    
    def get_unit_cell_xyz_2D(self,i,X):
        angle = eval("self.phi_"+X)
        offset = eval("self.delta_"+X)
        x = float(i)*(self.theta_A/(2.0*math.pi)) + angle/(2.0*math.pi) 
        x*= self.magCh
        k = numpy.float(int(float(i)*self.magR/self.z_boundary))
        
        z = (float(i)*self.magR  - float(k)*self.z_boundary) * math.sin(self.theta_Ch_R) - offset
        return x,z
    
    def calc_rotation_angle(self):
        distToMid = self.tubeIntersectPoints2D.pos[2::3] - self.thomsonPointsCOM[2]
        #printl("distToMid",distToMid)
        axespoint = numpy.argmin(numpy.abs(distToMid))
        '''
        find the x-position of this point which corresponds to angle around circumference.
        '''
        offset = self.tubeIntersectPoints2D.pos[0::3][axespoint]
        angletox = -1*(offset/(magnitude(self.Ch)*self.scale))*2.0*math.pi
        
        printl("angle to x found via intersection points",angletox,"axespoint",axespoint,"bisection:",
               self.tubeIntersectPoints2D.pos[2::3][axespoint]-self.thomsonPointsCOM[2])
        
        self.rotationAngle = angletox
    
    def rotate(self):
        cr = math.cos(self.rotationAngle)
        sr = math.sin(self.rotationAngle)
#
        self.carbonAtoms.pos[0::3] -= self.carbonAtomsCOM[0]
        self.carbonAtoms.pos[1::3] -= self.carbonAtomsCOM[1]
        self.carbonAtoms.pos[2::3] -= self.carbonAtomsCOM[2]

        xc = self.carbonAtoms.pos[0::3]*cr
        xs = self.carbonAtoms.pos[0::3]*sr
        yc = self.carbonAtoms.pos[1::3]*cr
        ys = self.carbonAtoms.pos[1::3]*sr
        self.carbonAtoms.pos[0::3] = xc - ys
        self.carbonAtoms.pos[1::3] = xs + yc
#        
#        print self.carbonAtoms.pos[0]
#     
        self.carbonAtoms.pos[0::3] += self.carbonAtomsCOM[0]
        self.carbonAtoms.pos[1::3] += self.carbonAtomsCOM[1]
        self.carbonAtoms.pos[2::3] += self.carbonAtomsCOM[2]
#        
        
        self.thomsonPoints.pos[0::3] -= self.thomsonPointsCOM[0]
        self.thomsonPoints.pos[1::3] -= self.thomsonPointsCOM[1]
        self.thomsonPoints.pos[2::3] -= self.thomsonPointsCOM[2]
        
        xc = self.thomsonPoints.pos[0::3]*cr
        xs = self.thomsonPoints.pos[0::3]*sr
        yc = self.thomsonPoints.pos[1::3]*cr
        ys = self.thomsonPoints.pos[1::3]*sr
        self.thomsonPoints.pos[0::3] = xc - ys
        self.thomsonPoints.pos[1::3] = xs + yc
#        
#        print self.carbonAtoms.pos[0]
#     
        self.thomsonPoints.pos[0::3] += self.thomsonPointsCOM[0]
        self.thomsonPoints.pos[1::3] += self.thomsonPointsCOM[1]
        self.thomsonPoints.pos[2::3] += self.thomsonPointsCOM[2]
    
    
    def checkMappingAngle(self,deltheta=0.0001):
        '''        
        soo atm the nanotube has been rotated such that the 1,0,0 axis is inline with the bisected C-C bond (also Hex-Hex bond) at the midz point
        This means we can return MappingAngle = 0!, but for now this will act as a check for 0 mapping angle (it will return quickly if correct)
        
        '''
        self.mappingAngle = 0.0
        
        atoms = points.Points("")
        atoms.initArrays(self.thomsonPoints.npoints)
        atoms.pos = numpy.copy(self.thomsonPoints.pos)
        atomsCOM = self.thomsonPointsCOM
        atoms.pos[0::3] -= atomsCOM[0]
        atoms.pos[1::3] -= atomsCOM[1]
        atoms.pos[2::3] -= atomsCOM[2]
        
        p1 = numpy.array([-1.5,0.0,atomsCOM[2]])
        p2 = numpy.array([1.5,0.0,atomsCOM[2]])
        #self.XAxis = rendering.LineActor(p1,p2,(1,0,0))
        
        p1 = numpy.array([0.0,0.0,atomsCOM[2]])
        p2 = numpy.array([0.0,1.5,atomsCOM[2]])
#        p1 = numpy.array([0.0,0.0,atomsCOM[2]])
#        p2 = numpy.array([x0,y0,atomsCOM[2]])
        #self.YAxis = rendering.LineActor(p1,p2,(0,1,0))
        
        #atoms.pos[0::3] *= -1
        #atoms.pos[0::3] *= -1
        atoms.pos[1::3] *= -1
        atoms.pos[2::3] *= -1  

        
        clib.get_mapping_angle.restype = ctypes.c_double
        self.mappingAngle = clib.get_mapping_angle(ctypes.c_int(atoms.npoints),
                                                   atoms.pos.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                                                   ctypes.c_int(self.thomsonPoints.npoints),
                                                   self.thomsonPoints.pos.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                                                   atomsCOM.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                                                   ctypes.c_double(deltheta))

        d = fractions.gcd(self.n, self.m)
         
        printl("**This should equal 0: angle", self.mappingAngle, "degrees:",math.degrees(self.mappingAngle),"or",
               (360/d)-math.degrees(self.mappingAngle),360/d)
        
        if(self.mappingAngle==-1.0):
            raw_input("Could not find mapping angle in C, suggests cap transformation will fail. Press enter ...")
            self.mappingAngle = deltheta
        
        if(self.mappingAngle==deltheta):return

        xc = atoms.pos[0::3]*math.cos(self.mappingAngle)
        xs = atoms.pos[0::3]*math.sin(self.mappingAngle)
        yc = atoms.pos[1::3]*math.cos(self.mappingAngle)
        ys = atoms.pos[1::3]*math.sin(self.mappingAngle)
        atoms.pos[0::3] = xc - ys
        atoms.pos[1::3] = xs + yc
#        
        atoms.pos[0::3] += atomsCOM[0]
        atoms.pos[1::3] += atomsCOM[1]
        atoms.pos[2::3] += atomsCOM[2]
        
        self.rotatedThomsonPoints = atoms
                
    def setup(self,n,m,l=None):
        printl("setting params n",n,"m",m)
        self.setup_params(n,m)
        
        printl("setting length",l)
        self.setup_length(l)
        
        self.setup_angles_and_offsets()
        
        self.carbonAtoms = points.Points("Nanotube Carbon Atoms")  
        self.carbonAtoms.initArrays(self.Nc)
        self.carbonAtomsCOM = numpy.zeros(3,NPF)
        
        self.thomsonPoints.initArrays(self.Nd)
        self.thomsonPoints.freeflags = numpy.zeros(self.thomsonPoints.npoints,NPI)
        self.thomsonPoints.freeflagspos = numpy.zeros(self.thomsonPoints.npoints*3,NPF)
        self.thomsonPoints.dampflags = numpy.zeros(self.thomsonPoints.npoints,NPI)
        self.thomsonPoints.dampflagspos = numpy.zeros(self.thomsonPoints.npoints*3,NPF)
        self.thomsonPoints.realflags = numpy.ones(self.thomsonPoints.npoints,NPI)
        self.thomsonPoints.realflagspos = numpy.ones(self.thomsonPoints.npoints*3,NPF)
        self.thomsonPointsCOM=numpy.zeros(3,NPF)
        
        self.tubeIntersectPoints2D = points.Points("Nanotube 2D Intersection Points")  
        self.tubeIntersectPoints2D.initArrays((self.Nc/2)*3 )
        self.tubeIntersectPoints2DCOM = numpy.zeros(3,NPF)
        
        stime = time.time()
        
        boundary = float(self.u)*self.magT
#        atomcount = 0
#        dualcount = 0
#        intersectcount = 0
#        for u in range(0,self.u):
#            for i in range(0,self.Nhex):
#                for key in ["A","B"]:
#                    x,y,z = self.get_unit_cell_xyz(i,key)
#                    z+=float(u)*self.magT
#                    if(z<1e-6):z+=boundary
#                    if(z > (boundary-1e-6)):z-=boundary
#                    self.carbonAtoms.pos[atomcount*3] = x
#                    self.carbonAtoms.pos[atomcount*3+1] = y 
#                    self.carbonAtoms.pos[atomcount*3+2] = z
#                    atomcount+=1 
#                for key in ["D",]:
#                    x,y,z = self.get_unit_cell_xyz(i,key)
#                    z+=float(u)*self.magT
#                    #printl("check z, 0, boundary",z,boundary-1e-12)
#                    if(z<1e-6):z+=boundary
#                    if(z > (boundary-1e-6)):z-=boundary
#                    self.thomsonPoints.pos[dualcount*3] = x
#                    self.thomsonPoints.pos[dualcount*3+1] = y 
#                    self.thomsonPoints.pos[dualcount*3+2] = z
#                    #printl(dualcount,x,y,z,boundary,boundary-1e-6)
#                    dualcount+=1   
#                for key in ["I1","I2","I3"]:
#                    x,z = self.get_unit_cell_xyz_2D(i,key)
#                    z+=float(u)*self.magT
#                    if(z<1e-6):z+=boundary
#                    if(z > (boundary-1e-6)):z-=boundary
#                    self.tubeIntersectPoints2D.pos[intersectcount*3] = x
#                    self.tubeIntersectPoints2D.pos[intersectcount*3+1] = 0.0 
#                    self.tubeIntersectPoints2D.pos[intersectcount*3+2] = z
#                    intersectcount+=1  
#                #raw_input()     
#        
#        printl("time taken for Python construct",time.time()-stime)
        stime = time.time()
        clib.build_nanotube(ctypes.c_int(self.thomsonPoints.npoints),
                            self.thomsonPoints.pos.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                            ctypes.c_int(self.carbonAtoms.npoints),
                            self.carbonAtoms.pos.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                            ctypes.c_int(self.tubeIntersectPoints2D.npoints),
                            self.tubeIntersectPoints2D.pos.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                            ctypes.c_int(self.Nhex),
                            ctypes.c_double(self.u),
                            ctypes.c_double(self.magT),
                            ctypes.c_double(self.magR),
                            ctypes.c_double(self.magCh),
                            ctypes.c_double(self.rad),
                            ctypes.c_double(self.theta_A),
                            ctypes.c_double(self.theta_Ch_R),
                            ctypes.c_double(self.z_boundary),
                            
                            ctypes.c_double(self.phi_A),
                            ctypes.c_double(self.phi_B),
                            ctypes.c_double(self.phi_D),
                            ctypes.c_double(self.phi_I1),
                            ctypes.c_double(self.phi_I2),
                            ctypes.c_double(self.phi_I3),
                            
                            ctypes.c_double(self.delta_A),
                            ctypes.c_double(self.delta_B),
                            ctypes.c_double(self.delta_D),
                            ctypes.c_double(self.delta_I1),
                            ctypes.c_double(self.delta_I2),
                            ctypes.c_double(self.delta_I3))
           
        printl("time taken for c construct",time.time()-stime)
                      
        printl("finished loop")      
        self.carbonAtoms.pos*=self.scale 
        self.thomsonPoints.pos*=self.scale 
        self.tubeIntersectPoints2D.pos*=self.scale     
        
        minZ = numpy.min(self.thomsonPoints.pos[2::3])
        printh("minZ",minZ)
        printh("boundary",boundary)
        self.thomsonPoints.pos[2::3]-= minZ
        self.carbonAtoms.pos[2::3]-= minZ
        self.tubeIntersectPoints2D.pos[2::3]-= minZ
        
        zremove = numpy.where(self.thomsonPoints.pos[2::3]>self.length*self.scale)[0]
        self.thomsonPoints.removeIndexes(zremove)
        zremove = numpy.where(self.carbonAtoms.pos[2::3]>self.length*self.scale)[0]
        self.carbonAtoms.removeIndexes(zremove)
        zremove = numpy.where(self.tubeIntersectPoints2D.pos[2::3]>self.length*self.scale)[0]
        self.tubeIntersectPoints2D.removeIndexes(zremove)
        
        printl("removed cutoff")   
        
        if(self.damping):
            for i in range(0,self.thomsonPoints.npoints):
                if(self.thomsonPoints.pos[i*3+2]<self.dampedlength):
                    self.thomsonPoints.freeflags[i] = 1.0
                    self.thomsonPoints.freeflagspos[i*3] = 1.0
                    self.thomsonPoints.freeflagspos[i*3+1] = 1.0
                    self.thomsonPoints.freeflagspos[i*3+2] = 1.0 
                    self.thomsonPoints.dampflags[i] = 1.0
                    self.thomsonPoints.dampflagspos[i*3] = 1.0
                    self.thomsonPoints.dampflagspos[i*3+1] = 1.0
                    self.thomsonPoints.dampflagspos[i*3+2] = 1.0
                
        self.thomsonPointsCOM = numpy.array([0.0,0.0,
                                                 (numpy.sum(self.thomsonPoints.pos[2::3]))/self.thomsonPoints.npoints])
        self.carbonAtomsCOM = numpy.array([0.0,0.0,
                                               (numpy.sum(self.carbonAtoms.pos[2::3]))/self.carbonAtoms.npoints])
        
        printl("self.thomsonPointsCOM",self.thomsonPointsCOM)
        
        self.thomsonPoints.pos0 = numpy.copy(self.thomsonPoints.pos)   
        
        self.calc_rotation_angle()
        
        self.rotate()
        
        '''this should be zero if we have found the correct rotation axes'''
        self.checkMappingAngle()
        
        self.Nc = self.carbonAtoms.npoints
        self.Nd = self.thomsonPoints.npoints
        self.circumference = 2.0*math.pi*self.rad
        self.surfaceArea = self.circumference*self.length
        self.radScaled = 1.0
        self.lengthScaled = self.length*self.scale
        self.circumferenceScaled = 2.0*math.pi* self.radScaled
        self.surfaceAreaScaled = self.circumferenceScaled*self.lengthScaled
        self.densityScaled = float(self.Nc)/self.surfaceAreaScaled 
        self.density = float(self.Nc)/self.surfaceArea
        printh("boundary",boundary)
        #raw_input()
        
        print self.get_info()
   
        

        
if(__name__=="__main__"):
    nanotube = nanotube()
    nanotube.setup(3,3,2)

