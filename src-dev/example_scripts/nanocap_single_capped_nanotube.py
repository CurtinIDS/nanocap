'''
-=-=-=-=-=-=-=-=-=-=-=-=-=NanoCap=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
Copyright Marc Robinson  2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

A script to construct a capped
nanotube.

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
                   
Output:
    xyz files containing dual lattice
    and carbon lattice 
    
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
'''
import sys,os,random,numpy
from nanocap.core import minimisation
from nanocap.structures import cappednanotube
from nanocap.core import output

n,m = 7,3
l = 10.0 
cap_estimate = True
     
dual_force_field = "Thomson"
carbon_force_field = "EDIP"
dual_lattice_mintol=1e-10
dual_lattice_minsteps=100
carbon_lattice_mintol=1e-10
carbon_lattice_minsteps=100
optimiser="LBFGS"
seed = 12345

my_nanotube = cappednanotube.CappedNanotube()

my_nanotube.setup_nanotube(n,m,l=l)

if(cap_estimate):
    NCapDual = my_nanotube.get_cap_dual_lattice_estimate(n,m)

my_nanotube.construct_dual_lattice(N_cap_dual=NCapDual,seed=seed)

my_nanotube.set_Z_cutoff(N_cap_dual=NCapDual)

cap = my_nanotube.cap
outfilename = "n_{}_m_{}_l_{}_cap_{}_dual_lattice_init"
outfilename = outfilename.format(n,m,l,cap.dual_lattice.npoints)
output.write_xyz(outfilename,my_nanotube.dual_lattice)


Dminimiser = minimisation.DualLatticeMinimiser(FFID=dual_force_field,
                                               structure = my_nanotube)
Dminimiser.minimise(my_nanotube.dual_lattice,
                    min_type=optimiser,
                    ftol=dual_lattice_mintol,
                    min_steps=dual_lattice_minsteps)

my_nanotube.update_caps()
outfilename = "n_{}_m_{}_l_{}_cap_{}_dual_lattice"
outfilename = outfilename.format(n,m,l,cap.dual_lattice.npoints)
output.write_xyz(outfilename,my_nanotube.dual_lattice)

my_nanotube.construct_carbon_lattice()

Cminimiser = minimisation.CarbonLatticeMinimiser(FFID=carbon_force_field,
                                                 structure = my_nanotube)

Cminimiser.minimise_scale(my_nanotube.carbon_lattice)
Cminimiser.minimise(my_nanotube.carbon_lattice,
                    min_type=optimiser,
                    ftol=carbon_lattice_mintol,
                    min_steps=carbon_lattice_minsteps)

outfilename = "n_{}_m_{}_l_{}_cap_{}_carbon_atoms"
outfilename = outfilename.format(n,m,l,cap.dual_lattice.npoints)
output.write_xyz(outfilename,my_nanotube.carbon_lattice)
outfilename = "n_{}_m_{}_l_{}_cap_{}_carbon_atoms_constrained"
outfilename = outfilename.format(n,m,l,cap.dual_lattice.npoints)
output.write_xyz(outfilename,my_nanotube.carbon_lattice,constrained=True)

