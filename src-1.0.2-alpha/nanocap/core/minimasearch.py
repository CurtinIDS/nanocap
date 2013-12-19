'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Sep 24 2013
Copyright Marc Robinson 2013
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

Minima search routines,
Minimiser class is passed, which also holds
the current Force Field

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
'''

from nanocap.core.globals import *
import nanocap.core.globals as globals
import os,sys,math,copy,random,time,threading,Queue,ctypes,types
 
import numpy

import nanocap.core.forcefield
from nanocap.core.util import *
from nanocap.clib import clib_interface
clib = clib_interface.clib

class MinimaSearch(object):
    def __init__(self,processor,minimiser):
        #self.gui=gui
        self.processor = processor
        self.config = self.processor.config
        self.recursion_count=0  
        self.lowestEnergy = 99999
        self.gaussianArray = []
        self.gaussiansDropped = 0
        self.uniqueMinima = []
        self.uniqueMinimaCarbon = []
        self.uniqueMinimaCount = 0
        self.minimiser = minimiser
        self.NUnique = 0
        '''
        Here we override the minimisers' modify_PES method so we can add gaussians to
        the PES. This method is always called after the force call in the minimiser.
        '''
        
        self.minimiser.modify_PES = types.MethodType( self.modify_PES, self.minimiser )
    
    def modify_PES(self,minimiser,pos,pointSet):
        #printl("modifying PES by Gaussain",globals.GaussianWidth,globals.GaussianHeight)
        energy = numpy.sum(pointSet.energy)
        if(self.config.opts["AddGaussians"]):
            for gpos in self.gaussianArray:
                genergy,gforce = core.forcefield.get_gauss_energy_and_force(pointSet.npoints,
                                                                    pos,
                                                                    gpos,
                                                                    self.config.opts["GaussianWidth"],
                                                                    self.config.opts["GaussianHeight"])
                energy+=genergy
                pointSet.force+=gforce
                #printl("gauss energy force",genergy,magnitude(gforce))
        return energy, pointSet.force       
    
    
    def print_minima_results(self):
        energies = numpy.zeros(len(self.uniqueMinima))
        for index,pointSet in  enumerate(self.uniqueMinima):
            energies[index] = numpy.sum(pointSet.energy)
            
        order = numpy.argsort(energies)
        
        espacing = 24
        if(self.config.opts["CarbonMinimise"]):
            
            
            headers = ("ID",
                          "Dual Lattice Energy",
                          "Carbon Lattice: Energy",
                          "Energy Per Atom",
                          "Scale",
                          "Constrained Energy")
            
            log = ("%"+str(int(espacing*len(headers)*0.5))+"s\n") %("Minima Search Log")
            log += "-"*(espacing*len(headers)) + "\n"

            format = ("%"+str(espacing)+"s")*len(headers)                
            log += (format+"\n") % headers
            log += "-"*(espacing*len(headers)) + "\n"
            for i in order:
                #print i, numpy.sum(self.uniqueMinima[i].energy)
#                log+= ("%"+str(espacing)+"s%"+str(espacing)+"s%"+str(espacing)+"s%s") %(i, numpy.sum(self.uniqueMinima[i].energy),
#                                         numpy.sum(self.uniqueMinimaCarbon[i].energy),"\n")
                
                try:    
                    FinalEnergy = self.uniqueMinimaCarbon[i].FinalEnergy
                    FinalEnergyPerAtom = self.uniqueMinimaCarbon[i].FinalEnergy/self.uniqueMinimaCarbon[i].npoints
                    FinalScale = self.uniqueMinimaCarbon[i].FinalScale
                    FinalScaleEnergy = self.uniqueMinimaCarbon[i].FinalScaleEnergy
                except:
                    FinalEnergy,FinalEnergyPerAtom,FinalScale,FinalScaleEnergy = "","","",""
              
                
                log+=  (format+"\n") % (i, self.uniqueMinima[i].FinalEnergy,
                                           FinalEnergy,
                                           FinalEnergyPerAtom,
                                           FinalScale,
                                           FinalScaleEnergy)
            
        else:
            log = ("%"+str(espacing)+"s%s") %("Minima Search Log","\n")
            log += "-"*(espacing*2) + "\n"
            log += ("%"+str(espacing)+"s%"+str(espacing)+"s%s") %("ID","Dual Lattice Energy","\n")
            log += "-"*(espacing*2) + "\n"
            for i in order:
                #print i, numpy.sum(self.uniqueMinima[i].energy)
                log+= ("%"+str(espacing)+"s%"+str(espacing)+"s%s") %(i, numpy.sum(self.uniqueMinima[i].energy),"\n")
            
        #f = open("MinimaLog.txt","w")
        #f.write(log)
        #f.close()
        print log
                
    def reset(self):
        printl("resetting minima search logs")
        self.lowestEnergy = 99999
        self.gaussianArray = []
        self.gaussiansDropped = 0
        self.uniqueMinima = []
        self.uniqueMinimaCarbon = []
        self.uniqueMinimaCount = 0
    
    def add_gaussian(self,pointSet):
        self.gaussianArray.append(numpy.copy(pointSet.pos))
        self.gaussiansDropped+=1  
        
        if(magnitude(pointSet.force) == 0.0):
            printl("magnitude(pointSet.force) = 0 ")
        

    
    def random_tangential_pertubation(self,pointSet,dir=None,alpha=None):
        printl("random_tangential_pertubation")#,"dir",dir)
        if(dir==None):dir = randvec(pointSet.pos)
        if(alpha==None):alpha = pointSet.getNNdist()*0.025
        if(self.config.opts["GenType"]=="Fullerene"):isNanotube=False
        if(self.config.opts["GenType"]=="Nanotube"):isNanotube=True
        
        clib.random_tangential_pertubation(ctypes.c_int(pointSet.npoints),
                                           pointSet.pos.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                                           pointSet.freeflagspos.ctypes.data_as(ctypes.POINTER(ctypes.c_double)), 
                                           ctypes.c_double(alpha),
                                           ctypes.c_int(isNanotube)) 
        
        #check if we have offset points into the nanotube
        #printl(numpy.max(pointSet.pos[2::3]*pointSet.freeflagspos[2::3]))
        if(isNanotube):
            zcap = pointSet.pos[2::3]*pointSet.freeflagspos[2::3]
            if(numpy.max(zcap)>0.0):
                
                printl("adding gaussian and offsetting into tube")
                #raw_input("wait.. ")
                indexes = numpy.where(zcap>0)[0]
                pointSet.pos[indexes*3+2]-=pointSet.pos[indexes*3+2] 
            zcap = pointSet.pos[2::3]*pointSet.freeflagspos[2::3]    
            #print zcap 
            
        return dir,alpha
        
    def check_stoping_criteria(self,currentMinima):  
        '''
        stopping criteria
        will have to have calculated ring statistics by this point
        '''
        printh("checking stopping criteria step",currentMinima)

        exitClausesReq = 0
        if(self.config.opts["StopCriteriaIP"]):exitClausesReq+=1
        if(self.config.opts["StopCriteriaPentsOnly"]):exitClausesReq+=1
            
        exitClausesCount = 0
        if(self.config.opts["StopCriteriaIP"]):
            try:
                if(self.processor.isolatedPentagons==self.processor.polyCount[5]):
                    printl("100 % IP? ")
                    exitClausesCount+=1
            except:pass     
                             
        if(self.config.opts["StopCriteriaPentsOnly"]):  
            try:
                if(self.processor.polyCount[5] == numpy.sum(self.processor.polyCount)-self.processor.polyCount[6]):
                    printl("100 % Pentagons? ")
                    exitClausesCount+=1           
            except:pass
        
        
        
        exit_status=False 
        if(exitClausesCount>0 and exitClausesCount == exitClausesReq):
            printl("exitClausesCount",exitClausesCount)
            exit_status=True  

        return exit_status
    
    def check_uniqueness(self,pointSet):
        
        self.minimiser.modifyPES=False
        
        #raw_input("Ready to minimise without Gaussians...")
        self.minimiser.minimise(pointSet,update=False)
        
        #raw_input("Minimised without Gaussians...")
        
        Unique  = True
        for psSet in self.uniqueMinima:
            #check current minima against log
            e1 = numpy.sum(psSet.energy)
            e2 = numpy.sum(pointSet.energy)
            printl("objects",psSet,pointSet,psSet is pointSet)
            printl("objects energy",psSet.energy is pointSet.energy)
            printl("objects pos",psSet.pos is pointSet.pos)
            printl("Comparing energies",e1,e2)
            printl("Comparing sep",magnitude(psSet.pos - pointSet.pos))
            printl("Comparing FinalEnergy",psSet.FinalEnergy,pointSet.FinalEnergy)
            if(numpy.abs(e1-e2) < numpy.abs(1e-5)):
                Unique  = False 
        
        #raw_input("Checked uniqueness...")        
        if(self.config.opts["AddGaussians"]==True):
            self.minimiser.modifyPES=True
            
        printl("Checking uniqueness ",Unique)
        
        #Unique  = True
        return Unique
    
    def select_minima_structure(self,ID):
        if(ID>=self.uniqueMinimaCount):
            return
        printl(self.uniqueMinimaCount,len(self.uniqueMinima))
        
        if(self.config.opts["GenType"]=="Fullerene"):
           self.processor.fullerene.thomsonPoints.pos = numpy.copy(self.uniqueMinima[ID].pos) 
           
           if(self.config.opts["CarbonMinimise"]): 
               self.processor.updateDualLattice(renderUpdate=False)
               self.processor.fullerene.carbonAtoms.pos = numpy.copy(self.uniqueMinimaCarbon[ID].pos)
               self.processor.updateCarbonLattice(renderUpdate=False)
           else:
               pass
               #self.processor.updateDualLattice()
               
        if(self.config.opts["GenType"]=="Nanotube"):
            self.processor.cappedNanotube.thomsonPoints.pos = numpy.copy(self.uniqueMinima[ID].pos) 
            if(self.config.opts["CarbonMinimise"]): 
               self.processor.updateDualLattice(renderUpdate=False)
               self.processor.cappedNanotube.carbonAtoms.pos = numpy.copy(self.uniqueMinimaCarbon[ID].pos)
               self.processor.updateCarbonLattice(renderUpdate=False)
            else:
                pass
               #self.processor.updateDualLattice()
               
        
    
    def basin_climb(self,pointSet):
        printl("climbing out of basin")
        
        pointSet0 = copy.deepcopy(pointSet)
        pointSet1 = copy.deepcopy(pointSet)
        printl(pointSet1.pos is pointSet.pos)

        self.random_tangential_pertubation(pointSet1,alpha=1e-3)        
        energy,grad = self.minimiser.minimise_step_operations(pointSet1.pos,pointSet1)
        force = -1.0*grad
        
        d = numpy.dot((pointSet1.pos-pointSet0.pos),normalise(pointSet1.force))
        dold = d
        #printl("dot",d)

        minalpha = 1e-3
        maxalpha = 5e-1
        alpha = minalpha
    
        count=0

        while(d<0.0):
            nf = normalise(pointSet1.force)
            pointSet1.pos += alpha*-1.0*nf
            
            
            
            if(self.config.opts["GenType"]=="Nanotube"):
                zcap = pointSet1.pos[2::3]*pointSet1.freeflagspos[2::3]
                if(numpy.max(zcap)>0.0):
                    #printl("basin climb offset into nanotube")
                    #raw_input("wait.. ")
                    indexes = numpy.where(zcap>0)[0]
                    pointSet1.pos[indexes*3+2]-=pointSet1.pos[indexes*3+2] 
                    #printl("new cap z max",numpy.max(zcap))
                    
            rp = (pointSet1.pos-pointSet0.pos)
            d = numpy.dot(rp,nf)
            #printl("dot",d,magnitude(rp),"alpha",alpha)

            energy,grad = self.minimiser.minimise_step_operations(pointSet1.pos,pointSet1)
            force = -1.0*grad
            #if(count%100==0):
            #    pointSet.pos = copy.copy(pointSet1.pos)
            #    self.minimiser.update_output(pointSet)
                #raw_input("step...")
            count+=1
            
            if(abs(d)>abs(dold)):
                alpha*=2.0
            else:
                alpha/=2.0
            
            if(alpha<minalpha):alpha=minalpha
            if(alpha>maxalpha):alpha=maxalpha        
            #alpha*=2.0
        
        pointSet1.pos += 2.0*alpha*-1.0*normalise(pointSet1.force)
        
        if(self.config.opts["GenType"]=="Nanotube"):
            zcap = pointSet1.pos[2::3]*pointSet1.freeflagspos[2::3]
            if(numpy.max(zcap)>0.0):
                #printl("basin climb offset into nanotube")
                #raw_input("wait.. ")
                indexes = numpy.where(zcap>0)[0]
                pointSet1.pos[indexes*3+2]-=pointSet1.pos[indexes*3+2] 
                #printl("new cap z max",numpy.max(zcap))
        
        printl("out of basin",d,"displacement",magnitude((pointSet1.pos-pointSet0.pos)))
        pointSet.pos = copy.deepcopy(pointSet1.pos)
        
        #raw_input("out of basin...")
        
    def search(self,pointSet):
        '''
        Uses globals.NStructures,globals.NMaxStructures
        '''    
        
        steptime = time.time()
        printh("Searching for minima",threading.current_thread(),"NStructures",self.config.opts["NStructures"],
               "NMaxStructures",self.config.opts["NMaxStructures"])
        #for i in range(0,globals.NStructures):
        
        self.NUnique = 0
        NTotal = 0
        
        #if(globals.AddGaussians==False):
        #    current_odir,current_alpha = self.random_tangential_pertubation(pointSet)
            
        
        while(self.NUnique < self.config.opts["NStructures"] and NTotal < self.config.opts["NMaxStructures"]):
            if(self.config.opts["StopMin"]==1): break
            
            
            stime = time.time()
            
            printh("Minimising, self.NUnique",self.NUnique,"NTotal", NTotal)
            
            self.minimiser.minimise(pointSet,update=False)
            
            
            if(pointSet.FinalEnergy<self.lowestEnergy):
                self.lowestEnergy = pointSet.FinalEnergy
                self.lowestEnergyPos = numpy.copy(pointSet.pos)
                printl("Lowest energy thomson solution found")
            
            if(self.config.opts["StopMin"]==1): break
            
            Unique = self.check_uniqueness(pointSet)
            
            if(Unique):
                printl("Unique Minima Found")
                printh("time for unique structure",time.time()-stime)
                
                if(self.config.opts["CarbonMinimise"]):
                    self.minimiser.update_output(pointSet,renderUpdate=False)
                else:
                    self.minimiser.update_output(pointSet,renderUpdate=False)
                
                #raw_input("Press Enter to continue...")
                self.uniqueMinima.append(copy.deepcopy(pointSet))
                self.uniqueMinimaCount+=1
                self.NUnique+=1
                
                if(self.config.opts["CarbonMinimise"]):
                    #self.processor.minimiseCarbonAtoms()
                    if(self.config.opts["GenType"]=="Fullerene"):
                       carbonAtoms = self.processor.fullerene.carbonAtoms
                    if(self.config.opts["GenType"]=="Nanotube"):
                       carbonAtoms = self.processor.cappedNanotube.carbonAtoms   
                    
                    self.processor.carbonLatticeMinimiser.minimise_scale(carbonAtoms)
                    self.processor.carbonLatticeMinimiser.minimise(carbonAtoms)   
                    
                    self.uniqueMinimaCarbon.append(copy.deepcopy(carbonAtoms))
                
                self.processor.addCurrentStructure()
                
                #current_odir,current_alpha = self.random_tangential_pertubation(pointSet)
                    
                self.print_minima_results()
                

            exit_status = self.check_stoping_criteria(NTotal)   
            
                        
            
            if(self.config.opts["BasinClimb"]):
                pre = copy.deepcopy(pointSet)
                self.basin_climb(pointSet)
                printl("basin hopping offset",magnitude(pre.pos - pointSet.pos))
                #self.minimiser.update_output(pointSet)
                #raw_input("out of basin...")
            
            if(self.config.opts["AddGaussians"]):
                printl("adding gaussian",self.gaussiansDropped)
                
                self.minimiser.modifyPES=True
                self.add_gaussian(pointSet)
                    
            self.lastMinimumEnergy = pointSet.FinalEnergy   
            
            if(self.config.opts["ResetPerIteration"]):        
                if(self.config.opts["GenType"]=="Nanotube"):
                    #self.gui.dock.currentToolbar().ResetNanotubeCapDualLatticePoints()
                    
                    self.processor.nanotube.reset()
                    self.processor.resetCap()
                    pointSet = self.processor.nanotube.cappedTubeThomsonPoints   
                    pointSet.FinalEnergy = self.lastMinimumEnergy   
                else:
                    #self.gui.dock.currentToolbar().ResetFullereneDualLatticePoints()
                    self.processor.resetFullereneThomsonPoints()
                    pointSet = self.processor.fullerene.thomsonPoints 
                    pointSet.FinalEnergy = self.lastMinimumEnergy   
                    
            if(self.config.opts["RandomPertubationPerIteration"]==True): 
                odir,alpha = self.random_tangential_pertubation(pointSet)
                
            #self.minimiser.update_output(pointSet)
            #raw_input("just offset")
            NTotal+=1
        
        
        if(self.uniqueMinimaCount>0):    
            self.select_minima_structure(self.uniqueMinimaCount-1)
            self.print_minima_results()
        
        self.processor.renderUpdate()
        
        printl("End minima search, found ",self.NUnique,"structures in",time.time()-steptime)
 
                
                  
        
        
        
        
        
        
        