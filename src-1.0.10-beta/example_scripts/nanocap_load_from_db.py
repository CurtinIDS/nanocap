'''
-=-=-=-=-=-=-=-=-=-=-=-=-=NanoCap=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
Created: May 23, 2014
Copyright Marc Robinson  2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

Example script showing how to load from a database. 
Simple example showing how to load fullerene dual lattice

Input: 
    type - the type of structure to return the dual
           for = "Fullerene","Capped Nanotube","Nanotube"
                   
Output:
    folders for each structure containing xyz files and
    info files.

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
'''
import sys,os
sys.path.append(os.path.abspath(os.path.dirname(__file__)+"/../"))
from nanocap.db.database import Database
from nanocap.core.output import write_xyz

type = "Fullerene"

my_db = Database()
my_db.init()

#let's query for all fullerene dual lattices

tables = ["dual_lattices"]
selects = ["id",]
checks  = { "dual_lattices" : ['type',] } 
data = {"dual_lattices" : {"type" : type}}
         
sql,data = my_db.construct_query(data,tables,selects,checks)  
results  = my_db.query(sql,data)
#out now contains dual lattice IDs of fullerenes 
print results

for result in results:
    id = result[0]
    structure = my_db.construct_structure(id)
    Nd = structure.dual_lattice.npoints
    folder = "Fullerene_dual_lattice_id_{}_N_{}".format(id,Nd)
    structure.export(  folder=".",
                       save_info=True,
                       save_image=False,
                       save_video=False,
                       save_carbon_lattice=False,
                       save_con_carbon_lattice=False,
                       info_file='structure_info.txt',
                       save_dual_lattice=True,
                       formats=['xyz',])
    