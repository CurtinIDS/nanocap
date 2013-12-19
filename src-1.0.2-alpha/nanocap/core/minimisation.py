'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: July 22 2012
Copyright Marc Robinson 2013
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

Minimisation of pointSets using a passed
Force Field ID.

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
'''

from nanocap.core.globals import *
import nanocap.core.globals as globals
import os,sys,math,copy,random,time,threading,Queue,ctypes

import numpy

from scipy.optimize import fmin_l_bfgs_b,fmin

import nanocap.core.forcefield as forcefield
from nanocap.core.util import * 
from nanocap.clib import clib_interface
clib = clib_interface.clib


class Minimiser(object):
    '''
    Parent class for both dual lattice and carbon lattice
    minimisation.
    
    minimise - minimse internal coords
    minimise_scale - scale internal coords by factor gamma
        
    '''
    def __init__(self,processor,FFID):
        self.processor = processor
        self.config = self.processor.config
        self.FFID = FFID
        try:self.FF = forcefield.FFS[FFID]
        except:
            printl(FFID,"not yet implemented")
        self.updateFlag = True
        self.modifyPES = False
        
    def minimise(self,pointSet,update=True):  
        if not self.FF.analytical_force: 
            printl("cannot minimiser with ffield:",self.FF.ID,"as does not return analyical force, will return")
            pointSet.FinalEnergy = 0.0
            pointSet.unconstrained_pos = numpy.copy(pointSet.pos)
            self.FinalEnergy = 0.0
            self.unconstrained_pos = pointSet.unconstrained_pos
        
            return 
        stime = time.time()
        
        self.updateFlag=update
        printh("Minimising:",pointSet,"with:",self.config.opts["MinType"],"minimiser and ffield:",self.FF.ID)
        
        self.setup_force_field(pointSet)
        self.minimise_pointSet(pointSet)
        self.final_operations(pointSet)
        
        printh("time for minimisation",time.time()-stime)
        
    def final_operations(self,pointSet):
        '''
        reimplement for any final ops post minimisation
        '''
        pass
#    def minima_search(self,pointSet):
#        pass
        
    def minimise_pointSet(self,pointSet):        
        if(self.config.opts["MinType"]=="LBFGS"):
            self.minimise_lbfgs_python(pointSet)    
        if(self.config.opts["MinType"]=="SD"):
            self.minimise_sd(pointSet)   

             
        pointSet.FinalEnergy = numpy.sum(pointSet.energy)
        pointSet.unconstrained_pos = numpy.copy(pointSet.pos)
        self.FinalEnergy = pointSet.FinalEnergy
        self.unconstrained_pos = pointSet.unconstrained_pos
        printl("FinalEnergy",self.FinalEnergy)
        
    def minimise_scale(self,pointSet):        
        printh("Minimising Scale:",pointSet,"with fmin minimiser and force field:",self.FF.ID)

        self.setup_force_field(pointSet)
        
        initial_gamma = self.get_initial_scale(pointSet)

        printl("initial_gamma",initial_gamma)
        
        gamma = fmin(self.minimise_scale_step_operations, initial_gamma, 
                     args=(pointSet,),
                     xtol=0.0001, ftol=0.0001,full_output=0)

        final_energy = self.minimise_scale_step_operations(gamma,pointSet)
        self.apply_scale(gamma,pointSet)
        
        pointSet.FinalScale = gamma[0]
        pointSet.FinalScaleEnergy = numpy.sum(pointSet.energy)
        pointSet.constrained_pos = numpy.copy(pointSet.pos) 
        
        
        
        self.FinalScale = pointSet.FinalScale
        self.FinalScaleEnergy = pointSet.FinalScaleEnergy
        self.constrained_pos = pointSet.constrained_pos
        
        printl("FinalScale", self.FinalScale, "FinalScaleEnergy",self.FinalScaleEnergy)
    
    def get_initial_scale(self,pointSet):
        return [1.0,]
          
    def setup_force_field(self):
        printl("Please reimplement setup_force_field")    

    def minimise_step_operations(self,pos,pointSet):
        
        self.pre_force_call_operations(pos,pointSet)
        pointSet.pos = pos
        
        energy,force = self.FF.get_energy(pointSet) 
        

        self.post_force_call_operations(pos,pointSet)
        pointSet.pos = pos
        
        if(self.modifyPES):
            energy,force = self.modify_PES(pos,pointSet)
        else:
            energy,force =  numpy.sum(pointSet.energy),pointSet.force
        
        

        
        grad = -1.0*force
        
        #printl("energy",energy,magnitude(grad))
        return energy,grad
    
    def modify_PES(self,pos,pointSet):
        '''
        will be overriden by minimaSearch to add gaussians 
        ''' 
        energy,force = 0,[0,0]
        return energy,force
        
    
    def apply_scale(self,scale,pointSet):
        '''
        reimplement to apply the scale transform
        '''   
        pass
    
    def minimise_scale_step_operations(self,gamma,pointSet):     
          
        pos0 = numpy.copy(pointSet.pos)
        
        self.pre_scale_force_call_operations(gamma,pointSet)
        
        self.apply_scale(gamma,pointSet)
                
        energy,force = self.FF.get_energy(pointSet)
        
        pointSet.force = force
        pointSet.pos = pos0
        self.previousGamma = gamma[0]
        
        self.post_scale_force_call_operations(gamma,pointSet)
        
        return energy
    
    def pre_scale_force_call_operations(self,gamma,pointSet):    
        '''
        reimplement for any ops before the scale force call
        '''   
        pass
    
    def post_scale_force_call_operations(self,gamma,pointSet):       
        '''
        reimplement for any ops after the scale force call
        '''    
        pass
    
    def pre_force_call_operations(self,pos,pointSet):    
        '''
        reimplement for any ops before the force call
        '''   
        pass
    
    def post_force_call_operations(self,pos,pointSet):       
        '''
        reimplement for any ops after the force call
        '''    
        pass
    
    def update_output(self,renderUpdate=True):
        '''
        reimplement for any render updates per globals.RenderUpdate
        '''
    
    def minimise_sd(self,pointSet):
        steps,echange = 0,10000000
        ienergy,iforce = self.FF.get_energy(pointSet)
        oldenergy = ienergy
        printl("initial energy, force",ienergy,magnitude(iforce))
        
        force = iforce
        while(steps < self.config.opts["MinSteps"] and self.config.opts["StopMin"]==0 and echange> self.config.opts["MinTol"]):
            
            energy, grad = self.minimise_step_operations(pointSet.pos,pointSet)
            
            step = 0.01/numpy.max(numpy.abs(grad))
            
            pointSet.pos = self.line_min(pointSet.pos,pointSet,grad,step,1e-5)
            
            fenergy,fforce = self.FF.get_energy(pointSet)
            
            self.post_force_call_operations(pointSet.pos, pointSet)
            
            echange = numpy.abs(oldenergy - fenergy)
            oldenergy = fenergy          
            pointSet.final_energy = fenergy
            
            if(steps>0 and steps % self.config.opts["RenderUpdate"] ==0):
                if(self.updateFlag):self.update_output(pointSet)
                printl("step",steps,"energy",fenergy,"echange",echange,"difference from known minimum",fenergy-self.config.opts["KnownMinimum"])
            steps+=1 
        
        if(self.updateFlag):self.update_output(pointSet)  
    
    def line_min(self,pos,pointSet,direction, step, tol):
        a_pos,b_pos,c_pos = numpy.copy(pos),numpy.copy(pos),numpy.copy(pos)
        energy, grad = self.minimise_step_operations(pointSet.pos,pointSet)
        '''
        bracket minimum along direction
        '''  
        a,b = 0,step
        dfa = numpy.dot(-grad, direction)
        
        b_pos += direction * b * pointSet.freeflagspos
        b_energy,b_grad = self.minimise_step_operations(b_pos,pointSet) 
        dfb = numpy.dot(-b_grad, direction)
        
        while(dfa*dfb >0):
            bold = b
            b = ((dfa*b - dfb*a) / (dfa - dfb))*1.5
            a = bold
            dfa=dfb
            b_pos = pos + (direction * b * pointSet.freeflagspos)
            b_energy,b_grad = self.minimise_step_operations(b_pos,pointSet) 
            dfb = numpy.dot(-b_grad, direction)
        
        '''
        find root of force
        '''            
        loopcount=0
        dfc = tol+1
        while(abs(dfc) > tol and loopcount < 50):
            c = b - ((b-a)/(dfb - dfa))*dfb
            c_pos = pos + (direction * c * pointSet.freeflagspos)
            c_energy,c_grad = self.minimise_step_operations(c_pos,pointSet) 
            dfc = numpy.dot(-c_grad, direction)
            a = b
            dfa = dfb
            b = c
            dfb = dfc
            loopcount+=1
        
        c_pos = pos + (direction * c * pointSet.freeflagspos)    
        printd("post force z",c_pos[numpy.arange(2,len(pos),3)])    
        return c_pos
    
    def minimise_lbfgs_python(self,pointSet):
        steps,echange = 0,10000000
        ienergy,iforce = self.FF.get_energy(pointSet)
        oldenergy = ienergy
        printl("initial energy, force",ienergy,magnitude(iforce))
        
        printl("N minimise steps",self.config.opts["MinSteps"],
               "stop min",self.config.opts["StopMin"],
               "tolerance",self.config.opts["MinTol"])
        
        while(steps < self.config.opts["MinSteps"] and self.config.opts["StopMin"]==0 and echange> self.config.opts["MinTol"]):
            bounds = None
#            bounds=[]
#            for i in range(0,len(pointSet.freeflagspos)):
#                bounds.append((None,None))
                
                
            startt = time.time()
            
            pointSet.pos, final_energy, d = fmin_l_bfgs_b(self.minimise_step_operations, 
                                                          pointSet.pos, 
                                                          args = (pointSet,),
                                                          #fprime = self.get_force,
                                                          approx_grad = 0, 
                                                          bounds = bounds, 
                                                          m = 100, 
                                                          factr = 10.0, 
                                                          pgtol = self.config.opts["MinTol"], 
                                                          iprint = -1, maxfun = 150000)
            
            printl("time for lbfgs",time.time()-startt,"steps",steps)
            printl("fmin_l_bfgs_b:" , d['task'],d['funcalls'],magnitude(d['grad']))

            fenergy,fforce = self.FF.get_energy(pointSet)
            
            self.post_force_call_operations(pointSet.pos, pointSet)

            echange = numpy.abs(oldenergy - fenergy)
            oldenergy = final_energy            
            pointSet.final_energy = fenergy
            
            if(steps>0 and steps % self.config.opts["RenderUpdate"] ==0):
                if(self.updateFlag):self.update_output(pointSet)
                #self.processor.updateDualLattice()
                printl("step",steps,"energy",fenergy,"echange",echange,"difference from known minimum",fenergy-self.config.opts["KnownMinimum"])
            steps+=1 
        
        if(self.updateFlag):self.update_output(pointSet)    
        #self.processor.updateDualLattice()
    
 
        
class dualLatticeMinimiser(Minimiser):
    def __init__(self,processor):
        Minimiser.__init__(self,processor,"Thomson")
        self.req_radius=1.0
        
    def setup_force_field(self,pointSet):
        self.FF.setup(pointSet)
        if(self.config.opts["GenType"]=="Nanotube"):
            '''set the z-cutoff for thomson potential the nanotube '''
            self.FF.set_cutoff(self.processor.cappedNanotube.nanotube.cutoff)
            
            #if(self.FF.ID=="Thomson"):
            #    self.FF.args[2] = self.processor.cappedNanotube.nanotube.cutoff
    
#    def final_operations(self,pointSet):
#        if(globals.CarbonMinimise and self.updateFlag):
#            self.processor.minimiseCarbonAtoms()
    
    def update_output(self,pointSet,renderUpdate=True):
        printl("updating output")
        self.processor.updateDualLattice(renderUpdate=renderUpdate)
            
    def pre_force_call_operations(self,pos,pointSet):       
        if(self.config.opts["GenType"]=="Nanotube"):
            length=self.processor.cappedNanotube.nanotube.thomsonPointsCOM[2]*2 
        else:
            length=None
        clib_interface.scale_points_to_rad(pointSet.npoints,pos,self.req_radius,length=length)          
        
    
    def post_force_call_operations(self,pos,pointSet): 
        #raw_input("...")
        if(self.config.opts["GenType"]=="Nanotube"):
            #if cap atoms enter the tube add force... 
            k=1e4
            forcefield.force_on_cap_atoms_in_tube(self.config.opts["NCapDualLatticePoints"],
                                                       pos,
                                                       pointSet.force,
                                                       pointSet.energy,
                                                       k)

        forcefield.remove_radial_component_of_force(pointSet.npoints,
                                                         pos,
                                                         pointSet.force
                                                         )    
        pointSet.force*=pointSet.freeflagspos 

class carbonLatticeMinimiser(Minimiser):
    def __init__(self,processor, FFID):
        Minimiser.__init__(self,processor,FFID)

    def setup_force_field(self,pointSet):
        self.FF.setup(pointSet)
#        bounds = pointSet.getBounds()
#        self.FF.args[0] = (bounds[3]-bounds[0])*2000.0
#        self.FF.args[1] = (bounds[4]-bounds[1])*2000.0
#        self.FF.args[2] = (bounds[5]-bounds[2])*2000.0
#        printl("end setup_force_field")
    
    def update_output(self,pointSet,renderUpdate=False):
        #pointSet.update()  
        self.processor.updateCarbonLattice(renderUpdate=renderUpdate)
    
#    def pre_force_call_operations(self,pos,pointSet):  
#        printl("pre force call")
#        self.setup_force_field(pointSet)
    
    
    def apply_scale(self,gamma,pointSet):
        if(self.config.opts["GenType"]=="Nanotube"):
            length=self.processor.cappedNanotube.nanotube.thomsonPointsCOM[2]*2.0
        else:
            length=None
        
        clib_interface.scale_points_to_rad(pointSet.npoints,pointSet.pos,float(gamma[0]),length=length) 
        
    
    def get_initial_scale(self,pointSet):
        gamma = numpy.zeros(1,NPF)
        gamma[0] = math.sqrt( float(pointSet.npoints) * 0.22)
    
        printl("initial scale",gamma[0])
        while(math.fabs(self.minimise_scale_step_operations(gamma,pointSet))<50):
            gamma[0]*=0.95
        
        return gamma              