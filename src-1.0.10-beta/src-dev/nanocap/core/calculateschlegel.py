'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Apr 15, 2014
Copyright Marc Robinson  2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

return a new pointset that is the 
2D projection.

also calculate carbon rings


-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
'''

import numpy
import nanocap.core.points as points
from nanocap.core.util import *
from nanocap.core.globals import *


def calculate_schlegel_projection(pointSet,gamma):
    
    printl("Calculating Schlegel",pointSet,gamma)
    outPoints = points.Points(pointSet.PointSetLabel+" Schlegel")
    outPoints.initArrays(pointSet.npoints)
    outPoints.pos = numpy.copy(pointSet.pos)
    
    z = outPoints.pos[2::3]
    zmax,zmin = numpy.max(z),numpy.min(z)
    outPoints.pos[2::3]-=zmin
    
    x = outPoints.pos[0::3]
    y = outPoints.pos[1::3]
    z = outPoints.pos[2::3]
    x2 = x*x
    y2 = y*y
    zoff = gamma*numpy.fabs(z)
    m = numpy.sqrt(x2 + y2)
    axisp = numpy.where(m<1e-10)[0]
    printl(axisp)
    m[axisp]=1e-10
    outPoints.pos[0::3] += zoff*x/m 
    outPoints.pos[1::3] += zoff*y/m 
    outPoints.pos[2::3]  = 0  
    
    return outPoints