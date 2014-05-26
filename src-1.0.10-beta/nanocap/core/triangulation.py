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
from nanocap.clib import clib_interface
clib = clib_interface.clib


def triangulationVolume(points):
    maxTriangles = points.npoints*50
    triangles = numpy.zeros(maxTriangles*3,NPF)
    
    AvBondLength = numpy.zeros(points.npoints,NPF)
    clib.get_average_bond_length(ctypes.c_int(points.npoints),
                                 points.pos.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                                 AvBondLength.ctypes.data_as(ctypes.POINTER(ctypes.c_double)))
               
    printl(points.PointSetLabel,"Average point NN distance",numpy.average(AvBondLength))
    
    vertlist = numpy.zeros(maxTriangles*3*3,NPI)
    outcenters = numpy.zeros(maxTriangles*3,NPF)
    
    AvBondLength*=4.0
    
    clib.triangulate.restype = ctypes.c_int
    ntriangles = clib.triangulate(ctypes.c_int(points.npoints),
                     points.pos.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                     vertlist.ctypes.data_as(ctypes.POINTER(ctypes.c_int)),
                     outcenters.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                     AvBondLength.ctypes.data_as(ctypes.POINTER(ctypes.c_double)))
    
    clib.calc_volume_using_div_thereom.restype = None
    
    out = numpy.zeros(2,NPF)
    clib.calc_volume_using_div_thereom(ctypes.c_int(ntriangles),
                                       vertlist.ctypes.data_as(ctypes.POINTER(ctypes.c_int)),
                                       points.pos.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                                       out.ctypes.data_as(ctypes.POINTER(ctypes.c_double)))
    
    SA,V = out[0],out[1]
    #print "surface area",SA,"vol",V
    
    return vertlist,ntriangles,SA,V
    
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
    
    printd("ntriangles",ntriangles)
    
    vertlist = vertlist[0:ntriangles*3]
    return vertlist,ntriangles