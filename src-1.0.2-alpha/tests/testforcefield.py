'''
Created on Sep 20, 2013

@author: Marc Robinson
'''

import unittest,sys,os
if __name__ == "__main__":sys.path.append(os.path.abspath(__file__+"/../../"))
print sys.path
from nanocap.core.util import *
from nanocap.core.globals import *
import nanocap.core.globals as globals
from nanocap.core import minimisation
from nanocap.core import forcefield
import nanocap.objects.tube as tube
import nanocap.objects.cap as cap
import nanocap.objects.points as points
import nanocap.objects.fullerene as fullerene

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
        
        self.nanotube = tube.nanotube()
        self.nanotube.setup(5,5,5)
        self.cap = cap.cap()
        self.cap.setup(ncap,
                       seed=123456)

        self.points = points.joinPointSets((self.cap.thomsonPoints,self.nanotube.tubeThomsonPoints))
        
        self.nanotube.setZcutoff(ncap)
        
        self.force = numpy.zeros_like(self.points.pos)
        
        self.FF = forcefield.ThomsonForceField()
        
        self.FF.args[2] = self.nanotube.cutoff


        for i in range(0,10):
            self.FF.check_numerical_forces(self.points, 0.001)
            
            
            
        
if __name__ == "__main__":
    unittest.main()   