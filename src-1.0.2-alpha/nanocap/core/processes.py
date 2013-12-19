'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: July 20 2012
Copyright Marc Robinson 2013
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

Processor class which holds current instances 
of fullerens and nanotubes. These ops can be
threaded away from the GUI thread. 

Override renderUpdate to update positions etc

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
'''
import os,sys,math,copy,random,time,threading,Queue,ctypes

from nanocap.core.globals import *
import nanocap.core.globals as globals
from nanocap.core.util import *
import nanocap.objects.points as points
import nanocap.core.minimisation as minimisation
import nanocap.core.minimasearch as minimasearch
import nanocap.core.triangulation as triangulation
import nanocap.core.ringcalculator as ringcalculator 
import nanocap.core.structurelog as structurelog
import nanocap.core.config as config 
import nanocap.objects.nanotube as tube
import nanocap.objects.cappednanotube as cappednanotube
import nanocap.objects.cap as cap
import nanocap.objects.fullerene as fullerene
from nanocap.clib import clib_interface
clib = clib_interface.clib
#clib = ctypes.cdll.LoadLibrary(ROOTDIR+"/clib/clib.so") 

class Processor(object):
    '''
    Processing routines only. NO RENDER OR GUI OPS
    '''
    
    def __init__(self,config = None):
        
        
        if(config==None):
            self.config = config.Config()
        else:
            self.config = config
            
        self.minimiser = minimisation .dualLatticeMinimiser(self)
        self.minsearch = minimasearch.MinimaSearch(self,self.minimiser)
        self.carbonLatticeMinimiser = minimisation.carbonLatticeMinimiser(self,self.config.opts["CarbonForceField"])
        
        self.structureLog = {}
        self.structureLog["Fullerene"] = structurelog.StructureLog("Fullerene")
        self.structureLog["Nanotube"] = structurelog.StructureLog("Nanotube")
        
        self.ringCount = numpy.zeros(10,NPI)
    
    def setupCarbonLatticeMinimiser(self,FFID=None):
        if(FFID!=None):self.config.opts["CarbonForceField"] = FFID
        self.carbonLatticeMinimiser = minimisation.carbonLatticeMinimiser(self,self.config.opts["CarbonForceField"])
        
        
    
    def waitGUIlock(self):
        time.sleep(0.1)
        while(self.config.opts["GUIlock"]):
            printl("awaiting globals.GUIlock=False",self.config.opts["GUIlock"])
            time.sleep(0.1)
        printl("ending globals.GUIlock=False",self.config.opts["GUIlock"])    
        
    def addCurrentStructure(self):      
        printl("Adding current structure")      
        if(self.config.opts["GenType"]=="Fullerene"):
            self.structureLog["Fullerene"].addStructure(self.fullerene,
                                           rings = self.ringCount)
            
            self.structureLog["Fullerene"].print_log()
            self.structureLog["Fullerene"].write_log(folder=self.config.opts['Home'],filename="FullereneStructureLog.txt")
            
            self.waitGUIlock()
            self.outputSignal(signal="update_fullerene_structure_table()") 
            self.waitGUIlock()
            
        if(self.config.opts["GenType"]=="Nanotube"):
            self.structureLog["Nanotube"].addStructure(self.cappedNanotube,
                                                       rings = self.ringCount)
            
            self.structureLog["Nanotube"].print_log()
            
            self.structureLog["Nanotube"].write_log(folder=self.config.opts['Home'],filename="NanotubeStructureLog.txt")
                      
            self.waitGUIlock()
            self.outputSignal(signal="update_nanotube_structure_table()") 
            self.waitGUIlock()
        

    def updateStructureWindow(self):
        pass    
    
    def outputSignal(self,signal=None):
        pass
                              
    
    def selectStructure(self,ID,carbonMinimised=False,carbonConstrained=False):
        printh("selectStructure",ID,"carbonFull",carbonMinimised,"carbonConstrained",carbonConstrained)
        
        if(self.config.opts["GenType"]=="Fullerene"):
           self.fullerene = copy.deepcopy(self.structureLog["Fullerene"].structures[ID].fullerene) 
            
           #self.fullerene.thomsonPoints = copy.copy(self.structureLog["Fullerene"].structures[ID].dualLattice)
           self.config.opts["NFullereneCarbonAtoms"]=self.fullerene.carbonAtoms.npoints
           self.config.opts["NFullereneDualLatticePoints"]=self.fullerene.thomsonPoints.npoints
           
           if(carbonMinimised):
               try:
                   self.updateDualLattice(renderUpdate=False)
                   self.fullerene.carbonAtoms = copy.deepcopy(self.structureLog["Fullerene"].structures[ID].fullerene.carbonAtoms)
                   
                   if(carbonConstrained):
                       try:self.fullerene.carbonAtoms.pos = numpy.copy(self.fullerene.carbonAtoms.constrained_pos)
                       except:pass
                       
                   self.updateCarbonLattice()
               except:pass
           else:
               self.updateDualLattice()
               
           
            
               
        if(self.config.opts["GenType"]=="Nanotube"):
            structure = self.structureLog["Nanotube"].structures[ID]
            self.cappedNanotube = copy.deepcopy(structure.cappedNanotube)
            
            printl("selectstructure max Z", numpy.max(self.cappedNanotube.carbonAtoms.pos[2::3]))
            
            printl("checking y,z ", self.cappedNanotube.carbonAtoms.pos[1::3][0:2],
                   self.cappedNanotube.carbonAtoms.pos[2::3][0:2])
            #self.cap = copy.deepcopy(structure.cap)
             
            self.config.opts["NCapDualLatticePoints"]=self.cappedNanotube.cap.thomsonPoints.npoints
            self.config.opts["NTubeDualLatticePoints"]=self.cappedNanotube.nanotube.thomsonPoints.npoints
            self.config.opts["NTubeCarbonAtoms"]=self.cappedNanotube.nanotube.carbonAtoms.npoints
            self.config.opts["NCapCarbonAtoms"]=self.cappedNanotube.cap.thomsonPoints.npoints*2 - 2
            self.config.opts["NCappedTubeCarbonAtoms"]=self.cappedNanotube.carbonAtoms.npoints
            self.config.opts["NCappedTubeDualLatticePoints"]=self.cappedNanotube.thomsonPoints.npoints

            self.cappedNanotube.resetSecondaryCap()

            printh("received ","globals.NCapDualLatticePoints",self.config.opts["NCapDualLatticePoints"])
            printh("received ","globals.NTubeDualLatticePoints",self.config.opts["NTubeDualLatticePoints"])
            printh("received ","globals.NTubeCarbonAtoms",self.config.opts["NTubeCarbonAtoms"])
            printh("received ","globals.NCapCarbonAtoms",self.config.opts["NCapCarbonAtoms"])
            printh("received ","globals.NCappedTubeCarbonAtoms",self.config.opts["NCappedTubeCarbonAtoms"])
            printh("received ","globals.NCappedTubeDualLatticePoints",self.config.opts["NCappedTubeDualLatticePoints"])
            
            if(carbonMinimised): 
                try:
                    self.updateDualLattice(renderUpdate=False)
                    self.cappedNanotube.carbonAtoms = copy.deepcopy(structure.cappedNanotube.carbonAtoms)
                    if(carbonConstrained):
                       try:self.cappedNanotube.carbonAtoms.pos = numpy.copy(self.cappedNanotube.carbonAtoms.constrained_pos)
                       except:pass

                    self.updateCarbonLattice()
                    
                except:pass
            else:
                self.updateDualLattice()    
    
            printl("selectstructure max Z", numpy.max(self.cappedNanotube.carbonAtoms.pos[2::3]))    
            printl("checking y,z ", self.cappedNanotube.carbonAtoms.pos[1::3][0:2],
                   self.cappedNanotube.carbonAtoms.pos[2::3][0:2])
                
    def saveCurrentStructure(self,folder,recalculate=True,
                             dualLattice=True,carbonAtoms=True,carbonEnergy=False):
        if(recalculate):
            self.updateDualLattice()
            self.updateCarbonLattice()
            
        printl("saving current structure")    
        if(self.config.opts["GenType"]=="Nanotube"):
            self.cappedNanotube.calcInfo()
            folder += "/"+self.cappedNanotube.get_single_line_description(carbonAtoms=carbonAtoms,
                                                                          dualLattice=dualLattice,
                                                                          carbonEnergy=carbonEnergy)
            printl("making dir",folder)
            try:os.makedirs(folder)
            except:pass

            if(carbonAtoms):
                write_xyz(folder+"/atom_coords.xyz",self.cappedNanotube.carbonAtoms)
                try:write_xyz(folder+"/atom_coords.xyz",self.cappedNanotube.carbonAtoms,contstrained=True)
                except:pass            
            if(dualLattice):
                write_xyz(folder+"/thomson_coords.txt",self.cappedNanotube.thomsonPoints)

            f = open(folder+"/info.txt","w")
            f.write(self.cappedNanotube.__repr__())
            f.close() 

        else:
            self.fullerene.calcInfo()
            
            folder += "/"+self.fullerene.get_single_line_description(carbonAtoms=carbonAtoms,
                                                                          dualLattice=dualLattice,
                                                                          carbonEnergy=carbonEnergy)
            try:os.makedirs(folder)
            except:pass
            
            if(carbonAtoms):
                write_xyz(folder+"/atom_coords.xyz",self.fullerene.carbonAtoms)
                try:write_xyz(folder+"/atom_coords.xyz",self.fullerene.carbonAtoms,contstrained=True)
                except:pass            
            if(dualLattice):
                write_xyz(folder+"/thomson_coords.txt",self.fullerene.thomsonPoints)
                       
            f = open(folder+"/info.txt","w") 
            f.write(self.fullerene.__repr__())
            f.close()
            
        return folder
    
    def renderUpdate(self):
        '''
        this will be overriden by the gui if we are using the processor in the gui app
        to update the rendering of the points etc
        '''

    def resetCap(self,seed=None,ncap_dual_lattice_points = None):
        printl("resetting cap seed",seed)
        
        self.cappedNanotube.resetCap()

        if(ncap_dual_lattice_points!=None):
            self.config.opts["NCapDualLatticePoints"] = ncap_dual_lattice_points
        
        self.cappedNanotube.setupCap(self.config.opts["NCapDualLatticePoints"],seed=seed)
        self.cappedNanotube.resetSecondaryCap()
        self.cappedNanotube.construct()

        printl("globals.AutoNanotubeZCutoff",self.config.opts["AutoNanotubeZCutoff"])
        
        if(self.config.opts["AutoNanotubeZCutoff"]):
            self.cappedNanotube.setZcutoffFromCapPoints(self.config.opts["NCapDualLatticePoints"])
        else:
            self.cappedNanotube.setZcutoff(self.config.opts["NanotubeZCutoff"])

        
        printh("Reset cap dual lattice points",self.config.opts["NCapDualLatticePoints"],"seed",seed)
        printh("Total capped nanotube dual lattice points",self.cappedNanotube.thomsonPoints.npoints)
        
        self.config.opts["NCapCarbonAtoms"] = 2*self.config.opts["NCapDualLatticePoints"] - 2
        self.config.opts["NCappedTubeDualLatticePoints"] = self.cappedNanotube.thomsonPoints.npoints
        self.config.opts["NCappedTubeCarbonAtoms"] = 2*self.config.opts["NCapCarbonAtoms"] + self.config.opts["NTubeCarbonAtoms"]


    def estimateCapPoints(self,n,m):
        cappedNanotube = cappednanotube.CappedNanotube()
        estimate = cappedNanotube.getCapDualLatticeEstimate(n,m)
        self.config.opts["NCapDualLatticePoints"]  = estimate
        self.config.opts["NCapCarbonAtoms"] = self.config.opts["NCapDualLatticePoints"]*2 - 2
        
    
    def setMinimumNanotubeLength(self,n,m):
        cappedNanotube = cappednanotube.CappedNanotube()
        cappedNanotube.nanotube.setup_params(n,m)
        cappedNanotube.nanotube.setup_length()
        self.config.opts["NanotubeLength"] = cappedNanotube.nanotube.length
        
        
    def resetNanotube(self,n,m,l=None,capEstimate=True):
        self.cappedNanotube = cappednanotube.CappedNanotube()
        
        #self.cap = None        
        printl("resetting nanotube ",capEstimate,self.config.opts["NCapDualLatticePoints"],l)
        #self.nanotube = tube.nanotube()
        
        if(capEstimate):            
            estimate = self.cappedNanotube.getCapDualLatticeEstimate(n,m)
            printl("using capEstimate",estimate)
            self.config.opts["NCapDualLatticePoints"]  = estimate
            self.config.opts["NCapCarbonAtoms"] = estimate*2 - 2
                
        
        #self.nanotube.setup(n,m,l=l)
        self.cappedNanotube.setupNanotube(n,m,l=l)
        
        printl("globals.ShowTubeCarbonAtoms",self.config.opts["ShowTubeCarbonAtoms"])
        printl("globals.ShowTubeDualLatticePoints",self.config.opts["ShowTubeCarbonAtoms"])
        printl("globals.AutoNanotubeZCutoff",self.config.opts["AutoNanotubeZCutoff"])

        self.config.opts["NTubeCarbonAtoms"] = self.cappedNanotube.nanotube.Nc
        self.config.opts["NTubeDualLatticePoints"] = self.cappedNanotube.nanotube.Nd
        
        #printl("reset nanotube dual",self.config.opts["NTubeDualLatticePoints"],self.nanotube.Nc,
        #       self.nanotube.Nd,self.nanotube.n,self.nanotube.m,self.nanotube.u)
        
        printl("globals.NCapDualLatticePoints",self.config.opts["NCapDualLatticePoints"])

        if(self.config.opts["AutoNanotubeZCutoff"]):
            self.cappedNanotube.setZcutoffFromCapPoints(self.config.opts["NCapDualLatticePoints"])
        else:
            self.cappedNanotube.setZcutoff(self.config.opts["NanotubeZCutoff"])
            #self.nanotube.cutoff = self.config.opts["NanotubeZCutoff"]

        
    def resetFullereneDualLattice(self,inputpoints=None, seed=None):        
        #self.gui.vtkframe.VTKRenderer.RemoveAllViewProps()
        
        NTp = self.config.opts["NFullereneDualLatticePoints"]
        
        printl("NFullereneDualLatticePoints",NTp)
        
        try: minimum = self.knownMimimaCatalogue[int(NTp)] 
        except: minimum = 0
        
        #****move me to toolbar operations
        #try:self.gui.dock.currentToolbar().KnownMinimum.setText(str(minimum))
        #except:pass
        
        self.fullerene = fullerene.Fullerene()
        
        if(seed==None):seed = random.randint(1,100000) 
        
        nfix = self.config.opts["FullereneDualLatticeNFixedEquator"]
        rad = self.config.opts["FullereneDualLatticePointRadius"]
        col = self.config.opts["FullereneDualLatticePointColourRGB"]
        
        if(self.config.opts["FullereneDualLatticeFixPole"]):fixPole = True
        else:fixPole = False
            
        if(inputpoints==None):
            self.fullerene.setupThomsonPoints(NTp,rad,col,1.0,seed=seed,
                                              nfixequator=nfix,fixpole = fixPole)
        else:
            NTp = len(inputpoints)/3
            self.fullerene.setupThomsonPoints(NTp,rad,col,1.0,inputpoints=inputpoints,
                                 seed=seed,nfixequator=nfix,fixpole = fixPole)    
        
        printl("resetting", NTp,"Thomson points","fixPole",fixPole,"nfix",nfix,"rad",rad,"col",col)
        
        NNdist = self.fullerene.thomsonPoints.getNNdist()
        self.config.opts["GaussianWidth"] = NNdist*0.05
        
        printl("setting GaussianWidth",self.config.opts["GaussianWidth"])
        printh("Total fullerene dual lattice points",self.fullerene.thomsonPoints.npoints,"seed",seed)
    
    def minimaSearch(self):
        self.carbonLatticeMinimiser = minimisation.carbonLatticeMinimiser(self,self.config.opts["CarbonForceField"])
        if(self.config.opts["GenType"]=="Fullerene"):
            try:self.fullerene 
            except:return
            self.minsearch.search(self.fullerene.thomsonPoints)
                
        if(self.config.opts["GenType"]=="Nanotube"):
            try:self.cappedNanotube 
            except:return
            self.minsearch.search(self.cappedNanotube.thomsonPoints)

    
    def minimiseDualLattice(self):
        if(self.config.opts["GenType"]=="Fullerene"):
            try:self.fullerene 
            except:return
            self.minimiser.minimise(self.fullerene.thomsonPoints)
                
        if(self.config.opts["GenType"]=="Nanotube"):
            try:self.cappedNanotube 
            except:return
            self.minimiser.minimise(self.cappedNanotube.thomsonPoints)
        
        self.addCurrentStructure()
        #if(globals.CarbonMinimise):
            #self.minimiseCarbonAtoms()
                
                     
    def minimiseCarbonAtoms(self):
        self.carbonLatticeMinimiser = minimisation.carbonLatticeMinimiser(self,self.config.opts["CarbonForceField"])
        
        if(self.config.opts["GenType"]=="Fullerene"):
            try:self.fullerene 
            except:return
            self.carbonLatticeMinimiser.minimise_scale(self.fullerene.carbonAtoms)
            self.carbonLatticeMinimiser.minimise(self.fullerene.carbonAtoms)
            printl("scale ",self.fullerene.carbonAtoms.FinalScale,
               " edip_scaled_energy ",self.fullerene.carbonAtoms.FinalScaleEnergy,
               " edip_energy ",self.fullerene.carbonAtoms.FinalEnergy,
               " edip_energy_per_atom ",self.fullerene.carbonAtoms.FinalEnergy/self.fullerene.carbonAtoms.npoints)
            
        if(self.config.opts["GenType"]=="Nanotube"):
            try:self.cappedNanotube 
            except:return
            #printl(self.cappedNanotube.carbonAtoms.pos)
            self.carbonLatticeMinimiser.minimise_scale(self.cappedNanotube.carbonAtoms)
            #printl(self.cappedNanotube.carbonAtoms.pos)
            self.carbonLatticeMinimiser.minimise(self.cappedNanotube.carbonAtoms)
            printl("scale ",self.cappedNanotube.carbonAtoms.FinalScale,
               " edip_scaled_energy ",self.cappedNanotube.carbonAtoms.FinalScaleEnergy,
               " edip_energy ",self.cappedNanotube.carbonAtoms.FinalEnergy,
               " edip_energy_per_atom ",self.cappedNanotube.carbonAtoms.FinalEnergy/self.cappedNanotube.carbonAtoms.npoints)
            #self.carbonLatticeMinimiser.scale_and_minimise(self.cappedNanotube.carbonAtoms)
        
        self.addCurrentStructure()
        #self.updateCarbonLattice()
    
    def calculateRingStats(self):
        if not self.config.opts["CalcCarbonRings"]:
            return
        
        stime = time.time()
        
        printl("beginning ring calc")
        self.MaxNebs = 3
        self.MaxVerts = 9
        
        if(self.config.opts["GenType"]=="Fullerene"):
            outdict = self.fullerene.calculateCarbonRings(MaxNebs = self.MaxNebs,MaxVerts=self.MaxVerts)
            
        if(self.config.opts["GenType"]=="Nanotube"):
            outdict = self.cappedNanotube.calculateCarbonRings(MaxNebs = self.MaxNebs,MaxVerts=self.MaxVerts)
        
        for key, val in outdict.items():
            exec "self."+key+" = outdict[key]"

    def constructDualGraph(self,pointSet,centerflag="centroid"):
        stime = time.time()
        
        if(self.config.opts["GenType"]=="Fullerene"):
            if not self.config.opts["CalcFullereneCarbonAtoms"]:
                return
        if(self.config.opts["GenType"]=="Nanotube"):    
            if not self.config.opts["CalcCappedTubeCarbonAtoms"]:
                return
            
        if(self.ntriangles==None or self.verts==None):
            printl("Cannot construct dual graph points not triangulated")
            return
        
        Nc =  self.ntriangles 
        printl("constructing dual graph for ",self.ntriangles, "triangles")
        
        
        if(self.config.opts["GenType"]=="Fullerene"):
            if(self.fullerene.carbonAtoms!=None):
                self.fullerene.carbonAtoms.reset(Nc)
            else:    
                self.fullerene.carbonAtoms = points.Points("Fullerene Carbon Atoms")    
                self.fullerene.carbonAtoms.initArrays(Nc)
            carbonAtoms = self.fullerene.carbonAtoms
        
        if(self.config.opts["GenType"]=="Nanotube"):
            if(self.cappedNanotube.carbonAtoms!=None):
                self.cappedNanotube.carbonAtoms.reset(Nc)
            else:    
                self.cappedNanotube.carbonAtoms = points.Points("Capped Nanotube Carbon Atoms")    
                self.cappedNanotube.carbonAtoms.initArrays(Nc)
            carbonAtoms = self.cappedNanotube.carbonAtoms
            
            try:self.cappedNanotube.cap
            except:
                self.cappedNanotube.carbonAtoms = self.cappedNanotube.nanotube.carbonAtoms
                return
            if(self.cappedNanotube.cap==None):
                self.cappedNanotube.carbonAtoms = self.cappedNanotube.nanotube.carbonAtoms
                return

        v1x = pointSet.pos[self.verts[0::3]*3]
        v1y = pointSet.pos[self.verts[0::3]*3+1]    
        v1z = pointSet.pos[self.verts[0::3]*3+2]   
        
        v2x = pointSet.pos[self.verts[1::3]*3]
        v2y = pointSet.pos[self.verts[1::3]*3+1]    
        v2z = pointSet.pos[self.verts[1::3]*3+2]   
        
        v3x = pointSet.pos[self.verts[2::3]*3]
        v3y = pointSet.pos[self.verts[2::3]*3+1]    
        v3z = pointSet.pos[self.verts[2::3]*3+2]    
        
        cx = (v1x+v2x+v3x)/3.0
        cy = (v1y+v2y+v3y)/3.0
        cz = (v1z+v2z+v3z)/3.0
         
        carbonAtoms.pos[0::3] = cx 
        carbonAtoms.pos[1::3] = cy 
        carbonAtoms.pos[2::3] = cz  
            
        if(self.config.opts["GenType"]=="Nanotube"):
            length=self.cappedNanotube.nanotube.thomsonPointsCOM[2]*2 
        else:
            length=None
        clib_interface.scale_points_to_rad(carbonAtoms.npoints,carbonAtoms.pos,1.0,length=length)
        
        printl("finished constructing dual graph for ",self.ntriangles, "triangles")
        printh("N triangulated carbon atoms",carbonAtoms.npoints)
        printh("time for dual lattice construction",time.time()-stime)
    
    def calculateSchlegel(self,carbonAtoms=None):
        stime = time.time()
        printl("calculateSchlegel")
        
        if(self.config.opts["GenType"]=="Fullerene"):
            pointSet = self.fullerene.thomsonPoints
            if(carbonAtoms==None):carbonAtoms = self.fullerene.carbonAtoms

            
        if(self.config.opts["GenType"]=="Nanotube"):
            pointSet = self.cappedNanotube.thomsonPoints
            if(carbonAtoms==None):carbonAtoms = self.cappedNanotube.carbonAtoms
        
        try:
            self.schlegelThomsonPoints.reset(pointSet.npoints)
        except:
            self.schlegelThomsonPoints = points.Points("Schlegel Dual Lattice Points")
            self.schlegelThomsonPoints.initArrays(pointSet.npoints)
        
        self.schlegelThomsonPoints.pos = numpy.copy(pointSet.pos)
        z = self.schlegelThomsonPoints.pos[2::3]
        todelete  = numpy.where(z>self.config.opts["SchlegelCutoff"])[0]
        zmax,zmin = numpy.max(z),numpy.min(z)
      
        self.schlegelThomsonPoints.pos[2::3]-=zmin

        self.schlegelThomsonPoints.removeIndexes(todelete)
        self.schlegelProjection(self.schlegelThomsonPoints.pos,
                                self.config.opts["SchlegelGamma"])

        
        #self.schlegelThomsonPoints.update() 


        try:
            self.schlegelCarbonAtoms.reset(carbonAtoms.npoints)
        except:
            self.schlegelCarbonAtoms = points.Points("Schlegel Carbon Atoms")
            self.schlegelCarbonAtoms.initArrays(carbonAtoms.npoints)
        
        self.schlegelCarbonAtoms.pos = numpy.copy(carbonAtoms.pos)
        z = self.schlegelCarbonAtoms.pos[2::3]
        todelete  = numpy.where(z>self.config.opts["SchlegelCutoff"])[0]

        self.schlegelCarbonAtoms.pos[2::3]-=zmin
        self.schlegelProjection(self.schlegelCarbonAtoms.pos,
                                   self.config.opts["SchlegelGamma"])
        
        self.schlegelCarbonLattice = copy.deepcopy(self.schlegelCarbonAtoms)
        self.schlegelCarbonAtoms.removeIndexes(todelete)
        #self.schlegelCarbonAtoms.update() 
        
        if(self.config.opts["GenType"]=="Nanotube"):
            #add tubeThomsonPoints to show boundary

        
            try:
                self.schlegelTubeThomsonPoints.reset(self.cappedNanotube.nanotube.thomsonPoints.npoints)
            except:
                self.schlegelTubeThomsonPoints = points.Points("Schlegel Tube Dual Lattice Points")
                self.schlegelTubeThomsonPoints.initArrays(self.cappedNanotube.nanotube.thomsonPoints.npoints)
            
            self.schlegelTubeThomsonPoints.pos = numpy.copy(self.cappedNanotube.nanotube.thomsonPoints.pos)
            
            z = self.schlegelTubeThomsonPoints.pos[2::3]
            todelete  = numpy.where(z>self.config.opts["SchlegelCutoff"])[0]         
            self.schlegelTubeThomsonPoints.pos[2::3]-=zmin                 
            self.schlegelTubeThomsonPoints.removeIndexes(todelete)
            
            self.schlegelProjection(self.schlegelTubeThomsonPoints.pos,
                                               self.config.opts["SchlegelGamma"])

            #self.schlegelTubeThomsonPoints.update() 

        if not self.config.opts["CalcCarbonRings"]:return
        
        
        self.schlegelMaxVerts = self.MaxVerts
        self.schlegelRings = numpy.copy(self.Rings)
        self.schlegelVertsPerRingCount = numpy.copy(self.VertsPerRingCount)
        for i in range(0,self.nrings):
            for j in range(0,self.VertsPerRingCount[i]):
                index = self.Rings[i*self.MaxVerts + j]
                if(carbonAtoms.pos[index*3+2]>self.config.opts["SchlegelCutoff"]):
                    self.schlegelVertsPerRingCount[i] =0 
                    break    
        
        printh("time for Schlegel calc",time.time()-stime)
    
    def schlegelProjection(self,pos,gamma):
        x = pos[0::3]
        y = pos[1::3]
        z = pos[2::3]
        x2 = x*x
        y2 = y*y
        zoff = gamma*numpy.fabs(z)
        m = numpy.sqrt(x2 + y2)
        axisp = numpy.where(m<1e-10)[0]
        printl(axisp)
        m[axisp]=1e-10
        pos[0::3] += zoff*x/m 
        pos[1::3] += zoff*y/m 
        pos[2::3]  = 0    

    def calculateCarbonBonds(self,pointSet):
        if not self.config.opts["CalcCarbonBonds"]:return

        if(self.config.opts["GenType"]=="Fullerene"):
            if(self.fullerene.carbonAtoms==None):
                printl("Cannot construct bonds carbon atoms not calculated")
                return
        if(self.config.opts["GenType"]=="Nanotube"):
            if(self.cappedNanotube.carbonAtoms==None):
                printl("Cannot construct bonds carbon atoms not calculated")
                return
                
        printl("building bonds for",pointSet.npoints," atoms")
        
        maxbonds = 10
        AvBondLength = numpy.zeros(pointSet.npoints,NPF)
        clib.get_average_bond_length(ctypes.c_int(pointSet.npoints),
                                     pointSet.pos.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                                     AvBondLength.ctypes.data_as(ctypes.POINTER(ctypes.c_double)))
          
        cutoff  = numpy.average(AvBondLength)*1.2
        mybonds = numpy.zeros(pointSet.npoints*6*maxbonds, NPF)

        clib.calc_carbon_bonds.restype = ctypes.c_int
        nbonds=clib.calc_carbon_bonds(ctypes.c_int(pointSet.npoints),
                                            pointSet.pos.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                                            mybonds.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                                            ctypes.c_double(cutoff))
        
        self.nbonds =   nbonds
        self.bonds =   mybonds           
        printl("nbonds",nbonds,"cutoff",cutoff)
        printl("finished calculating bonds")

        
    def triangulatePointset(self,pointSet):
        stime = time.time()
        printl("beginning Delauny Triangulation",self.config.opts["CalcTriangulation"],self.config.opts["ShowTriangulation"])
        if not self.config.opts["CalcTriangulation"]:
            return
        
        self.verts, self.ntriangles =  triangulation.delaunyTriangulation(pointSet)
        self.verts = self.verts[0:self.ntriangles*3]
        self.ntriangles

        printh("time for triangluation",time.time()-stime,"ntriangles",self.ntriangles)
    
    def updateDualLattice(self,renderUpdate=True):
        printl("updating dual lattice","renderUpdate=",renderUpdate)
        if(self.config.opts["GenType"]=="Fullerene"):
            dualLattice = self.fullerene.thomsonPoints 
            
        if(self.config.opts["GenType"]=="Nanotube"):    
            dualLattice = self.cappedNanotube.thomsonPoints
            printl("CappedNanotubeTubeDualLatticePoints arrays",
                   self.cappedNanotube.thomsonPoints.pos[0:10],
                   self.cappedNanotube.cap.thomsonPoints.pos[0:10])
            self.cappedNanotube.updateCaps()
        
        if(self.config.opts["CalcTriangulation"]):
            self.triangulatePointset(dualLattice)
        else:
            if(renderUpdate):
               printl("processor updating renderer")
               self.renderUpdate()
            return
        
        if((self.config.opts["GenType"]=="Fullerene" and self.config.opts["CalcFullereneCarbonAtoms"])):
            self.constructDualGraph(dualLattice)
            carbonAtoms = self.fullerene.carbonAtoms
            
        elif((self.config.opts["GenType"]=="Nanotube" and self.config.opts["CalcCappedTubeCarbonAtoms"])):
            self.constructDualGraph(dualLattice) 
            carbonAtoms = self.cappedNanotube.carbonAtoms   
        else:
            if(renderUpdate):
               printl("processor updating renderer")
               self.renderUpdate()    
        
        if(self.config.opts["CalcCarbonBonds"]):
            if(self.config.opts["GenType"]=="Fullerene"):self.calculateCarbonBonds(carbonAtoms)
            if(self.config.opts["GenType"]=="Nanotube"):self.calculateCarbonBonds(carbonAtoms)
        
        if(self.config.opts["CalcCarbonRings"]):self.calculateRingStats()
        if(self.config.opts["CalcSchlegel"]):self.calculateSchlegel()
        
        if(renderUpdate):
           printl("processor updating renderer")
           self.renderUpdate()
            
    def updateCarbonLattice(self,renderUpdate=True):
       if(self.config.opts["GenType"]=="Fullerene"):
           self.fullerene.calcInfo()
       if(self.config.opts["CalcCarbonBonds"]):
           if(self.config.opts["GenType"]=="Fullerene"):
               self.calculateCarbonBonds(self.fullerene.carbonAtoms)
           if(self.config.opts["GenType"]=="Nanotube"):
               self.calculateCarbonBonds(self.cappedNanotube.carbonAtoms)
       if(self.config.opts["CalcCarbonRings"]):self.calculateRingStats()     
        
       if(renderUpdate):
           self.renderUpdate()

        
        