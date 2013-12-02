'''
Created on Sep 20, 2013

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

class MinimiserCheck(unittest.TestCase):
    def testNanotubeDualLatticeMinimisation(self):
        
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
        
        seed = 12345
        
        self.processor = processes.Processor(config = self.config)
        self.processor.resetNanotube(5,5,capEstimate=True)
        
        self.processor.resetCap(seed)
        
        self.processor.minimiseDualLattice()
            
    def testFullereneDualLatticeMinimisation(self):
        self.config = config.Config()
        self.config.setHomeDir(os.getcwd())
        self.config.setUser("Test")
        
        self.config.opts["GenType"]="Fullerene"
        self.config.opts["CalcCappedTubeCarbonAtoms"]=True
        self.config.opts["CalcCarbonRings"]=True
        self.config.opts["CalcCarbonBonds"]=True
        self.config.opts["CalcTriangulation"]=True     
        self.config.opts["CalcSchlegel"]=False     
        self.config.opts["NFullereneDualLatticePoints"] = 60
        
        seed = 12345
        
        self.processor = processes.Processor(config = self.config)
        self.processor.resetFullereneDualLattice(seed=seed)
               
        self.processor.minimiseDualLattice()
            



if __name__ == "__main__":
    unittest.main() 
