'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: July 22 2012
Copyright Marc Robinson 2013
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

Output routines

Currently:
XYZ

add a function and a key to 'funcs'
then write_points is called. 

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
'''

from nanocap.core.util import *
    
def write_xyz(filename,pointSet,constrained=False):
    if(constrained and len(pointSet.constrained_pos)==0):
        printe("pointset does not constrained positions")
        return
    f = open(filename+".xyz","w")
    f.write(str(pointSet.npoints)+"\n")
    f.write("\n")
    for i in range(0,pointSet.npoints):
        if not constrained:f.write("C "+str(pointSet.pos[i*3])+" "+str(pointSet.pos[i*3+1])+" "+str(pointSet.pos[i*3+2])+"\n")
        else:f.write("C "+str(pointSet.constrained_pos[i*3])+" "+str(pointSet.constrained_pos[i*3+1])+" "+str(pointSet.constrained_pos[i*3+2])+"\n")
    f.close()
    
    
funcs ={}
funcs['xyz']=write_xyz

def write_points(filename,pointSet,format,constrained=False):
    funcs[format](filename,pointSet,constrained=constrained)