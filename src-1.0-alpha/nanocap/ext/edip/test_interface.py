
import numpy
import time
import random
import math
import ctypes
from nanocap.core.globals import *
from nanocap.core.util import *
edip = ctypes.cdll.LoadLibrary(ROOTDIR+"/ext/edip/edip.so") 
#print edip_interface.__doc__


def get_force_edip(natoms,box,pos):
    start= time.time()
    edip.defaults()
    #pass positions only
    #edip_interface.parse("ntakof=","0",True)
    edip.parse("norings","0",True)
    print "passing coords",pos
    edip.passcoords(natoms,box[0],box[1],box[2],pos)
    
    edip.volume()
    edip.neighbour()
    edip.force()
    
    force = numpy.zeros(natoms*3,dtype=numpy.float64)
    energytotal = numpy.zeros(1,dtype=numpy.float64)
    
    edip.getforce(force,energytotal)
    
    print "force",force,"mag",magnitude(force),"energy",energytotal[0]
    
    print "edip force call time",time.time()-start,"seconds"
    
    return force,energytotal[0]

def check_numerical_forces(natoms,box,pos,h=0.001):
    HVec = h*normalise(randvec(pos))
       
    forwardPos = numpy.copy(pos) + HVec
    backPos = numpy.copy(pos) - HVec
    
    force,forwardEnergy = get_force_edip(natoms,box,forwardPos)
    force,backEnergy =  get_force_edip(natoms,box,backPos)
    force,energy = get_force_edip(natoms,box,pos)
    
    numerical = -1.0*(forwardEnergy-backEnergy)/(2.0*h)        
    
    analytical = numpy.dot(force, normalise(HVec))
    error = numerical - analytical
    ratio = analytical/numerical
    print "checking numerical",numerical,"analytical",analytical,"forces error", error,"ratio", ratio,forwardEnergy,backEnergy,energy

def randvec(v):
    numpy.random.seed(int(time.time()))
    vtemp = numpy.random.randn(v.size)
    return vtemp.reshape(v.shape)

def normalise(vec):
    vec = vec/magnitude(vec)
    return vec

def magnitude(vector):
    mag = math.sqrt(numpy.dot(vector,vector))    
    return mag  
    
def main():

    
    '''
    #can call any subroutine in edip like this:
    edip.printtime(1)
    edip.defaults()
    #set parameters like this:
    edip.parse("bondcutoff=","1.85",True)
    #edip.edip_force_call()
    #print edip.bondcutoff
    '''

    natoms = 100
    dim = 10
    pos = numpy.zeros(natoms*3,dtype=numpy.float64)
    box = numpy.array([dim,dim,dim],dtype=numpy.float64)
    #force = numpy.zeros(natoms*3+10,dtype=numpy.float64)
    for i in range(0,natoms):
        pos[i*3] = random.random()*dim
        pos[i*3+1] = random.random()*dim
        pos[i*3+2] = random.random()*dim
    
    get_force_edip(natoms,box,pos)
    
    check_numerical_forces(natoms,box,pos)

    return    
        

if __name__=="__main__":
    main()