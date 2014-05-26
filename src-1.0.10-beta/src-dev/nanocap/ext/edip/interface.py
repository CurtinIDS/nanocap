'''
Created on Aug 15, 2013

@author: Marc Robinson
'''

import ctypes,sys,numpy,os,inspect
from nanocap.core.globals import *
from nanocap.core.util import *


if(PLATFORM=="win"):lib="edip.dll"
else:  lib="edip.so"
    
#relative_lib = os.path.join(os.path.dirname(get_relative_path(__file__)),lib)    
    
#if(PLATFORM == "win"):path_relative_to_exe = "/ext/edip"
#elif(PLATFORM == "osx"):path_relative_to_exe = "/../Resources/ext/edip"
#else:path_relative_to_exe = ""

#print path_from_file(__file__,path_relative_to_exe)+"/"+lib

relative_lib = os.path.join(get_root(),"ext","edip","lib",lib)

print "relative_lib",relative_lib
edip = ctypes.cdll.LoadLibrary(relative_lib) 

parameters={}
parameters["gamma"] = 1.35419222406125
parameters["xlam"] = 66.5
parameters["xmu"] = 0.30
parameters["zrep"] = 0.06
parameters["zrep2"] = 0.06
parameters["flow"] = 1.48
parameters["fhigh"] = 2.0
parameters["falpha"] = 1.544
parameters["zlow"] = 1.547
parameters["zhigh"] = 2.270
parameters["zalpha"] = 1.544
parameters["bondcutoff"] = 1.85
parameters["flow"] = 1.48
parameters["norings"] = 0

def setup_parameters():
    edip.defaults()
    edip.parse.argtypes = [ctypes.c_char_p,
                                  ctypes.c_char_p,
                                  ctypes.POINTER(ctypes.c_bool),
                                  ctypes.c_int,ctypes.c_int]
    
    for p,v in parameters.items():
        edip.parse(ctypes.c_char_p(str(p)),
                   ctypes.c_char_p(str(v)),
                   ctypes.byref(ctypes.c_bool(False)),
                   ctypes.c_int(len(str(p))),ctypes.c_int(len(str(v))))
        

def get_energy_force(natoms,box,pos):  
    
    setup_parameters()      
    edip.passcoords.argtypes = [ctypes.POINTER(ctypes.c_int),
                                ctypes.POINTER(ctypes.c_double),
                                ctypes.POINTER(ctypes.c_double),
                                ctypes.POINTER(ctypes.c_double),
                                ctypes.POINTER(ctypes.c_int),
                                ctypes.POINTER(ctypes.c_double)]


    #print "passing coords",pos
        
    force = numpy.zeros(len(pos),dtype=NPF)
    #force.
    #printl(len(pos))
    edip.passcoords(ctypes.byref(ctypes.c_int(natoms)),
                    ctypes.byref(ctypes.c_double(float(box[0]))),
                    ctypes.byref(ctypes.c_double(box[1])),
                    ctypes.byref(ctypes.c_double(box[2])),
                    ctypes.byref(ctypes.c_int(len(pos))),
                    pos.ctypes.data_as(ctypes.POINTER(ctypes.c_double)))
#        
#        #edip.readmasses()
#        #edip.nabor()
    edip.volume()
    edip.neighbour()
    edip.force()
#        
#        force = numpy.zeros(len(pos),dtype=NPF)
#        energytotal = numpy.zeros(1,dtype=NPF)
#        
    #print "getforce"
    edip.getforce.argtypes = [ctypes.POINTER(ctypes.c_int),
                              ctypes.POINTER(ctypes.c_double),
                              ctypes.POINTER(ctypes.c_double)]      
    
    
     
    energy = ctypes.c_double()
    edip.getforce(ctypes.byref(ctypes.c_int(len(pos))),
                  force.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                  ctypes.byref(energy))    
    energy = float(energy.value)
    
#    #printl("force 0",force[0],force[1],force[2])
#    #printl("force 1",force[3],force[4],force[5])
#    na = (len(pos)/3)-2
#    printl("force",na,force[na*3],force[na*3+1],force[na*3+2])
#    na+=1
#    printl("force",na,force[na*3],force[na*3+1],force[na*3+2])
    #printl("energy",energy)
    
    return energy,force


def check_numerical_forces(natoms,box,pos,h=0.001):
    HVec = h*normalise(randvec(pos))
       
    forwardPos = numpy.copy(pos) + HVec
    backPos = numpy.copy(pos) - HVec
    
    forwardEnergy,force = get_energy_force(natoms,box,forwardPos)
    backEnergy,force =  get_energy_force(natoms,box,backPos)
    energy,force = get_energy_force(natoms,box,pos)
    
    numerical = -1.0*(forwardEnergy-backEnergy)/(2.0*h)        
    
    analytical = numpy.dot(force, normalise(HVec))
    error = numerical - analytical
    ratio = analytical/numerical
    perc = abs(1.0-ratio)*100.0
    print "checking numerical",numerical,"analytical",analytical,"forces error", error,"ratio", ratio,"%",perc,forwardEnergy,backEnergy,energy
    #print normalise(randvec(pos))
    return ratio

def test():
    box = numpy.array([1000,1000,1000],NPF)
    '''
    quick graphene lattice
    '''
    iunits,junits = 3,3
    natoms = iunits*junits*2
    pos = numpy.zeros(natoms*3,NPF)
    acc = 1.421
    z = 1.0
    a1,a2 = acc*numpy.array([math.sqrt(3),0]),acc*numpy.array([-math.sqrt(3)/2,3.0/2.0]),
        
    c = 0
    for i in range(0,iunits):
        for j in range(0,junits):
            p = i*a1 + j*a2
            #print p
            if(p[0]<0):
                p[0]+= math.sqrt(3)*acc*iunits
                
            pos[c*3],pos[c*3+1],pos[c*3+2] = p[0],p[1],z
            c+=1
            pos[c*3],pos[c*3+1],pos[c*3+2] = p[0],p[1] + acc,z
            c+=1

    error = []
    for i in range(0,1):            
        e = check_numerical_forces(natoms,box,pos,h=0.1)
        error.append(e)
    
    return error
if __name__=="__main__":

    test()



