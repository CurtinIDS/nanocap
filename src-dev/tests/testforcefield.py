'''
Created on Sep 20, 2013

@author: Marc Robinson
'''

import unittest,sys,os
if __name__ == "__main__":sys.path.append(os.path.abspath(__file__+"/../../"))
print sys.path
from nanocap.core.util import *
from nanocap.core.globals import *
from nanocap.core import minimisation
from nanocap.core import forcefield
import nanocap.structures.nanotube as nanotube
import nanocap.structures.cap as cap
import nanocap.structures.cappednanotube as cappednanotube 
import nanocap.core.points as points
import nanocap.structures.fullerene as fullerene

from nanocap.clib import clib_interface
clib = clib_interface.clib

class CheckForceField(unittest.TestCase):  
    def testSphereThomsonForceField(self):
        
        npoints= 100
        self.points = points.Points("test_points")
        self.points.initArrays(npoints)
        clib.setup_random_points_on_sphere(ctypes.c_int(self.points.npoints),
                                        ctypes.c_int(123456),
                                        ctypes.c_int(0),
                                        ctypes.c_double(1.0),
                                        self.points.pos.ctypes.data_as(ctypes.POINTER(ctypes.c_double)))
        self.force = numpy.zeros_like(self.points.pos)
        
        
        self.FF = forcefield.ThomsonForceField()

        for i in range(0,10):
            self.FF.check_numerical_forces(self.points, 0.001)

    def testNanotubeThomsonForceField(self):     
        ncap = 32
        n,m=5,5
        l=10.0
        capEstimate = True
        seed = 123654
        
        my_nanotube = cappednanotube.CappedNanotube()
        my_nanotube.setup_nanotube(n,m,l=l)
        
        if(capEstimate):
            NCapDual = my_nanotube.get_cap_dual_lattice_estimate(n,m)
    
        my_nanotube.construct_dual_lattice(N_cap_dual=NCapDual,seed=seed)
        
        my_nanotube.set_Z_cutoff(N_cap_dual=NCapDual)
        
        self.force = numpy.zeros_like(my_nanotube.dual_lattice.pos)
        
        self.FF = forcefield.ThomsonForceField()
        
        self.FF.args[2] = my_nanotube.cutoff


        for i in range(0,10):
            self.FF.check_numerical_forces(my_nanotube.dual_lattice, 0.001)
            
            
            
        
if __name__ == "__main__":
    unittest.main()   