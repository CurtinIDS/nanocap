'''
Created on Sep 12, 2013

@author: Marc Robinson
'''
import unittest
from nanocap.core.util import *
from nanocap.core.globals import *
from nanocap.objects import points
from nanocap.ext.edip import interface

print "ROOTDIR",ROOTDIR
clib = ctypes.cdll.LoadLibrary(ROOTDIR+"/clib/clib.so") 

class CheckGaussianEnergyAndForce(unittest.TestCase):  
    def testEDIPInterface(self):

        tol = 1e-1
        errors = interface.test()
        faillog = []
        for e in errors: 
            #
            if(abs(1.0-e)>tol):
                print abs(1.0-e)
                faillog.append(1)

        self.assertNotIn(1, faillog, "Numerical Force Fail")

        
        
        
        
        
        
if __name__ == "__main__":
    unittest.main()   