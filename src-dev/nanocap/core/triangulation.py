'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Sep 20 2013
Copyright Marc Robinson 2013
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=


routine to triangulate a give points class

returns: ntriangles, vertlist 

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
'''

from nanocap.core.globals import *
from nanocap.core.util import *
import nanocap.core.globals as globals
import os,sys,math,copy,random,time,threading,Queue,ctypes



def delaunyTriangulation(points):   
        
    maxTriangles = points.npoints*50
    triangles = numpy.zeros(maxTriangles*3,NPF)
    
    AvBondLength = numpy.zeros(points.npoints,NPF)
    clib.get_average_bond_length(ctypes.c_int(points.npoints),
                                 points.pos.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                                 AvBondLength.ctypes.data_as(ctypes.POINTER(ctypes.c_double)))
               
    printl(points.PointSetLabel,"Average point NN distance",numpy.average(AvBondLength))
    
    vertlist = numpy.zeros(maxTriangles*3*3,NPI)
    outcenters = numpy.zeros(maxTriangles*3,NPF)
    
    clib.triangulate.restype = ctypes.c_int
    ntriangles = clib.triangulate(ctypes.c_int(points.npoints),
                     points.pos.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                     vertlist.ctypes.data_as(ctypes.POINTER(ctypes.c_int)),
                     outcenters.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                     AvBondLength.ctypes.data_as(ctypes.POINTER(ctypes.c_double)))
    
    return vertlist,ntriangles