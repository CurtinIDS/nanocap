'''
Created on Oct 8, 2013

@author: Marc Robinson
'''
import unittest

from nanocap.core.util import *
from nanocap.core.globals import *
from nanocap.core import globals
from nanocap.core import processes
from nanocap.core import config

print "ROOTDIR",ROOTDIR
clib = ctypes.cdll.LoadLibrary(ROOTDIR+"/clib/clib.so") 

class TestNonGuiCapRange(unittest.TestCase):  
    def testCapRange(self):
        self.config = config.Config()
        self.config.setHomeDir(os.getcwd())
        self.config.setUser("Test")
        
        self.config.opts["GenType"]="Nanotube"
        self.config.opts["CalcCappedTubeCarbonAtoms"]=True
        self.config.opts["CalcCarbonRings"]=True
        self.config.opts["CalcCarbonBonds"]=True
        self.config.opts["CalcTriangulation"]=True     
        self.config.opts["CalcSchlegel"]=False     
        self.config.opts["NCapDualLatticePoints"] = 16
        self.config.opts["AutoNanotubeZCutoff"]=True
        self.config.opts["NMinima"]=3
        self.config.opts["CarbonMinimise"]=False
        self.config.opts["BasinClimb"]=True

        
        self.processor = processes.Processor(config = self.config)
        
        
        self.processor.resetNanotube(10,10,8)
        self.processor.resetCap(21036)
        
        estimate = self.processor.nanotube.capThomsonPointEstimate
        
        print "estimate",estimate
        time.sleep(0.5)
        
        for ncap in range(estimate-4,estimate+4):
            
            
            self.processor.resetNanotube(10,10,8,capEstimate=False)
            self.processor.resetCap(seed=21036,ncap_dual_lattice_points=ncap)

            self.processor.minimaSearch()
            
            self.processor.minsearch.reset()
        
        
if __name__ == "__main__":
    unittest.main()  