'''
Created on Sep 12, 2013

@author: Marc Robinson
'''

import unittest
from nanocap.core.util import *
from nanocap.core.globals import *
from nanocap.core import minimisation
import nanocap.objects.tube as tube
import nanocap.objects.cap as cap
import nanocap.objects.points as points
import nanocap.objects.fullerene as fullerene

print "ROOTDIR",ROOTDIR
clib = ctypes.cdll.LoadLibrary(ROOTDIR+"/clib/clib.so") 

class CheckGaussianEnergyAndForce(unittest.TestCase):  
    def testNanotubeAnalyticalForce(self):
        gwidth = 20.0
        gheight = 500.0 
        ntests = 5
        h = 0.05
        tol = h/100.0
        npoints = 100
        ncap = 32
        print "testing with","gwidth",gwidth,"gheight",gheight,"performing",ntests,"checks"
        
        faillog = []
        
        for i in range(0,ntests):
        
            self.nanotube = tube.nanotube()
            self.nanotube.setup(5,5,5)
            self.cap = cap.cap()
            self.reflectedCap = cap.cap()
            self.cap.setup(ncap,
                           seed=123456)
    
            self.points = points.joinPointSets((self.cap.thomsonPoints,self.nanotube.tubeThomsonPoints))
            
            
            self.force = numpy.zeros_like(self.points.pos)
            offset = randvec(self.points.pos)
            #print offset
            
            gpos = numpy.copy(self.points.pos)+offset*5.0
            #gpos+=0.001
            
            clib.do_gauss_force.restype = ctypes.c_double
            gaussenergy = clib.do_gauss_force(ctypes.c_int(self.points.npoints),
                                self.force.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                                self.points.pos.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                                gpos.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                                ctypes.c_double(gwidth),
                                ctypes.c_double(gheight))
    
            #print "genergy,force",gaussenergy,magnitude(self.force)
            
            
            HVec = h*normalise(randvec(self.points.pos))
            
            temp = numpy.zeros_like(self.points.pos)
            fpos = numpy.copy(self.points.pos)+HVec
            bpos = numpy.copy(self.points.pos)-HVec
    
            fenergy = clib.do_gauss_force(ctypes.c_int(self.points.npoints),
                                temp.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                                fpos.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                                gpos.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                                ctypes.c_double(gwidth),
                                ctypes.c_double(gheight))
            
            benergy = clib.do_gauss_force(ctypes.c_int(self.points.npoints),
                                temp.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                                bpos.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                                gpos.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                                ctypes.c_double(gwidth),
                                ctypes.c_double(gheight))
    
            
            numerical = -1*(fenergy-benergy)/(2.0*h)
            analytical = numpy.dot(self.force , normalise(HVec))
            error = numerical - analytical
            ratio = analytical/numerical
            print "NUMERICAL FORCE ", numerical," ANALYTICAL FORCE ",analytical, " ERROR ",error," RATIO ",ratio
            if(abs(1.0-ratio)>tol):
                faillog.append(1)

        self.assertNotIn(1, faillog, "Numerical Force Fail")
        
    def testFullereneAnalyticalForce(self):
        gwidth = 200.0
        gheight = 500.0 
        ntests = 10
        h = 0.01
        tol = h/100.0
        npoints = 100
        print "testing with","gwidth",gwidth,"gheight",gheight,"performing",ntests,"checks"
        
        faillog = []
        
        for i in range(0,ntests):
        
            self.points = points.Points("blah")
            self.points.initArrays(npoints)
            clib.setup_random_points_on_sphere(ctypes.c_int(self.points.npoints),
                                            ctypes.c_int(123456),
                                            ctypes.c_int(0),
                                            ctypes.c_double(1.0),
                                            self.points.pos.ctypes.data_as(ctypes.POINTER(ctypes.c_double)))
            self.force = numpy.zeros_like(self.points.pos)
    
            gpos = self.points.pos+randvec(self.points.pos)
    
            clib.do_gauss_force.restype = ctypes.c_double
            gaussenergy = clib.do_gauss_force(ctypes.c_int(self.points.npoints),
                                self.force.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                                self.points.pos.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                                gpos.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                                ctypes.c_double(gwidth),
                                ctypes.c_double(gheight))
    
            #print "genergy,force",gaussenergy,magnitude(self.force)
            
            
            HVec = h*normalise(randvec(self.points.pos))
            
            temp = numpy.zeros_like(self.points.pos)
            fpos = numpy.copy(self.points.pos)+HVec
            bpos = numpy.copy(self.points.pos)-HVec
    
            fenergy = clib.do_gauss_force(ctypes.c_int(self.points.npoints),
                                temp.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                                fpos.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                                gpos.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                                ctypes.c_double(gwidth),
                                ctypes.c_double(gheight))
            
            benergy = clib.do_gauss_force(ctypes.c_int(self.points.npoints),
                                temp.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                                bpos.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                                gpos.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                                ctypes.c_double(gwidth),
                                ctypes.c_double(gheight))
    
            
            numerical = -1*(fenergy-benergy)/(2.0*h)
            analytical = numpy.dot(self.force , normalise(HVec))
            error = numerical - analytical
            ratio = analytical/numerical
            print "NUMERICAL FORCE ", numerical," ANALYTICAL FORCE ",analytical, " ERROR ",error," RATIO ",ratio
            if(abs(1.0-ratio)>tol):
                faillog.append(1)

        self.assertNotIn(1, faillog, "Numerical Force Fail")


if __name__ == "__main__":
    unittest.main()   