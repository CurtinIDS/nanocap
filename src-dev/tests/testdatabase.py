'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: May 1, 2014
Copyright Marc Robinson  2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

Database Tests


-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
'''



import unittest,sys,os
if __name__ == "__main__":sys.path.append(os.path.abspath(__file__+"/../"))
print sys.path
from nanocap.core.util import *
from nanocap.core.globals import *
import nanocap.core.globals as globals
import nanocap.structures.nanotube as nanotube
from nanocap.structures import fullerene,cappednanotube
import nanocap.core.points as points
from nanocap.gui.settings import *
from nanocap.rendering import vtkqtrenderwidgets,pointset,renderwidgets
from nanocap.core import minimisation,triangulation
from nanocap.db import database

from nanocap.clib import clib_interface
clib = clib_interface.clib

class CheckFullerene(unittest.TestCase): 
    def test_construct_capped_nanotube(self):
        
        n,m = 12,12
        l = 10.0 
        capEstimate = True
             
        DualLatticeMinimiser = "Thomson"
        CarbonLatticeMinimiser = "EDIP"
        DualLattice_mintol=1e-10
        DualLattice_minsteps=100
        CarbonLattice_mintol=1e-10
        CarbonLattice_minsteps=100
        mintype="LBFGS"
        seed = 123456
        
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
        
        my_nanotube.calculate_rings()
        
        print my_nanotube
        
        my_db = database.Database()
        my_db.init()
        my_db.add_structure(my_nanotube,add_dual_lattice=True,add_carbon_lattice=True)
    
    def test_nanotube(self):
        
        n=6
        m=4
        l=5.0
        u=1
        p=True
        
        myNanotube = nanotube.Nanotube()
        myNanotube.construct_nanotube(n,m,length=l,units=u,periodic=p)
        
        myNanotube.calculate_rings()
        
        my_db = database.Database()
        my_db.add_structure(myNanotube,add_dual_lattice=True,add_carbon_lattice=True)
        
    def test_fullerene(self):
        
        NCarbon = 220 
        
        #for NCarbon in range(60,200):
             
        DualLatticeMinimiser = "Thomson"
        CarbonLatticeMinimiser = "EDIP"
        DualLattice_mintol=1e-12
        DualLattice_minsteps=100
        CarbonLattice_mintol=1e-12
        CarbonLattice_minsteps=100
        mintype="LBFGS"
        seed = 123456
        
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
        
        my_fullerene.calculate_rings()
        #my_fullerene.render()
        
        my_db = database.Database()
        my_db.add_structure(my_fullerene,add_dual_lattice=True,add_carbon_lattice=True)
        
        
        
if __name__ == "__main__":
    unittest.main() 