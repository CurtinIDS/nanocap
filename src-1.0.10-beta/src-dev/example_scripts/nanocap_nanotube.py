'''
-=-=-=-=-=-=-=-=-=-=-=-=-=NanoCap=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
Copyright Marc Robinson  2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

A script to construct an uncapped
nanotube.

Input: 
    n,m = Chirality (n,m)
    l = length
    u = number of unit cells
    p = periodic
Output:
    xyz file containing carbon
    lattice
    
if periodic, length is ignored and
unit cells is used
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
'''
from nanocap.structures import nanotube
from nanocap.core import output

n=6
m=4
l=5.0
u=1
p=True

my_nanotube = nanotube.Nanotube()
my_nanotube.construct(n,m,length=l,
                     units=u,periodic=p)

output.write_xyz("nanotube_carbon_lattice",
                 my_nanotube.carbon_lattice)