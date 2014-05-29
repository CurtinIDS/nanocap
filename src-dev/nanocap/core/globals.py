'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Aug 1 2013
Copyright Marc Robinson 2013
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

Generic globals

The global CONFIG is set here which defines
the user and database locations. This can
be editted at any point to change the 
NanoCap config.
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
'''

import os,numpy,sys,inspect,platform
import ctypes
from nanocap.core import config


VERSION = "1.0.10 beta"
COPYRIGHT = " M Robinson 2012 - 2014"
        
ps = platform.system()
if(ps=="Darwin"):PLATFORM = "osx"
if(ps=="Windows"):PLATFORM = "win"
if(ps=="Linux"):PLATFORM = "linux"        
    
#os.system("export OMP_NUM_THREADS=4")
if(PLATFORM!='win'):os.environ["OMP_NUM_THREADS"] = "4"

NPF = numpy.float64
NPF32 = numpy.float32
NPI = numpy.int32
use_clib= True
DEBUG   = False
VERBOSE = False
ERROR   = False

NANOCAP_META = {"info":"Software for the generation of carbon nanostructures",
                "version": "NanoCap {}".format(VERSION),
                "copyright": "Copyright {}".format(COPYRIGHT),
                "url": "http://sourceforge.net/projects/nanocap/"
               }

CONFIG = config.Config()

class StructureType(object):
    '''
    enum for comparisons
    text for internal text
    label for decoration
    '''
    def __init__(self,enum,text,label):
        self.enum = enum
        self.text = text
        self.label = label
    
    def __eq__(self, enum):
        if self.enum==enum:
            return True
        else:
            return False

    def __ne__(self, enum):
        return not self.__eq__(enum)

POINTKEYS = "DualLattice","CarbonAtoms"

NULL = -1
FULLERENE = 0
CAPPEDNANOTUBE = 1
NANOTUBE = 2
CAP = 3
ONION = 4
CAPPEDMWNT = 5
CAP_R = 6

STRUCTURE_TYPES = [0]*7
STRUCTURE_TYPES[FULLERENE] = StructureType(FULLERENE,"FULLERENE","Fullerene")
STRUCTURE_TYPES[CAPPEDNANOTUBE] = StructureType(CAPPEDNANOTUBE,"CAPPEDNANOTUBE","Capped Nanotube")
STRUCTURE_TYPES[NANOTUBE] = StructureType(NANOTUBE,"NANOTUBE","Nanotube")
STRUCTURE_TYPES[CAP] = StructureType(CAP,"CAP","Cap Primary")
STRUCTURE_TYPES[CAP_R] = StructureType(CAP_R,"CAP_R","Cap Secondary")
STRUCTURE_TYPES[ONION] = StructureType(ONION,"ONION","Onion")
STRUCTURE_TYPES[CAPPEDMWNT] = StructureType(CAPPEDMWNT,"CAPPEDMWNT","Capped MWNT")




#for now we will hold these has globals




                    
                     
                     
