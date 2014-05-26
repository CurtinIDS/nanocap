'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Sep 20 2013
Copyright Marc Robinson 2013
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=


routine to array of triangle centers

returns: array of centers 
         [x1,y1,z1,x2,y2,z2...]

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
'''

from nanocap.core.globals import *
from nanocap.core.util import *
import os,sys,math,copy,random,time,threading,Queue,ctypes
import nanocap.core.points as points

def constructDual(pointSet,ntriangles,verts,outpoints=None,outlabel="dual points"):    
    print "outpoints",outpoints
    if (outpoints==None):
        outpoints = points.Points(outlabel)    
        outpoints.initArrays(ntriangles)
    else:
        outpoints.reset(ntriangles)
    
    print "outpoints",outpoints
        
    v1x = pointSet.pos[verts[0::3]*3]
    v1y = pointSet.pos[verts[0::3]*3+1]    
    v1z = pointSet.pos[verts[0::3]*3+2]   
    
    v2x = pointSet.pos[verts[1::3]*3]
    v2y = pointSet.pos[verts[1::3]*3+1]    
    v2z = pointSet.pos[verts[1::3]*3+2]   
    
    v3x = pointSet.pos[verts[2::3]*3]
    v3y = pointSet.pos[verts[2::3]*3+1]    
    v3z = pointSet.pos[verts[2::3]*3+2]    
    
    cx = (v1x+v2x+v3x)/3.0
    cy = (v1y+v2y+v3y)/3.0
    cz = (v1z+v2z+v3z)/3.0
     
    outpoints.pos[0::3] = cx 
    outpoints.pos[1::3] = cy 
    outpoints.pos[2::3] = cz  
    
    
    return outpoints
    