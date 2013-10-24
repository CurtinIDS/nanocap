'''
Created on Oct 15, 2013

@author: Marc Robinson
'''
import unittest,os,sys

from nanocap.core.util import *
from nanocap.core.globals import *
from nanocap.core import globals
from nanocap.core import processes
from nanocap.core import config
from nanocap.objects import tube

class TestBatchJobs(unittest.TestCase): 
    
    def testNanotubeGenAndSaveCarbonMinimise(self):
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
        
        self.processor.resetNanotube(16,12,l=None,capEstimate=True)
        
        seed = 12345
        
        self.processor.resetCap(seed)
        
        self.processor.minimaSearch()
        
        for i in range(self.processor.minsearch.NUnique):
        
            self.processor.selectStructure(i,
                                           carbonMinimised=True,carbonConstrained=True)
            
            self.processor.saveCurrentStructure(os.getcwd(),
                                                update=True,
                                                dualLattice=True,
                                                carbonAtoms=True,
                                                carbonEnergy=True)


if __name__ == "__main__":
    
    unittest.main()  