'''
-=-=-=-=-=-=-=-=-=-=-=-=-=NanoCap=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
Copyright Marc Robinson  2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

A script to construct a series of capped
nanotubes of the same chirality

Input: 
    n,m = Chirality (n,m)
    l = length
    cap_estimate = estimate cap from
                   tube density
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
from nanocap.structures.cappednanotube import CappedNanotube
from nanocap.core.output import write_points

n,m = 10,10
l = 20.0 
cap_estimate = True

N_nanotubes = 5
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

my_nanotube = CappedNanotube()
my_nanotube.setup_nanotube(n,m,l=l)

if(cap_estimate):
    N_cap_dual = my_nanotube.get_cap_dual_lattice_estimate(n,m)

my_nanotube.construct_dual_lattice(N_cap_dual=N_cap_dual,seed=seed)
my_nanotube.set_Z_cutoff(N_cap_dual=N_cap_dual)

Dminimiser = DualLatticeMinimiser(FFID=dual_lattice_minimiser,
                                  structure = my_nanotube,
                                  min_type= optimiser,
                                  ftol = dual_lattice_mintol,
                                  min_steps = dual_lattice_minsteps)

Cminimiser = CarbonLatticeMinimiser(FFID=carbon_lattice_minimiser,
                                  structure = my_nanotube,
                                  min_type= optimiser,
                                  ftol = carbon_lattice_mintol,
                                  min_steps = carbon_lattice_minsteps)

Searcher = MinimaSearch(Dminimiser,
                        carbon_lattice_minimiser= Cminimiser,
                        basin_climb=basin_climb,
                        calc_rings=calc_rings)

Searcher.start_search(my_nanotube.dual_lattice,
                      N_nanotubes,
                      N_max_structures)

Searcher.structure_log.write_log(os.getcwd(),"myStructures.out")

for i,structure in enumerate(Searcher.structure_log.structures):
    carbon_lattice = structure.carbon_lattice
    filename = "C{}_carbon_atoms_{}".format(carbon_lattice.npoints,i)
    write_points(filename,carbon_lattice,format="xyz")



