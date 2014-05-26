'''
-=-=-=-=-=-=-=-=-=-=-=-=-=NanoCap=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
Copyright Marc Robinson  2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

A script to construct a series of 
fullerenes

Input: 
    N_carbon = number of carbon atoms
                in the fullerene
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
    N_nanotubes = required number of structures 
    N_max_structures = maximum number of possible 
                        structures to search through
    basin_climb = True/False - climb out of 
                  minima  
    calc_rings = True/False - calculate rings for 
                  each structure
                   
Output:
    -A structure log in myStructures.out
    
    -xyz files containing the carbon lattices 
    
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
'''

import sys,os,random,numpy
from nanocap.core.minimisation import DualLatticeMinimiser, \
                                      CarbonLatticeMinimiser  
from nanocap.core.minimasearch import MinimaSearch
from nanocap.structures.fullerene import Fullerene
from nanocap.core.output import write_points

N_carbon = 200 
dual_lattice_minimiser = "Thomson"
carbon_lattice_minimiser = "EDIP"
seed = 12345

N_fullerenes = 5
N_max_structures = 20
basin_climb = True
calc_rings = True

dual_lattice_minimiser = "Thomson"
carbon_lattice_minimiser = "EDIP"
dual_lattice_mintol=1e-10
dual_lattice_minsteps=100
carbon_lattice_mintol=1e-10
carbon_lattice_minsteps=100
optimiser="LBFGS"
seed = 12345

my_fullerene = Fullerene()
my_fullerene.construct_dual_lattice(N_carbon=N_carbon,seed=seed)
my_fullerene.construct_carbon_lattice()
my_fullerene.set_fix_pole(False)
my_fullerene.set_nfixed_to_equator(0)

Dminimiser = DualLatticeMinimiser(FFID=dual_lattice_minimiser,
                                  structure = my_fullerene,
                                  min_type= "LBFGS",
                                  ftol = 1e-10,
                                  min_steps = 10)

Cminimiser = CarbonLatticeMinimiser(FFID=carbon_lattice_minimiser,
                                  structure = my_fullerene,
                                  min_type= "LBFGS",
                                  ftol = 1e-10,
                                  min_steps = 10)

Searcher = MinimaSearch(Dminimiser,
                         carbon_lattice_minimiser= Cminimiser,
                         basin_climb=basin_climb,
                         calc_rings=calc_rings)

Searcher.start_search(my_fullerene.dual_lattice,
                      N_fullerenes,
                      N_max_structures)

Searcher.continue_search(my_fullerene.dual_lattice,
                         N_fullerenes,
                         N_max_structures)

Searcher.structure_log.write_log(os.getcwd(),"myStructures.out")

for i,structure in enumerate(Searcher.structure_log.structures):
    outfilename = "C{}_carbon_atoms_{}"
    outfilename = outfilename.format(structure.carbon_lattice.npoints,i)
    write_points(outfilename,
                 structure.carbon_lattice,
                 "xyz")

