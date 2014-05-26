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

from nanocap.core.util import *
from nanocap.clib import clib_interface
from nanocap.core import structurelog
from nanocap.core import forcefield
from nanocap.core import minimisation
clib = clib_interface.clib

class MinimaSearch(object):
    def __init__(self,dual_lattice_minimiser,
                 carbon_lattice_minimiser=None,
                 basin_climb=False,add_gaussians=False,
                 reset_per_iteration=False,random_pertubation_per_iteration=False,
                 stop_criteria_IP=False,stop_criteria_pents_only=False,calc_rings=False,
                 callback=None,StructureLog=None):
        self.recursion_count=0  
        self.lowestEnergy = 99999
        self.gaussianArray = []
        self.gaussians_dropped = 0
        self.uniqueMinima = []
        self.uniqueMinimaCarbon = []
        self.unique_minima_count = 0
        
        self.dual_lattice_minimiser = minimisation.DualLatticeMinimiser()
        self.carbon_lattice_minimiser = minimisation.CarbonLatticeMinimiser()
        
        self.dual_lattice_minimiser = dual_lattice_minimiser
        self.carbon_lattice_minimiser = carbon_lattice_minimiser

        self.NUnique = 0
        self.callback = callback
        self.status = "Performing structure search"
        '''
        Here we override the minimisers' modify_PES method so we can add gaussians to
        the PES. This method is always called after the force call in the minimiser.
        '''
        self.basin_climb = basin_climb
        self.add_gaussians = add_gaussians
        self.reset_per_iteration = reset_per_iteration
        self.random_pertubation_per_iteration = random_pertubation_per_iteration
        self.stop_criteria_IP =stop_criteria_IP
        self.stop_criteria_pents_only=stop_criteria_pents_only
        self.calc_rings = calc_rings
        
        self.GaussianWidth = 0.5
        self.GaussianHeight = 0.5
        
        self.dual_lattice_minimiser.modify_PES = types.MethodType( self.modify_PES, self.dual_lattice_minimiser )
    
        if(StructureLog==None):self.structure_log = structurelog.StructureLog(self.dual_lattice_minimiser.structure.type)
        else: self.structure_log = StructureLog
               
    def modify_PES(self,minimiser,pos,pointSet):
        #printl("modifying PES by Gaussain",globals.GaussianWidth,globals.GaussianHeight)
        energy = numpy.sum(pointSet.energy)
        if(self.add_gaussians):
            for gpos in self.gaussianArray:
                genergy,gforce = core.forcefield.get_gauss_energy_and_force(pointSet.npoints,
                                                                    pos,
                                                                    gpos,
                                                                    self.GaussianWidth,
                                                                    self.GaussianHeight)
                energy+=genergy
                pointSet.force+=gforce
                #printl("gauss energy force",genergy,magnitude(gforce))
        return energy, pointSet.force       
        
    def reset(self):
        printl("resetting minima search logs")
        self.lowestEnergy = 99999
        self.gaussianArray = []
        self.gaussians_dropped = 0
        self.uniqueMinima = []
        self.uniqueMinimaCarbon = []
        self.unique_minima_count = 0
    
    def add_gaussian(self,pointSet):
        self.status = "Adding Gaussian"    
        self.gaussianArray.append(numpy.copy(pointSet.pos))
        self.gaussians_dropped+=1  
        
        if(magnitude(pointSet.force) == 0.0):
            printl("magnitude(pointSet.force) = 0 ")
        

    
    def random_tangential_pertubation(self,pointSet,dir=None,alpha=None):
        printl("random_tangential_pertubation")#,"dir",dir)
        self.status = "Applying random tangential pertubation"   
        if(dir==None):dir = randvec(pointSet.pos)
        if(alpha==None):alpha = pointSet.getNNdist()*0.025
        
        if(self.dual_lattice_minimiser.structure.type==FULLERENE):isNanotube=False
        if(self.dual_lattice_minimiser.structure.type==CAPPEDNANOTUBE):isNanotube=True
        
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
        self.status = "Checking stopping criteria"   
        
        exitClausesReq = 0
        if(self.stop_criteria_IP):exitClausesReq+=1
        if(self.stop_criteria_pents_only):exitClausesReq+=1
            
        exitClausesCount = 0
        if(self.stop_criteria_IP):
            try:
                if(self.processor.isolatedPentagons==self.processor.polyCount[5]):
                    printl("100 % IP? ")
                    exitClausesCount+=1
            except:pass     
                             
        if(self.stop_criteria_pents_only):  
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
    
    
    def check_uniqueness(self,structure):
        self.status = "Checking new structure"
        unique = self.structure_log.check_for_uniqueness(structure)
        return unique
    
    def select_minima_structure(self,ID):
        if(ID>=self.unique_minima_count):
            return
        printl(self.unique_minima_count,len(self.uniqueMinima))
        
        structure = self.dual_lattice_minimiser.structure
        structure.dual_lattice.pos = numpy.copy(self.uniqueMinima[ID].pos)         
    
    def start_basin_climb(self,pointSet):
        printl("climbing out of basin")
        self.status = "climbing out of basin"
        
        pointSet0 = copy.deepcopy(pointSet)
        pointSet1 = copy.deepcopy(pointSet)
        printl(pointSet1.pos is pointSet.pos)

        self.random_tangential_pertubation(pointSet1,alpha=1e-3)        
        energy,grad = self.dual_lattice_minimiser.minimise_step_operations(pointSet1.pos,pointSet1)
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
            
            if(self.dual_lattice_minimiser.structure.type==CAPPEDNANOTUBE):
                zcap = pointSet1.pos[2::3]*pointSet1.freeflagspos[2::3]
                if(numpy.max(zcap)>0.0):
                    indexes = numpy.where(zcap>0)[0]
                    pointSet1.pos[indexes*3+2]-=pointSet1.pos[indexes*3+2] 
                    #printl("new cap z max",numpy.max(zcap))
                    
            rp = (pointSet1.pos-pointSet0.pos)
            d = numpy.dot(rp,nf)
            #printl("dot",d,magnitude(rp),"alpha",alpha)

            energy,grad = self.dual_lattice_minimiser.minimise_step_operations(pointSet1.pos,pointSet1)
            force = -1.0*grad

            count+=1
            
            if(abs(d)>abs(dold)):
                alpha*=2.0
            else:
                alpha/=2.0
            
            if(alpha<minalpha):alpha=minalpha
            if(alpha>maxalpha):alpha=maxalpha        
            #alpha*=2.0
        
        pointSet1.pos += 2.0*alpha*-1.0*normalise(pointSet1.force)
        
        if(self.dual_lattice_minimiser.structure.type==CAPPEDNANOTUBE):
            zcap = pointSet1.pos[2::3]*pointSet1.freeflagspos[2::3]
            if(numpy.max(zcap)>0.0):
                indexes = numpy.where(zcap>0)[0]
                pointSet1.pos[indexes*3+2]-=pointSet1.pos[indexes*3+2] 
        
        printl("out of basin",d,"displacement",magnitude((pointSet1.pos-pointSet0.pos)))
        pointSet.pos = copy.deepcopy(pointSet1.pos)
        
    
    def continue_search(self,pointSet,NExtra,NMaxExtra):
        self.search(pointSet, self.NUnique+NExtra, self.NMaxStructures+NMaxExtra)
    
    def start_search(self,pointSet,NStructures,NMaxStructures):
        
        self.NUnique = 0
        self.NTotal = 0
        
        self.search(pointSet, NStructures, NMaxStructures)
        
    def search(self,pointSet,NReqStructures,NMaxStructures):
        '''
        Uses globals.NStructures,globals.NMaxStructures
        '''    
        self.finished=False
        self.StopMin=0
        self.NReqStructures=NReqStructures
        self.NMaxStructures=NMaxStructures
        
        steptime = time.time()
        printh("Searching for minima",threading.current_thread(),"Required Structures",self.NReqStructures,
               "Max Structures",self.NMaxStructures)

        while(self.NUnique < self.NReqStructures and self.NTotal < self.NMaxStructures):
            if(self.StopMin==1): break
            
            self.status = "Performing structure search"
            
            stime = time.time()
            
            printh("Minimising, self.NUnique",self.NUnique,"NTotal", self.NTotal)
            
            self.dual_lattice_minimiser.minimise(pointSet,update=False)
            
            
            if(pointSet.final_energy<self.lowestEnergy):
                self.lowestEnergy = pointSet.final_energy
                self.lowestEnergyPos = numpy.copy(pointSet.pos)
                printl("Lowest energy thomson solution found")
            
            if(self.StopMin==1): break
            
            Unique = self.check_uniqueness(self.dual_lattice_minimiser.structure)
            
            if(Unique):
                printl("Unique Minima Found")
                printh("time for unique structure",time.time()-stime)
                
                self.uniqueMinima.append(copy.deepcopy(pointSet))
                self.unique_minima_count+=1
                self.NUnique+=1
                
                rings = None
                if(self.carbon_lattice_minimiser!=None):
                    
                    if(self.carbon_lattice_minimiser.structure.type==CAPPEDNANOTUBE):
                        self.carbon_lattice_minimiser.structure.update_caps()
                    
                    self.status = "Constructing carbon atoms"    
                    self.carbon_lattice_minimiser.structure.construct_carbon_lattice()
                    
                    if(self.calc_rings):
                        self.status = "Calculating carbon rings"    
                        self.carbon_lattice_minimiser.structure.calculate_rings()
                        #rings = self.carbon_lattice_minimiser.structure.ring_info['ringCount']
                        
                    carbon_lattice = self.carbon_lattice_minimiser.structure.carbon_lattice
                    
                    self.carbon_lattice_minimiser.minimise_scale(carbon_lattice)
                    self.carbon_lattice_minimiser.minimise(carbon_lattice)   
                    
                    self.uniqueMinimaCarbon.append(copy.deepcopy(carbon_lattice))
                                
                self.structure_log.add_structure(self.dual_lattice_minimiser.structure)
                if(self.callback!=None):self.callback()

            exit_status = self.check_stoping_criteria(self.NTotal)   
            
                        
            if(self.basin_climb):
                pre = copy.deepcopy(pointSet)
                self.start_basin_climb(pointSet)
                printl("basin hopping offset",magnitude(pre.pos - pointSet.pos))
                if(self.carbon_lattice_minimiser.structure.type==CAPPEDNANOTUBE):
                    self.carbon_lattice_minimiser.structure.update_caps()
            
            if(self.add_gaussians):
                printl("adding gaussian",self.gaussians_dropped)
                
                self.minimiser.modifyPES=True
                self.add_gaussian(pointSet)
                    
            self.lastMinimumEnergy = pointSet.final_energy   
            
            if(self.reset_per_iteration):        
                if(self.dual_lattice_minimiser.structure.type==CAPPEDNANOTUBE):
                    self.structure.reset()
                    pointSet = self.structure.dual_lattice_minimiser  
                    pointSet.final_energy = self.lastMinimumEnergy   
                else:
                    self.structure.reset()
                    pointSet = self.structure.dual_lattice_minimiser  
                    pointSet.final_energy = self.lastMinimumEnergy   
                    
            if(self.random_pertubation_per_iteration==True): 
                odir,alpha = self.random_tangential_pertubation(pointSet)

            self.NTotal+=1
        
        if(self.unique_minima_count>0):    
            self.select_minima_structure(self.unique_minima_count-1)

        self.structure_log.print_log()
        
        self.finished=True
        printl("End minima search, found ",self.NUnique,"structures in",time.time()-steptime)
 
                
                  
        
        
        
        
        
        
        