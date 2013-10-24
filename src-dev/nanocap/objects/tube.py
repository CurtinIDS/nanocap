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
clib = clib_interface.clib
    
from decimal import *
import scipy.special


class nanotube(object):
    def __init__(self):
        '''tube dual lattice points'''
        self.tubeThomsonPoints = points.Points("Nanotube Dual Lattice Points")
        self.tubeThomsonPoints.initArrays(0)
        '''additional damp flags for attaching spring forces if needed'''
        self.tubeThomsonPoints.dampflags = numpy.zeros(0,NPI)
        self.tubeThomsonPoints.dampflagspos = numpy.zeros(0,NPF)
        self.dampedlength = 0.5
        self.damping = False
        self.k = 10.0
        
        self.tubeCarbonAtoms = None
        self.cappedTubeCarbonAtoms = None
        '''current the full system is the only the tube dual lattice'''
        self.cappedTubeThomsonPoints = self.tubeThomsonPoints
        '''minimum length of nanotube = cutoffFactor*Zcutoff'''
        self.cutoffFactor = 1.5
    
    
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
            zpos = self.tubeThomsonPoints.pos[2::3]
            if(self.cutoff > numpy.max(zpos)):
                printl("***ERROR NANOTUBE TOO SHORT FOR CONSTRUCTION! INCREASE U***")
        except:
            pass
        printl("nanotube cutoff",self.cutoff)    
    
    def calcInfo(self):
        printl("calculating nanotube info")
        try:
            self.radius,self.radius_std = self.calcAverageCapRadius(self.cappedTubeCarbonAtoms.npoints,self.cappedTubeCarbonAtoms.constrained_pos)
            printl("cap average radius",self.constrained_radius,"+-",self.constrained_radius_std)
        except:pass
        
        try:
            self.constrained_radius,self.constrained_radius_std = self.calcAverageCapRadius(self.cappedTubeCarbonAtoms.npoints,self.cappedTubeCarbonAtoms.constrained_pos)
            printl("cap constrained average radius",self.constrained_radius,"+-",self.constrained_radius_std)
        except:pass
        try:
            self.unconstrained_radius,self.unconstrained_radius_std = self.calcAverageCapRadius(self.cappedTubeCarbonAtoms.npoints,self.cappedTubeCarbonAtoms.unconstrained_pos)
            printl("cap unconstrained average radius",self.unconstrained_radius,"+-",self.unconstrained_radius_std)
        except:pass
    
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
    

    
    def getCapEstimates(self,n,m):
        printl("getting cap estimates")
        
        self.setup_params(n,m)
        
        Nc = self.NperU
        Nd = self.Nhex
        
        length = self.magT
        circumference = 2.0*math.pi*self.rad
        surfaceArea = circumference*length
        
        lengthScaled = length*self.scale
        circumferenceScaled = circumference*self.scale
        surfaceAreaScaled = lengthScaled*circumferenceScaled
        
        self.tubeDualLatticeDensity = float(self.Nhex)/surfaceAreaScaled
        self.tubeCarbonAtomDensity = float(Nc)/surfaceAreaScaled
        
        self.capThomsonPointEstimate = int(math.ceil(self.tubeDualLatticeDensity*2.0*math.pi))
        self.capCarbonAtomEstimate = int(math.ceil(self.tubeCarbonAtomDensity*2.0*math.pi))
        
        #based on C60
        
        dualRho  = 0.22
        
        self.capThomsonPointEstimate  = int(math.ceil(dualRho*(4.0*math.pi*self.rad*self.rad)/2.0))
        self.capCarbonAtomEstimate = 2*self.capThomsonPointEstimate- 2

        printl("nanotube dual lattice density",self.tubeDualLatticeDensity,self.rad,dualRho*(4.0*math.pi*self.rad*self.rad),
               "npoints in cap estimate",self.capThomsonPointEstimate)
        
    
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
        distToMid = self.tubeIntersectPoints2D.pos[2::3] - self.tubeThomsonPointsCOM[2]
        #printl("distToMid",distToMid)
        axespoint = numpy.argmin(numpy.abs(distToMid))
        '''
        find the x-position of this point which corresponds to angle around circumference.
        '''
        offset = self.tubeIntersectPoints2D.pos[0::3][axespoint]
        angletox = -1*(offset/(magnitude(self.Ch)*self.scale))*2.0*math.pi
        
        printl("angle to x found via intersection points",angletox,"axespoint",axespoint,"bisection:",
               self.tubeIntersectPoints2D.pos[2::3][axespoint]-self.tubeThomsonPointsCOM[2])
        
        self.rotationAngle = angletox
    
    def rotate(self):
        cr = math.cos(self.rotationAngle)
        sr = math.sin(self.rotationAngle)
#
        self.tubeCarbonAtoms.pos[0::3] -= self.tubeCarbonAtomsCOM[0]
        self.tubeCarbonAtoms.pos[1::3] -= self.tubeCarbonAtomsCOM[1]
        self.tubeCarbonAtoms.pos[2::3] -= self.tubeCarbonAtomsCOM[2]

        xc = self.tubeCarbonAtoms.pos[0::3]*cr
        xs = self.tubeCarbonAtoms.pos[0::3]*sr
        yc = self.tubeCarbonAtoms.pos[1::3]*cr
        ys = self.tubeCarbonAtoms.pos[1::3]*sr
        self.tubeCarbonAtoms.pos[0::3] = xc - ys
        self.tubeCarbonAtoms.pos[1::3] = xs + yc
#        
#        print self.tubeCarbonAtoms.pos[0]
#     
        self.tubeCarbonAtoms.pos[0::3] += self.tubeCarbonAtomsCOM[0]
        self.tubeCarbonAtoms.pos[1::3] += self.tubeCarbonAtomsCOM[1]
        self.tubeCarbonAtoms.pos[2::3] += self.tubeCarbonAtomsCOM[2]
#        
        
        self.tubeThomsonPoints.pos[0::3] -= self.tubeThomsonPointsCOM[0]
        self.tubeThomsonPoints.pos[1::3] -= self.tubeThomsonPointsCOM[1]
        self.tubeThomsonPoints.pos[2::3] -= self.tubeThomsonPointsCOM[2]
        
        xc = self.tubeThomsonPoints.pos[0::3]*cr
        xs = self.tubeThomsonPoints.pos[0::3]*sr
        yc = self.tubeThomsonPoints.pos[1::3]*cr
        ys = self.tubeThomsonPoints.pos[1::3]*sr
        self.tubeThomsonPoints.pos[0::3] = xc - ys
        self.tubeThomsonPoints.pos[1::3] = xs + yc
#        
#        print self.tubeCarbonAtoms.pos[0]
#     
        self.tubeThomsonPoints.pos[0::3] += self.tubeThomsonPointsCOM[0]
        self.tubeThomsonPoints.pos[1::3] += self.tubeThomsonPointsCOM[1]
        self.tubeThomsonPoints.pos[2::3] += self.tubeThomsonPointsCOM[2]
    
    
    def checkMappingAngle(self,deltheta=0.0001):
        '''        
        soo atm the nanotube has been rotated such that the 1,0,0 axis is inline with the bisected C-C bond (also Hex-Hex bond) at the midz point
        This means we can return MappingAngle = 0!, but for now this will act as a check for 0 mapping angle (it will return quickly if correct)
        
        '''
        self.mappingAngle = 0.0
        
        atoms = points.Points("")
        atoms.initArrays(self.tubeThomsonPoints.npoints)
        atoms.pos = numpy.copy(self.tubeThomsonPoints.pos)
        atomsCOM = self.tubeThomsonPointsCOM
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
                                                   ctypes.c_int(self.tubeThomsonPoints.npoints),
                                                   self.tubeThomsonPoints.pos.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
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
        
        self.tubeCarbonAtoms = points.Points("Nanotube Carbon Atoms")  
        self.tubeCarbonAtoms.initArrays(self.Nc)
        self.tubeCarbonAtomsCOM = numpy.zeros(3,NPF)
        
        self.tubeThomsonPoints.initArrays(self.Nd)
        self.tubeThomsonPoints.freeflags = numpy.zeros(self.tubeThomsonPoints.npoints,NPI)
        self.tubeThomsonPoints.freeflagspos = numpy.zeros(self.tubeThomsonPoints.npoints*3,NPF)
        self.tubeThomsonPoints.dampflags = numpy.zeros(self.tubeThomsonPoints.npoints,NPI)
        self.tubeThomsonPoints.dampflagspos = numpy.zeros(self.tubeThomsonPoints.npoints*3,NPF)
        self.tubeThomsonPoints.realflags = numpy.ones(self.tubeThomsonPoints.npoints,NPI)
        self.tubeThomsonPoints.realflagspos = numpy.ones(self.tubeThomsonPoints.npoints*3,NPF)
        self.tubeThomsonPointsCOM=numpy.zeros(3,NPF)
        
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
#                    self.tubeCarbonAtoms.pos[atomcount*3] = x
#                    self.tubeCarbonAtoms.pos[atomcount*3+1] = y 
#                    self.tubeCarbonAtoms.pos[atomcount*3+2] = z
#                    atomcount+=1 
#                for key in ["D",]:
#                    x,y,z = self.get_unit_cell_xyz(i,key)
#                    z+=float(u)*self.magT
#                    #printl("check z, 0, boundary",z,boundary-1e-12)
#                    if(z<1e-6):z+=boundary
#                    if(z > (boundary-1e-6)):z-=boundary
#                    self.tubeThomsonPoints.pos[dualcount*3] = x
#                    self.tubeThomsonPoints.pos[dualcount*3+1] = y 
#                    self.tubeThomsonPoints.pos[dualcount*3+2] = z
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
        clib.build_nanotube(ctypes.c_int(self.tubeThomsonPoints.npoints),
                            self.tubeThomsonPoints.pos.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                            ctypes.c_int(self.tubeCarbonAtoms.npoints),
                            self.tubeCarbonAtoms.pos.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
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
        self.tubeCarbonAtoms.pos*=self.scale 
        self.tubeThomsonPoints.pos*=self.scale 
        self.tubeIntersectPoints2D.pos*=self.scale     
        
        minZ = numpy.min(self.tubeThomsonPoints.pos[2::3])
        printh("minZ",minZ)
        printh("boundary",boundary)
        self.tubeThomsonPoints.pos[2::3]-= minZ
        self.tubeCarbonAtoms.pos[2::3]-= minZ
        self.tubeIntersectPoints2D.pos[2::3]-= minZ
        
        zremove = numpy.where(self.tubeThomsonPoints.pos[2::3]>self.length*self.scale)[0]
        self.tubeThomsonPoints.removeIndexes(zremove)
        zremove = numpy.where(self.tubeCarbonAtoms.pos[2::3]>self.length*self.scale)[0]
        self.tubeCarbonAtoms.removeIndexes(zremove)
        zremove = numpy.where(self.tubeIntersectPoints2D.pos[2::3]>self.length*self.scale)[0]
        self.tubeIntersectPoints2D.removeIndexes(zremove)
        
        printl("removed cutoff")   
        
        if(self.damping):
            for i in range(0,self.tubeThomsonPoints.npoints):
                if(self.tubeThomsonPoints.pos[i*3+2]<self.dampedlength):
                    self.tubeThomsonPoints.freeflags[i] = 1.0
                    self.tubeThomsonPoints.freeflagspos[i*3] = 1.0
                    self.tubeThomsonPoints.freeflagspos[i*3+1] = 1.0
                    self.tubeThomsonPoints.freeflagspos[i*3+2] = 1.0 
                    self.tubeThomsonPoints.dampflags[i] = 1.0
                    self.tubeThomsonPoints.dampflagspos[i*3] = 1.0
                    self.tubeThomsonPoints.dampflagspos[i*3+1] = 1.0
                    self.tubeThomsonPoints.dampflagspos[i*3+2] = 1.0
                
        self.tubeThomsonPointsCOM = numpy.array([0.0,0.0,
                                                 (numpy.sum(self.tubeThomsonPoints.pos[2::3]))/self.tubeThomsonPoints.npoints])
        self.tubeCarbonAtomsCOM = numpy.array([0.0,0.0,
                                               (numpy.sum(self.tubeCarbonAtoms.pos[2::3]))/self.tubeCarbonAtoms.npoints])
        
        printl("self.tubeThomsonPointsCOM",self.tubeThomsonPointsCOM)
        
        self.tubeThomsonPoints.pos0 = numpy.copy(self.tubeThomsonPoints.pos)   
        
        self.calc_rotation_angle()
        
        self.rotate()
        
        '''this should be zero if we have found the correct rotation axes'''
        self.checkMappingAngle()
        
        self.Nc = self.tubeCarbonAtoms.npoints
        self.Nd = self.tubeThomsonPoints.npoints
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

