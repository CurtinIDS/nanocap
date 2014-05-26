'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: May 11, 2014
Copyright Marc Robinson  2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

Input routines


-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
'''

from nanocap.core import points

def read_xyz(filename):
    p = points.Points("")
    
    f = open(filename,"r")
    n = int(str(f.readline().split()[0]))
    p.initArrays(n)
    f.readline()
    
    for i in range(0,n):
        symb,x,y,z = f.readline().split()
        p.pos[i*3] = float(x)
        p.pos[i*3+1] = float(y)
        p.pos[i*3+2] = float(z)
        
    
    return p

funcs ={}
funcs['xyz']=read_xyz

def read_points(filename,format):
    points = funcs[format](filename)
    return points