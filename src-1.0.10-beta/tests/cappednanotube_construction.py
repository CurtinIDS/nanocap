'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Apr 22, 2014
Copyright Marc Robinson  2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

test construction of a cappednanotube 
from chirality and length.

Show in VTK window


-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
'''

import unittest,sys,os
if __name__ == "__main__":sys.path.append(os.path.abspath(__file__+"/../"))
print sys.path
from nanocap.core.util import *
from nanocap.core.globals import *
import nanocap.core.globals as globals
import nanocap.structures.nanotube as nanotube
from nanocap.structures import cappednanotube
import nanocap.core.points as points
from nanocap.core import minimisation,triangulation

from nanocap.clib import clib_interface
clib = clib_interface.clib

class CheckCappedNanotube(unittest.TestCase): 
    def test_construct_capped_nanotube(self):
        
        n,m = 10,10
        l = 20.0 
        capEstimate = True
             
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
        
        if(capEstimate):
            NCapDual = my_nanotube.get_cap_dual_lattice_estimate(n,m)
                
        my_nanotube.construct_dual_lattice(N_cap_dual=NCapDual,seed=seed)
        my_nanotube.update_caps()
        
        my_nanotube.set_Z_cutoff(N_cap_dual=NCapDual)
        
        
        Dminimiser = minimisation.DualLatticeMinimiser(FFID=DualLatticeMinimiser,structure = my_nanotube)
        Dminimiser.minimise(my_nanotube.dual_lattice,
                            min_type=mintype,
                            ftol=DualLattice_mintol,
                            min_steps=DualLattice_minsteps)
        
        my_nanotube.update_caps()
        my_nanotube.construct_carbon_lattice()
        
        Cminimiser = minimisation.CarbonLatticeMinimiser(FFID=CarbonLatticeMinimiser,structure = my_nanotube)
        
        Cminimiser.minimise_scale(my_nanotube.carbon_lattice)
        Cminimiser.minimise(my_nanotube.carbon_lattice,
                            min_type=mintype,
                            ftol=CarbonLattice_mintol,
                            min_steps=CarbonLattice_minsteps)

        my_nanotube.render()
        

    
if __name__ == "__main__":
    unittest.main() 
        