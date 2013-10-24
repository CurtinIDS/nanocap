'''
Created on Sep 26, 2013

@author: Marc Robinson
'''
import unittest,copy

from nanocap.core.util import *
from nanocap.core.globals import *
from nanocap.core import globals
from nanocap.core import minimisation
from nanocap.core import processes
import nanocap.objects.tube as tube
import nanocap.objects.cap as cap
import nanocap.objects.points as points
import nanocap.objects.fullerene as fullerene
import nanocap.gui.forms as forms
import nanocap.gui.dock as dock

print "ROOTDIR",ROOTDIR
clib = ctypes.cdll.LoadLibrary(ROOTDIR+"/clib/clib.so") 

class TestPoints(unittest.TestCase):  
    def testCopy(self):
        
        self.p1 = points.Points("p1")
        self.p1.initArrays(100)
        self.p1.pos[0] = 11.0
        
        self.p2 = copy.deepcopy(self.p1)
        
        assert self.p2 is not self.p1
        assert self.p2.pos is not self.p1.pos
        print self.p2.pos[0],self.p1.pos[0]
        
        
        self.f1 = fullerene.fullerene()
        
        self.f2 = copy.deepcopy(self.f1)
        
        assert self.f1 is not self.f2
        assert self.f1.thomsonPoints is not self.f2.thomsonPoints
        
        
if __name__ == "__main__":
    unittest.main()  