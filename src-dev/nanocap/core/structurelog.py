'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Oct 3 2013
Copyright Marc Robinson 2013
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

Storage of structures in a class. Will
require offline storage.


#TODO
Store structures in local && online database
Can view/load/save to local or online. 
Will need userID and time

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
'''


from nanocap.core.globals import *
import nanocap.core.globals as globals
import os,sys,math,copy,random,time,threading,Queue,ctypes,types
 
import numpy
from nanocap.core.util import *
import sqlite3



class Structure(object):
    def __init__(self,type,structobject,cap=None,
                 NCapDualLattice=None,NTubeDualLattice=None,NCapCarbonAtoms=None,
                 NTubeCarbonAtoms=None,rings=None):
        
        self.type = type
        self.rings = numpy.copy(rings)
        
        if(self.type=="Fullerene"):
            self.fullerene = copy.deepcopy(structobject)
        
            printl("added structure checking copies")
            printl("fullerene", self.fullerene is structobject)  
            printl("fullerene.thomsonPoints", self.fullerene.thomsonPoints is structobject.thomsonPoints)     
            printl("fullerene.thomsonPoints.pos", self.fullerene.thomsonPoints.pos is structobject.thomsonPoints.pos)   
            printl("fullerene.carbonAtoms", self.fullerene.carbonAtoms is structobject.carbonAtoms)     
            printl("fullerene.carbonAtoms.pos", self.fullerene.carbonAtoms.pos is structobject.carbonAtoms.pos)   
            printl("fullerene.thomsonPoints.freeflags", self.fullerene.thomsonPoints.freeflags is structobject.thomsonPoints.freeflags)   
            
            
        if(self.type=="Nanotube"):    
            self.nanotube = copy.deepcopy(structobject)
            self.cap = copy.deepcopy(cap)
#            self.NCapDualLattice=NCapDualLattice
#            self.NTubeDualLattice=NTubeDualLattice
#            self.NCapCarbonAtoms=NCapCarbonAtoms
#            self.NTubeCarbonAtoms=NTubeCarbonAtoms
            
            printl("added structure checking copies")
            printl("nanotube", self.nanotube is structobject)     
            
    def getDualLatticeEnergy(self):
        if(self.type=="Fullerene"):
            return self.fullerene.thomsonPoints.FinalEnergy
        if(self.type=="Nanotube"):
            return self.nanotube.cappedTubeThomsonPoints.FinalEnergy
    
    def getCarbonLatticeEnergy(self):
        try:
            if(self.type=="Fullerene"):
                FinalEnergy = self.fullerene.carbonAtoms.FinalEnergy
                FinalEnergyPerAtom = self.fullerene.carbonAtoms.FinalEnergy/self.fullerene.carbonAtoms.npoints
                FinalScale = self.fullerene.carbonAtoms.FinalScale
                FinalScaleEnergy = self.fullerene.carbonAtoms.FinalScaleEnergy
                return FinalEnergy,FinalEnergyPerAtom,FinalScale,FinalScaleEnergy
            
            if(self.type=="Nanotube"):
                FinalEnergy = self.nanotube.cappedTubeCarbonAtoms.FinalEnergy
                FinalEnergyPerAtom = self.nanotube.cappedTubeCarbonAtoms.FinalEnergy/self.nanotube.cappedTubeCarbonAtoms.npoints
                FinalScale = self.nanotube.cappedTubeCarbonAtoms.FinalScale
                FinalScaleEnergy = self.nanotube.cappedTubeCarbonAtoms.FinalScaleEnergy
                return FinalEnergy,FinalEnergyPerAtom,FinalScale,FinalScaleEnergy
        
        except:
            return "","","",""
        
#        if(nanotube!=None):
#                    self.NDualLatticePoints = NDualLatticePoints
#        self.NCarbonAtoms = NCarbonAtoms
#        
#        self.dualLattice = copy.deepcopy(dualLatticePointSet)
#        self.carbonLattice = copy.deepcopy(carbonLatticePointSet)
        
        
            
#            self.n = copy.deepcopy(nanotube)
#            self.nanotube_n = self.n.n
#            self.nanotube_m = self.n.m
#            self.nanotube_u = self.n.u
#            self.nanotube_mappingAngle = self.n.mappingAngle
#            self.nanotube_tubeDualLatticeCOM = self.n.tubeThomsonPointsCOM
            
        
        
        
#        printl("added structure checking copies")
#        printl("rings", self.rings is rings)
#        printl("dualLattice", self.dualLattice is dualLatticePointSet)
#        printl("carbonLattice", self.carbonLattice is carbonLatticePointSet) 
#        if(nanotube!=None):
#            printl("nanotube_n", nanotube.n is self.n.n)     
#            printl("nanotube_n", self.n is nanotube)  
#            printl("nanotube_n", self.n.tubeCarbonAtoms is nanotube.tubeCarbonAtoms)  
        
class StructureLog(object):
    def __init__(self,type):
        self.structures = []
        self.type = type
        self.lastAdded = None
        self.locklog = False
        
        self.logpad = 4
        
        if(self.type=="Nanotube"):
            self.headers = ["ID","Ch (n,m)","Unit Radius Scale","Uncapped Length",
                   "N Dual (Cap,Tube)",
                   "N Carbon (Cap,Tube)"]
        
        else:
            self.headers = ["ID",
                       "N Dual",
                       "N Carbon"]
            
        self.headers.extend(["3-rings","4-rings","5-rings",  
                        "6-rings", "7-rings",  "8-rings" ])      
        
        self.headers.extend(["Dual Lattice Energy",
                        "Carbon Lattice: Energy",
                           "Energy Per Atom",
                           "Scale Factor",
                           "Constrained Energy"])
    
    
    #def loadFromDataBase(self):
        
    
    #def saveStructureToDataBase(self):    
        
        
    def reset(self):
        self.structures = []
        
    def addStructure(self,structobject,cap=None,
                     NCapDualLattice=None,NTubeDualLattice=None,NCapCarbonAtoms=None,
                     NTubeCarbonAtoms=None,rings=None):
        
        self.locklog = True
        
        if(self.type=="Fullerene"):
            
            #Nd = strucobject.npoints
            #Nc = dualLatticePointSet.npoints*2 - 4
            structure = Structure(self.type,structobject,rings = rings)
        
        if(self.type=="Nanotube"):
            #Nd = dualLatticePointSet.npoints
            #Nc = dualLatticePointSet.npoints*2 - 4
            structure = Structure(self.type,structobject,cap = cap,
                                  rings = rings)    
            
        self.lastAdded = len(self.structures)
        self.structures.append(structure)
        
        
        self.locklog = False
    
    def get_data(self,i):
        while(self.locklog):
            pass
        
        FinalEnergy,FinalEnergyPerAtom,FinalScale,FinalScaleEnergy = self.structures[i].getCarbonLatticeEnergy()
        
        if(self.type=="Nanotube"):
            Nd = str(self.structures[i].nanotube.cappedTubeThomsonPoints.npoints)
            Nd += " "+str(self.structures[i].cap.thomsonPoints.npoints)
            Nd += " "+str(self.structures[i].nanotube.tubeThomsonPoints.npoints)
            
            try:
                Nc = str(self.structures[i].nanotube.cappedTubeCarbonAtoms.npoints)
                Nc += " "+str(self.structures[i].cap.thomsonPoints.npoints*2 - 2)
                Nc += " "+str(self.structures[i].nanotube.tubeCarbonAtoms.npoints)
            except:
                Nc = 0
                printl("log: no carbon atoms found")
                
            Ch = str(self.structures[i].nanotube.n)+" "
            Ch += str(self.structures[i].nanotube.m)
            Length =str(self.structures[i].nanotube.length)
            Scale = str(self.structures[i].nanotube.scale)
            data  = [i,Ch,Scale,Length,Nd,Nc,
            self.structures[i].rings[3],
            self.structures[i].rings[4],
            self.structures[i].rings[5],
            self.structures[i].rings[6],
            self.structures[i].rings[7],
            self.structures[i].rings[8],
            self.structures[i].getDualLatticeEnergy(),
            FinalEnergy,
            FinalEnergyPerAtom,
            FinalScale,
            FinalScaleEnergy]
        else:
            Nd = self.structures[i].fullerene.thomsonPoints.npoints
            try:
                Nc = self.structures[i].fullerene.carbonAtoms.npoints
            except:
                Nc = 0
                printl("log: no carbon atoms found")
                
            data  = [i,Nd,Nc,
                    self.structures[i].rings[3],
                    self.structures[i].rings[4],
                    self.structures[i].rings[5],
                    self.structures[i].rings[6],
                    self.structures[i].rings[7],
                    self.structures[i].rings[8],
                    self.structures[i].getDualLatticeEnergy(),
                    FinalEnergy,
                    FinalEnergyPerAtom,
                    FinalScale,
                    FinalScaleEnergy]
            
            #data = [i,0,0,0,0,0,0,0,0,0,0,0,0,0]
        
        printl(len(data),data)
        return data  
        
    def get_data_OLD(self,i):
        while(self.locklog):
            pass
        
        try:    
            FinalEnergy = self.structures[i].carbonLattice.FinalEnergy
            FinalEnergyPerAtom = self.structures[i].carbonLattice.FinalEnergy/self.structures[i].carbonLattice.npoints
            FinalScale = self.structures[i].carbonLattice.FinalScale
            FinalScaleEnergy = self.structures[i].carbonLattice.FinalScaleEnergy
        except:
            FinalEnergy,FinalEnergyPerAtom,FinalScale,FinalScaleEnergy = "","","",""
                    
        if(self.type=="Nanotube"):
            Nd = str(self.structures[i].dualLattice.npoints)+" "+str(self.structures[i].NCapDualLattice)
            Nd += " "+str(self.structures[i].NTubeDualLattice)
            Nc = str(self.structures[i].carbonLattice.npoints)+" "+str(self.structures[i].NCapCarbonAtoms)
            Nc += " "+str(self.structures[i].NTubeCarbonAtoms)
            Ch = str(self.structures[i].nanotube_n)+" "
            Ch += str(self.structures[i].nanotube_m)+" "
            Ch += str(self.structures[i].nanotube_u)
            data  = [i,Ch,Nd,Nc,
            self.structures[i].rings[3],
            self.structures[i].rings[4],
            self.structures[i].rings[5],
            self.structures[i].rings[6],
            self.structures[i].rings[7],
            self.structures[i].rings[8],
            self.structures[i].dualLattice.FinalEnergy,
            FinalEnergy,
            FinalEnergyPerAtom,
            FinalScale,
            FinalScaleEnergy]
        else:
            Nd = self.structures[i].dualLattice.npoints
            Nc = self.structures[i].carbonLattice.npoints
            data  = [i,Nd,Nc,
                    self.structures[i].rings[3],
                    self.structures[i].rings[4],
                    self.structures[i].rings[5],
                    self.structures[i].rings[6],
                    self.structures[i].rings[7],
                    self.structures[i].rings[8],
                    self.structures[i].dualLattice.FinalEnergy,
                    FinalEnergy,
                    FinalEnergyPerAtom,
                    FinalScale,
                    FinalScaleEnergy]
            
            #data = [i,0,0,0,0,0,0,0,0,0,0,0,0,0]
        
        printl(len(data),data)
        return data     
    
    def get_sorted_indexes(self):
        while(self.locklog):
            pass
        
        energies = numpy.zeros(len(self.structures))
        for index,structure in enumerate(self.structures):
            #energies[index] = numpy.sum(structure.dualLattice.energy)
            energies[index] = structure.getDualLatticeEnergy()
        order = numpy.argsort(energies)
        return order    
    
    def write_log(self,folder,filename="StructureLog.txt"):
        printl("writing log")
#        if os.path.exists(os.path.join(folder,filename)):
#            f = open(os.path.join(folder,filename),"a")
#            log = self.get_log_string()
#            f.write(log)
#            f.close()
#        else:
        f = open(os.path.join(folder,filename),"w")
        log = self.get_header_string()
        f.write(log)
        log = self.get_log_string()
        f.write(log)
        f.close()
    
    
    def get_header_string(self):
        while(self.locklog):
            pass
        
        

        headers = tuple(self.headers)
        format =""
        tot = 0
        for h in headers:
            format+="%"+str(len(h)+self.logpad)+"s"
            tot +=len(h)+self.logpad
        
        printl("headers",headers,len(headers))
        title = self.type+" Structure Log"
        log = ("%"+str(int(tot*0.5))+"s\n") %(title)
        log += "-"*(tot) + "\n"

        
        printl("format",format)           
        log += (format+"\n") % headers
        log += "-"*(tot) + "\n"
        
        return log
    
    def get_log_string(self):
        
        order = self.get_sorted_indexes()
        headers = tuple(self.headers)
        format =""
        tot = 0
        for h in headers:
            format+="%"+str(len(h)+self.logpad)+"s"
            tot +=len(h)+self.logpad
            
        log=""
        for i in order:
            data = self.get_data(i)
            printl(format)
            log+=  (format+"\n") % (tuple(data))
        return log    
        
    def print_log(self):
        log = self.get_header_string()
        log += self.get_log_string()
        print log    
        