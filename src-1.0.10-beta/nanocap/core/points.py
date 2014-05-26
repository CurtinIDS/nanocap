'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Aug 24 2011
Copyright Marc Robinson 2013
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

Points class for holding positions, freeflags etc
Functions to get bounds, centers, NNdists etc.

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
'''

from nanocap.core.globals import *
from nanocap.core.util import *
import os,sys,math,copy,random,time
import numpy


class Points(object):
    def __init__(self,PointSetLabel):
        self.PointSetLabel = PointSetLabel
        self.final_energy = 0 
        self.final_scale_energy = 0 
        self.final_scale = 0 

    def setLabel(self,lab):
        self.PointSetLabel = lab
        
    def getCenter(self):
        b = self.getBounds()
        return numpy.array([(b[0]+b[3])*0.5,(b[1]+b[4])*0.5,(b[2]+b[5])*0.5])
        
    def getBounds(self):
        if(self.npoints==0):
            return 0,0,0,0,0,0
        x,y,z = self.pos[0::3],self.pos[1::3],self.pos[2::3]
        return numpy.min(x),numpy.min(y),numpy.min(z),numpy.max(x),numpy.max(y),numpy.max(z)        
    
    def getNNdist(self,ncheck=1):        
        avr2 = []
        for i in range(0,ncheck):
        
            xd = self.pos[i] - self.pos[0::3]
            yd = self.pos[i] - self.pos[1::3]
            zd = self.pos[i] - self.pos[2::3]
            
            r2 = xd*xd + yd*yd + zd*zd
            
            r2 = numpy.delete(r2,i)
            avr2.append(numpy.min(r2))
        
        return math.sqrt(numpy.average(avr2))

    def initArrays(self,npoints,free=True,damp=False):
        self.npoints = npoints
        self.pos = numpy.zeros(npoints*3,NPF)
        self.pos0 = numpy.zeros(npoints*3,NPF)
        if(free):
            self.freeflagspos = numpy.ones(npoints*3,NPF)
            self.freeflags = numpy.ones(npoints,NPF)
        else:
            self.freeflagspos = numpy.zeros(npoints*3,NPF)
            self.freeflags = numpy.zeros(npoints,NPF)    
        if(damp):
            self.dampflagspos = numpy.ones(npoints*3,NPF)
            self.dampflags = numpy.ones(npoints,NPF)
        else:
            self.dampflagspos = numpy.zeros(npoints*3,NPF)
            self.dampflags = numpy.zeros(npoints,NPF)    
                
    def reset(self,npoints):
        self.npoints = npoints
        self.pos = numpy.zeros(npoints*3,NPF)

            
    def removeIndexes(self,indexes):
        self.npoints -= len(indexes)
        
        posindexes = numpy.concatenate((indexes*3,indexes*3+1,indexes*3+2))
        
        self.pos = numpy.delete(self.pos,posindexes)
        try:self.freeflagspos = numpy.delete(self.freeflagspos,posindexes)
        except:pass
        try:self.freeflags = numpy.delete(self.freeflags,indexes)
        except:pass
        
    def getPoint(self,index):
        return numpy.array([self.pos[index*3],self.pos[index*3+1],self.pos[index*3+2]])
       
        
    def __str__(self):
        return "PointSet: "+str(self.PointSetLabel)

def joinPointSets(sets):
        
    out = Points("")
    np = 0
    pos = []
    pos0 = []
    freeflags = []
    freeflagspos = []
    dampflags = []
    dampflagspos = []
    for set in sets:
        np += set.npoints
        pos0.append(set.pos0)
        pos.append(set.pos)
        freeflagspos.append(set.freeflagspos)
        freeflags.append(set.freeflags)
        #dampflagspos.append(set.dampflagspos)
        #dampflags.append(set.dampflags)
    out.initArrays(np)
    
    out.pos = numpy.concatenate(pos)
    out.pos0 = numpy.concatenate(pos0)
    out.freeflagspos = numpy.concatenate(freeflagspos)
    out.freeflags = numpy.concatenate(freeflags)
    #out.dampflagspos = numpy.concatenate(dampflagspos)
    #out.dampflags = numpy.concatenate(dampflags)
    return out

