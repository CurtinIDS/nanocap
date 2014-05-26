'''
Created on Sep 20, 2013

@author: Marc Robinson
'''

import unittest
import os,sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)+"/../"))
from nanocap.core.util import *
from nanocap.core.globals import *
from nanocap.core import minimisation,triangulation
from nanocap.structures import cappednanotube
from nanocap.core import output


class MinimiserCheck(unittest.TestCase):
    def testNanotubeDualLatticeMinimisation(self):
        n,m = 7,3
        l = 10.0 
        cap_estimate = True
             
        DualLatticeMinimiser = "Thomson"
        CarbonLatticeMinimiser = "EDIP"
        DualLattice_mintol=1e-10
        DualLattice_minsteps=100
        CarbonLattice_mintol=1e-10
        CarbonLattice_minsteps=100
        mintype="LBFGS"
        seed = 12345
        
        
        
        my_nanotube = cappednanotube.CappedNanotube()
        
        my_nanotube.setup_nanotube(n,m,l=l)
        
        if(cap_estimate):
            NCapDual = my_nanotube.get_cap_dual_lattice_estimate(n,m)
    
        my_nanotube.construct_dual_lattice(N_cap_dual=NCapDual,seed=seed)
        
        my_nanotube.set_Z_cutoff(N_cap_dual=NCapDual)
    
        output.write_xyz("n_{}_m_{}_l_{}_cap_{}_dual_lattice_initial.xyz".format(n,m,l,my_nanotube.cap.dual_lattice.npoints),my_nanotube.dual_lattice)
    
        
        Dminimiser = minimisation.DualLatticeMinimiser(FFID=DualLatticeMinimiser,structure = my_nanotube)
        Dminimiser.minimise(my_nanotube.dual_lattice,
                            min_type=mintype,
                            ftol=DualLattice_mintol,
                            min_steps=DualLattice_minsteps)
        
        my_nanotube.update_caps()
        output.write_xyz("n_{}_m_{}_l_{}_cap_{}_dual_lattice.xyz".format(n,m,l,my_nanotube.cap.dual_lattice.npoints),my_nanotube.dual_lattice)
        
        my_nanotube.construct_carbon_lattice()
        
        Cminimiser = minimisation.CarbonLatticeMinimiser(FFID=CarbonLatticeMinimiser,structure = my_nanotube)
        
        Cminimiser.minimise_scale(my_nanotube.carbon_lattice)
        Cminimiser.minimise(my_nanotube.carbon_lattice,
                            min_type=mintype,
                            ftol=CarbonLattice_mintol,
                            min_steps=CarbonLattice_minsteps)
            
        
            
    def xtestFullereneDualLatticeMinimisation(self):
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
