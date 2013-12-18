'''
Created on Sep 24, 2013

@author: Marc Robinson
'''

import unittest,time

from nanocap.core.util import *
from nanocap.core.globals import *
from nanocap.core import globals
from nanocap.core import processes
from nanocap.core import config
from nanocap.objects import tube
from nanocap.clib import clib_interface
clib = clib_interface.clib

class TestNonGui(unittest.TestCase):  
    def testBasicFullereneOps(self):
        
        
        self.config = config.Config()
        self.config.setHomeDir(os.getcwd())
        self.config.setUser("Example")
            
        self.config.opts["GenType"]="Fullerene"
        self.config.opts["CalcCappedTubeCarbonAtoms"]=True
        self.config.opts["CalcCarbonRings"]=True
        self.config.opts["CalcCarbonBonds"]=True
        self.config.opts["CalcTriangulation"]=True     
        self.config.opts["CalcSchlegel"]=False     
        self.config.opts["NFullereneDualLatticePoints"] = 60
        self.config.opts["MinTol"]=1e-5
        self.config.opts["CarbonMinimise"]=True

        self.processor = processes.Processor(config = self.config)
        
        self.processor.resetFullereneDualLattice(seed  = 12345)
    
        self.processor.minimiseDualLattice()
        
        
        self.processor.minimiseCarbonAtoms()
        
        #self.processor.saveCurrentStructure()
        
        print self.processor.fullerene
        
        
    def xtestMinSearchFullereneVsTime(self):
        self.config = config.Config()
        self.config.opts["GenType"]="Fullerene"
        self.config.opts["CalcCappedTubeCarbonAtoms"]=True
        self.config.opts["CalcCarbonRings"]=True
        self.config.opts["CalcCarbonBonds"]=True
        self.config.opts["CalcTriangulation"]=True     
        self.config.opts["CalcSchlegel"]=False     
        
        self.config.opts["isNanotube"]=0
        self.config.opts["AutoNanotubeZCutoff"]=True
        self.config.opts["BasinClimb"]=True
        self.config.opts["MinTol"]=1e-5
        self.config.opts["AutoNanotubeZCutoff"]=True
        
        self.config.opts["NMinima"]=10
        self.processor = processes.Processor(config = self.config)
        
        f = open("FullereneTimeLog.txt","w")
        for t in range(100,1000,20):
            
            stime = time.time()
            self.config.opts["NFullereneDualLatticePoints"] = t
        
            
        
            self.processor.resetFullereneThomsonPoints(seed  = 12345)
        
        #globals.GaussianHeight = 2.0
        #globals.GaussianWidth = 2.0
        
            self.processor.minimaSearch()
            steptime = time.time()-stime
            f.write(("Nt %d Nc %d Nunique %d Time %lf\n") %
                    (self.processor.fullerene.thomsonPoints.npoints,
                    self.processor.fullerene.carbonAtoms.npoints,
                    self.processor.minsearch.NUnique,
                    steptime))
            self.processor.minsearch.reset()
            
            
    def xtestMinSearchFullereneOps(self):
        self.config = config.Config()
        self.config.opts["GenType"]="Fullerene"
        self.config.opts["CalcCappedTubeCarbonAtoms"]=True
        self.config.opts["CalcCarbonRings"]=True
        self.config.opts["CalcCarbonBonds"]=True
        self.config.opts["CalcTriangulation"]=True     
        self.config.opts["CalcSchlegel"]=False     
        
        self.config.opts["isNanotube"]=0
        self.config.opts["AutoNanotubeZCutoff"]=True
        self.config.opts["BasinClimb"]=True
        self.config.opts["MinTol"]=1e-5
        self.config.opts["AutoNanotubeZCutoff"]=True
        
        self.config.opts["NMinima"]=10
        
        
        self.config.opts["NFullereneDualLatticePoints"] = 100
        
        self.processor = processes.processor(config = self.config)
        
        self.processor.resetFullereneThomsonPoints(seed  = 12345)
        
        globals.GaussianHeight = 2.0
        globals.GaussianWidth = 2.0
        
        self.processor.minimaSearch()

    
    def xtestBasicNanotubeOps(self):
        
        self.config = config.Config()
        
        
        self.config.opts["GenType"]="Nanotube"
        self.config.opts["CalcCappedTubeCarbonAtoms"]=True
        self.config.opts["CalcCarbonRings"]=True
        self.config.opts["CalcCarbonBonds"]=True
        self.config.opts["CalcTriangulation"]=True     
        self.config.opts["CalcSchlegel"]=False     
        self.config.opts["NCapDualLatticePoints"] = 16
        self.config.opts["AutoNanotubeZCutoff"]=True
        
        #n,m = 16,12
        
        #from (N0,0) up to (N,0):
        
        self.nanotube = tube.nanotube()        
        self.nanotube.setup(35,14)
        
        
        
        N = 50
        N0 = 5
        
        #this produces all nanotubes from (N,0) to (N0,0) in decreasing radius
        angles = [] 
        for g in range(N,N0,-1):
            for n in range(g,0,-1):
                m = g-n
                if(m>n):break
                print n,m
        
        
                self.nanotube = tube.nanotube()        
                self.nanotube.setup(n,m)
                
                angles.append((n,m,self.nanotube.rotationAngle,self.nanotube.mappingAngle))
        for a in angles:
            if(a[3]>0.0001):print "****",        
            print a        
        
        #self.nanotube = tube.nanotubeOLD()        
        #self.nanotube.setup(n,m)
        
#        self.processor = processes.Processor(config = self.config)
#        
#        self.processor.resetNanotube(5,5)
#        self.processor.resetCap(12345)
#        
       
        #self.processor.minimiseDualLattice()
        #self.processor.minimiseCarbonAtoms()
    
    def xtestMinSearchNanotubeOps(self):
        self.config = config.Config()
        self.config.opts["GenType"]="Nanotube"
        self.config.opts["CalcCappedTubeCarbonAtoms"]=True
        self.config.opts["CalcCarbonRings"]=True
        self.config.opts["CalcCarbonBonds"]=True
        self.config.opts["CalcTriangulation"]=True     
        self.config.opts["CalcSchlegel"]=False     
        self.config.opts["NCapDualLatticePoints"] = 16
        self.config.opts["isNanotube"]=1
        self.config.opts["AutoNanotubeZCutoff"]=True
        self.config.opts["BasinClimb"]=True
        self.config.opts["MinTol"]=1e-5
        self.config.opts["AutoNanotubeZCutoff"]=True
        self.config.opts["NMinima"]=4
        
        
        self.processor = processes.processor(config = self.config)
        
        self.processor.resetNanotube(16,12)
        
        self.processor.resetCap(21036)
        
        self.processor.nanotube.cutoff = 1.0
        globals.GaussianHeight = 2.0
        globals.GaussianWidth = 2.0
        
        self.processor.minimaSearch()
                

        
        
        
if __name__ == "__main__":
    unittest.main()  