'''
Created on Oct 14, 2013

@author: Marc Robinson
'''
import unittest

from nanocap.core.util import *
from nanocap.core.globals import *
from nanocap.core import globals
from nanocap.structures import nanotube
from nanocap.clib import clib_interface
clib = clib_interface.clib


class TestNanotube(unittest.TestCase): 
    def testNanotube(self):
        n=6
        m=4
        l=5.0
        u=1
        p=True
        
        myNanotube = nanotube.Nanotube()
        myNanotube.construct_nanotube(n,m,length=l,units=u,periodic=p)

        
        print myNanotube
              
if __name__ == "__main__":
    unittest.main()  