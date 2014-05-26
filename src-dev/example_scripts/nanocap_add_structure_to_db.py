'''
-=-=-=-=-=-=-=-=-=-=-=-=-=NanoCap=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
Copyright Marc Robinson  2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

A script to construct and add a fullerene to the local database

Input: 
    N_carbon = Number of carbon atoms
    dual_lattice_force_field = force field 
                               for dual lattice
    carbon_force_field = force field 
                        for carbon lattice
    dual_lattice_mintol= energy tolerance for
                         dual lattice optimisation
    dual_lattice_minsteps= steps for dual lattice 
                            optimisation
    carbon_lattice_mintol=as above for carbon lattice
    carbon_lattice_minsteps=as above for carbon lattice
    optimiser=optimsation algorithm
    seed = seed for initial cap generation
                   
Output:
    structure is added to local database 
    
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
'''

import sys,os,random,numpy
from nanocap.core.minimisation import DualLatticeMinimiser, \
                                      CarbonLatticeMinimiser  
from nanocap.structures.fullerene import Fullerene
from nanocap.db.database import Database
from nanocap.core.output import write_xyz

N_carbon = 200 

dual_force_field = "Thomson"
carbon_force_field = "EDIP"
dual_lattice_mintol=1e-10
dual_lattice_minsteps=100
carbon_lattice_mintol=1e-10
carbon_lattice_minsteps=100
optimiser="LBFGS"
seed = 12345

my_fullerene = Fullerene()
my_fullerene.construct_dual_lattice(N_carbon=N_carbon,seed=seed)
my_fullerene.set_fix_pole(False)
my_fullerene.set_nfixed_to_equator(0)


Dminimiser = DualLatticeMinimiser(FFID=dual_force_field,
                                  structure = my_fullerene)
Dminimiser.minimise(my_fullerene.dual_lattice,
                    min_type=optimiser,
                    ftol=dual_lattice_mintol,
                    min_steps=dual_lattice_minsteps)

outfilename = "C{}_dual_lattice.xyz".format(N_carbon)
write_xyz(outfilename,my_fullerene.dual_lattice)

my_fullerene.construct_carbon_lattice()

Cminimiser = CarbonLatticeMinimiser(FFID=carbon_force_field,
                                    structure = my_fullerene)

Cminimiser.minimise_scale(my_fullerene.carbon_lattice)
Cminimiser.minimise(my_fullerene.carbon_lattice,
                    min_type=optimiser,
                    ftol=carbon_lattice_mintol,
                    min_steps=carbon_lattice_minsteps)


my_db = Database()
my_db.init()
my_db.add_structure(my_fullerene,
                    add_dual_lattice=True,
                    add_carbon_lattice=True)

       