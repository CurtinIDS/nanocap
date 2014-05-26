'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Dec 17, 2013
Copyright Marc Robinson 2013
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=


routine to calculate the rings of a 
given points class

returns: 

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
'''

from nanocap.core.globals import *
from nanocap.core.util import *
import os,sys,math,copy,random,time,threading,Queue,ctypes
from nanocap.clib import clib_interface
clib = clib_interface.clib


def calculate_volume_from_rings(pointSet,
                                nrings,
                                maxVerts,
                                rings,
                                vertsPerRingCount):
    
    out = numpy.zeros(2,NPF)
    
    clib.calc_volume_from_rings_using_div_thereom.restype = None
    clib.calc_volume_from_rings_using_div_thereom(ctypes.c_int(nrings),
                                                 ctypes.c_int(maxVerts),
                                                 rings.ctypes.data_as(ctypes.POINTER(ctypes.c_int)),
                                                 vertsPerRingCount.ctypes.data_as(ctypes.POINTER(ctypes.c_int)),
                                                 pointSet.pos.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                                                 out.ctypes.data_as(ctypes.POINTER(ctypes.c_double)))
    
    return out[0],out[1]
    

def calculate_rings(pointSet,MaxNebs=3,MaxVerts=9):
    
    stime = time.time()
    if(pointSet.npoints==0):
        outdict = {}
        outdict['percHex'] = 0
        outdict['isolatedPentagons'] = 0
        outdict['ringCount'] = 0
        outdict['VertsPerRingCount'] = 0
        outdict['ringdict'] = 0
        outdict['RingsPerVertCount'] = 0
        outdict['Rings'] = 0
        outdict['nrings'] = 0
        outdict['MaxVerts'] = 0
        return outdict
    
    NebList = numpy.zeros(pointSet.npoints*MaxNebs,NPI)
    NebDist = numpy.zeros(pointSet.npoints*MaxNebs,NPF)
    NebCount = numpy.zeros(pointSet.npoints,NPI)
    NebCount[:]=MaxNebs
    AvBondLength = numpy.zeros(pointSet.npoints,NPF)
    
    clib.get_average_bond_length(ctypes.c_int(pointSet.npoints),
                                 pointSet.pos.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                                 AvBondLength.ctypes.data_as(ctypes.POINTER(ctypes.c_double)))
    
    clib.calc_carbon_carbon_neb_list.restype = None
    clib.calc_carbon_carbon_neb_list(ctypes.c_int(pointSet.npoints),
                                     pointSet.pos.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),       
                                     NebList.ctypes.data_as(ctypes.POINTER(ctypes.c_int)),
                                     NebDist.ctypes.data_as(ctypes.POINTER(ctypes.c_int)))
    
    cutoff = numpy.average(AvBondLength)*1.2
    cullindexes = numpy.where(NebDist>cutoff*cutoff)[0]
    cullindexes = numpy.array(numpy.floor(cullindexes/3),NPI)
    NebCount[cullindexes] = 2
    
    printd("NebList",NebList)
    
    MaxRings = int(pointSet.npoints*2.0)
    Rings = numpy.zeros(MaxRings*MaxVerts,NPI)
    #how many verts per ring
    VertsPerRingCount = numpy.zeros(MaxRings,NPI)
    #how many rings per vert
    RingsPerVertCount = numpy.zeros(pointSet.npoints,NPI)
    
    nedges = len(NebList)
    
    clib.calculate_rings.restype = ctypes.c_int
    nrings = clib.calculate_rings(ctypes.c_int(pointSet.npoints),
                                     ctypes.c_int(nedges),
                                     NebList.ctypes.data_as(ctypes.POINTER(ctypes.c_int)),
                                     NebCount.ctypes.data_as(ctypes.POINTER(ctypes.c_int)),
                                     ctypes.c_int(MaxNebs),
                                     Rings.ctypes.data_as(ctypes.POINTER(ctypes.c_int)),
                                     VertsPerRingCount.ctypes.data_as(ctypes.POINTER(ctypes.c_int)),
                                     RingsPerVertCount.ctypes.data_as(ctypes.POINTER(ctypes.c_int)),
                                     ctypes.c_int(MaxVerts),
                                     pointSet.pos.ctypes.data_as(ctypes.POINTER(ctypes.c_double)))
    
    printl("nrings",nrings)
    if(nrings==0):
        outdict = {}
        outdict['percHex'] = 0
        outdict['isolatedPentagons'] = 0
        outdict['ringCount'] = 0
        outdict['VertsPerRingCount'] = 0
        outdict['ringdict'] = 0
        outdict['RingsPerVertCount'] = 0
        outdict['Rings'] = 0
        outdict['nrings'] = 0
        outdict['MaxVerts'] = 0
        return outdict
    
    VertsPerRingCount = VertsPerRingCount[0:nrings]
    ringdict = count_entries(VertsPerRingCount)
    printl(nrings,MaxRings,ringdict)
    
    ringCount = numpy.zeros(MaxVerts,NPI)
    ringCountDict = count_entries(VertsPerRingCount)
    for key in ringCountDict.keys():
        if(int(key)<MaxVerts):
            ringCount[int(key)] = ringCountDict[key]
    
    printl(ringCount,ringCountDict)
    
    pentagons = numpy.where((VertsPerRingCount==5))[0]
    printl("pentagons",pentagons)
    isolatedPentagons = 0
    sharedpents=numpy.zeros(ringCount[5],NPI)
    for p0 in range(0,ringCount[5]):
        p0index = pentagons[p0]
        for p1 in range(p0+1,ringCount[5]):
            p1index = pentagons[p1]
            
            for v0 in range(0,5):
                vert0 = Rings[p0index*MaxVerts + v0]
                for v1 in range(0,5):
                    vert1 = Rings[p1index*MaxVerts + v1]
                    if(vert0==vert1):
                        sharedpents[p0] = 1
                        sharedpents[p1] = 1
                        break
                
    printl('sharedpents',sharedpents)            
    isolatedPentagons = ringCount[5]- numpy.sum(sharedpents)    
    
    percHex = float(ringCount[6])/float(numpy.sum(ringCount)) 
    percHex *=100.0
    printl('isolatedPentagons',isolatedPentagons)     
    printl("percHex",percHex) 
    
    if(ringCount[3]>0):
        printh("*** warning triangles found in ring stats***")   
    
    printh("time for ring calc",time.time()-stime)
    
    
    outdict = {}
    outdict['percHex'] = percHex
    outdict['isolatedPentagons'] = isolatedPentagons
    outdict['ringCount'] = ringCount
    outdict['VertsPerRingCount'] = VertsPerRingCount
    outdict['ringdict'] = ringdict
    outdict['RingsPerVertCount'] = RingsPerVertCount
    outdict['Rings'] = Rings
    outdict['nrings'] = nrings
    outdict['MaxVerts'] = MaxVerts
    return outdict
    