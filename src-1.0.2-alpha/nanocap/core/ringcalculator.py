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
import nanocap.core.globals as globals
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
    
#    surfaceArea = 0
#    volume = 0
#    for i in range(0,nrings):
#        #print "ring",i,"verts",vertsPerRingCount[i]
#
#        v1,v2,v3 = rings[i*maxVerts],rings[i*maxVerts+1],rings[i*maxVerts+2]      
#          
#        p1 = numpy.array([pointSet.pos[v1*3],
#                          pointSet.pos[v1*3+1],
#                          pointSet.pos[v1*3+2]])    
#        p2 = numpy.array([pointSet.pos[v2*3],
#                          pointSet.pos[v2*3+1],
#                          pointSet.pos[v2*3+2]])    
#        p3 = numpy.array([pointSet.pos[v3*3],
#                          pointSet.pos[v3*3+1],
#                          pointSet.pos[v3*3+2]])    
#        
#        
#        #norm = unit_normal(p1,p2,p3)
#        
#        #norm = normalise(numpy.cross(p1-p3,p2-p3))
#        norm = normalise(numpy.cross(p3-p1,p3-p2))
#        
#        #check outward
#        
##        dp = numpy.dot(p1,norm)
##        if(dp<0):
##            norm = normalise(numpy.cross(p3-p2,p3-p1))
##            dp = numpy.dot(p1,norm)
##            print "corrected",dp
#                    
#        totxyz = numpy.zeros(3,NPF)
#        
#        center = numpy.zeros(3,NPF)
#        for j in range(0,vertsPerRingCount[i]): 
#            print "v",j,rings[i*maxVerts +j]
#            
#            jindex0 = j
#            jindex1 = ((j+1) % vertsPerRingCount[i])
#            v1,v2 = rings[i*maxVerts+jindex0],rings[i*maxVerts+jindex1]
#                    
#            p1 = numpy.array([pointSet.pos[v1*3],
#                              pointSet.pos[v1*3+1],
#                              pointSet.pos[v1*3+2]])    
#            
#            p2 = numpy.array([pointSet.pos[v2*3],
#                              pointSet.pos[v2*3+1],
#                              pointSet.pos[v2*3+2]])    
#            
#            cp = numpy.cross(p1,p2)
##            dp = numpy.dot(p1,cp)
##            if(dp<0):
##                cp = numpy.cross(p2,p1)
##                dp = numpy.dot(p1,cp)
##                print "corrected",dp
#            
#            center+= p1/vertsPerRingCount[i]
#            
#            print jindex0,jindex1,p1,p2,cp
#            totxyz+=cp
#        
#        
#        
#        area = numpy.abs(numpy.dot(totxyz,norm)/2.0)
#        
#        print center,area
#        
#        surfaceArea += area
#        
#        volume += numpy.abs(center[0] * norm[0] * area)
#        
#        #print "area of ring",abs(area/2.0)
#            
#    #self.surfaceArea,self.volume = 1,1
#    printl("surfaceArea",surfaceArea,"volume", volume)
    
    
#    for p in range(0,pointSet.npoints):
#        print pointSet.pos[p*3+2]
    return out[0],out[1]
    

def calculate_rings(pointSet,MaxNebs=3,MaxVerts=9):
    
    stime = time.time()
    
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
    