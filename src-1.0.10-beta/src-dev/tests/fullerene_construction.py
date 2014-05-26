'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Apr 25, 2014
Copyright Marc Robinson  2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-


test fullerene construction and 
render

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
'''


import unittest,sys,os
if __name__ == "__main__":sys.path.append(os.path.abspath(__file__+"/../"))
print sys.path
from nanocap.core.util import *
from nanocap.core.globals import *
import nanocap.core.globals as globals
import nanocap.structures.nanotube as nanotube
from nanocap.structures import fullerene
import nanocap.core.points as points
from nanocap.core import minimisation,triangulation

from nanocap.clib import clib_interface
clib = clib_interface.clib

class CheckFullerene(unittest.TestCase): 
    def test_fullerene(self):
        NCarbon = 200 
             
        DualLatticeMinimiser = "Thomson"
        CarbonLatticeMinimiser = "EDIP"
        DualLattice_mintol=1e-10
        DualLattice_minsteps=100
        CarbonLattice_mintol=1e-10
        CarbonLattice_minsteps=100
        mintype="LBFGS"
        seed = 12345
        
        my_fullerene = fullerene.Fullerene()
        my_fullerene.construct_dual_lattice(N_carbon=NCarbon,seed=seed)
        my_fullerene.set_fix_pole(False)
        my_fullerene.set_nfixed_to_equator(0)
        
        Dminimiser = minimisation.DualLatticeMinimiser(FFID=DualLatticeMinimiser,structure = my_fullerene)
        Dminimiser.minimise(my_fullerene.dual_lattice,
                            min_type=mintype,
                            ftol=DualLattice_mintol,
                            min_steps=DualLattice_minsteps)
        
       
        my_fullerene.construct_carbon_lattice()
        
        Cminimiser = minimisation.CarbonLatticeMinimiser(FFID=CarbonLatticeMinimiser,structure = my_fullerene)
        
        Cminimiser.minimise_scale(my_fullerene.carbon_lattice)
        Cminimiser.minimise(my_fullerene.carbon_lattice,
                            min_type=mintype,
                            ftol=CarbonLattice_mintol,
                            min_steps=CarbonLattice_minsteps)

        my_fullerene.render()
        
        
if __name__ == "__main__":
    unittest.main() 