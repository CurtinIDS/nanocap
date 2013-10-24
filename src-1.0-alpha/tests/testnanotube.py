'''
Created on Oct 14, 2013

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

class TestNanotube(unittest.TestCase): 
    def testNanotube(self):
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
        self.config.opts["CarbonMinimise"]=True
        self.config.opts["BasinClimb"]=True

        
        self.processor = processes.Processor(config = self.config)
            
        self.processor.resetNanotube(5,5)
        
        #self.processor.resetNanotube(16,12,None)
        
        #self.processor.resetNanotube(37,31,None)        
if __name__ == "__main__":
    unittest.main()  