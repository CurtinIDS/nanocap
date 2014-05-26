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
import os,sys,math,copy,random,time,threading,Queue,ctypes

import numpy

from scipy.optimize import fmin_l_bfgs_b,fmin

import nanocap.core.forcefield as forcefield
from nanocap.core.points import Points
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
    def __init__(self,FFID=None,structure=None,callback=None,
                 min_type="LBFGS",ftol=1e-10,min_steps=100,render_update_freq=1):
        self.FFID = FFID
        self.structure = structure
         
        try:self.FF = forcefield.FFS[FFID]
        except:
            printl(FFID,"not yet implemented")
            self.FF = forcefield.ForceField("Temp")
            self.FF = forcefield.NullForceField()
            
        self.updateFlag = True
        self.callback=callback
        self.modifyPES = False
        self.render_update_freq= render_update_freq
        
        self.ftol=ftol
        self.min_steps=min_steps
        self.min_type=min_type
        
        self.runSimplexWhenNoAnalyticalForce = False
        
        self.currentPointSet = Points("Default Points")
        
    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        return result

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        return result
    
    
    def __repr__(self):
        s = "Optimising: {} with: {} minimiser and forcefield: {}".format(self.currentPointSet.PointSetLabel,
                                                                          self.min_type,
                                                                          self.FF.ID)
        return s
        
        
    def minimise(self,pointSet,update=True,callback=None,min_type=None,
                 ftol=None,min_steps=None):  
        '''
        callback routine called every step and at the end of minimisation
        '''
        self.currentPointSet = pointSet
        pointSet.FF  = self.FF.ID
        
        if(callback!=None):self.callback=callback
        if(ftol!=None):self.ftol=ftol
        if(min_steps!=None):self.min_steps=min_steps
        if(min_type!=None):self.min_type=min_type
        
        
        if self.FF.ID=="NULL":
            pointSet.final_energy = 0.0
            pointSet.unconstrained_pos = numpy.copy(pointSet.pos)
            pointSet.constrained_pos = numpy.copy(pointSet.pos)
            pointSet.final_scale = 0.
            pointSet.final_scaled_energy = 0.0
            return
        
        printl("min_type",min_type,"SIMPLEX")
        
        if (self.min_type!="SIMPLEX"):
            if not self.FF.analytical_force:             
                if(self.runSimplexWhenNoAnalyticalForce):
                    self.min_type = "SIMPLEX"
                else:
                    printl("will not minimise with ffield:",self.FF.ID,"as does not return analytical force, will return")
                    pointSet.final_energy = 0.0
                    pointSet.unconstrained_pos = numpy.copy(pointSet.pos)
                    self.final_energy = 0.0
                    self.unconstrained_pos = pointSet.unconstrained_pos
                
                return 
        
        stime = time.time()
        
        self.updateFlag=update
        
        self.stopmin = 0
        
        printh("Minimising:",pointSet,"with:",min_type,"minimiser and ffield:",self.FF.ID)
        self.setup_force_field(pointSet)
        self.minimise_pointSet(pointSet)
        self.final_operations(pointSet)
        
        #if not self.FF.analytical_force: self.config.opts["MinType"] = iniMinType
        
        printh("energy",numpy.sum(pointSet.energy),"magnitude force",magnitude(pointSet.force))
        printh("time for minimisation",time.time()-stime)
        
    def final_operations(self,pointSet):
        '''
        reimplement for any final ops post minimisation
        '''
        pass
#    def minima_search(self,pointSet):
#        pass
        
    def minimise_pointSet(self,pointSet):       
        if self.FF.ID=="NULL":return 

        if(self.min_type=="LBFGS"):
            self.minimise_lbfgs_python(pointSet)    
        if(self.min_type=="SD"):
            self.minimise_sd(pointSet)   
        if(self.min_type=="SIMPLEX"):
            self.minimise_simplex_python(pointSet) 
         
        pointSet.final_energy = numpy.sum(pointSet.energy)
        pointSet.unconstrained_pos = numpy.copy(pointSet.pos)
        self.final_energy = pointSet.final_energy
        self.unconstrained_pos = pointSet.unconstrained_pos
        printl("final_energy",self.final_energy)
        
    def minimise_scale(self,pointSet,ftol=1e-5):        
        printh("Minimising Scale:",pointSet,"with fmin minimiser and force field:",self.FF.ID)
        
        pointSet.FF  = self.FF.ID
        self.currentPointSet = pointSet
        
        if self.FF.ID=="NULL":return
        
        self.setup_force_field(pointSet)
        
        initial_gamma = self.get_initial_scale(pointSet)

        printl("initial_gamma",initial_gamma)
        
        gamma = fmin(self.minimise_scale_step_operations, initial_gamma, 
                     args=(pointSet,),
                     xtol=0.0001, ftol=ftol,full_output=0)

        final_energy = self.minimise_scale_step_operations(gamma,pointSet)
        self.apply_scale(gamma,pointSet)
        
        pointSet.final_scale = gamma[0]
        pointSet.final_scaled_energy = numpy.sum(pointSet.energy)
        pointSet.constrained_pos = numpy.copy(pointSet.pos) 
        
        
        
        self.final_scale = pointSet.final_scale
        self.final_scaled_energy = pointSet.final_scaled_energy
        self.constrained_pos = pointSet.constrained_pos
        
        printl("final_scale", self.final_scale, "final_scaleEnergy",self.final_scaled_energy)
        self.final_operations(pointSet)
    
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
    
    def minimise_step_operations_no_force(self,pos,pointSet):
        
        energy,grad = self.minimise_step_operations(pos,pointSet)
        
        return energy
        
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
    
    def minimise_simplex_python(self,pointSet):
        steps,echange = 0,10000000
        ienergy,iforce = self.FF.get_energy(pointSet)
        oldenergy = ienergy
        while(steps < self.min_steps  and echange > self.ftol and self.stopmin==0):            
            
            pointSet.pos, final_energy, iters, funceval, errorflags = fmin(self.minimise_step_operations_no_force, 
                                                          pointSet.pos, 
                                                          args = (pointSet,),
                                                          xtol=self.ftol*1000,
                                                          ftol=self.ftol*1000, 
                                                          full_output=True,
                                                          maxiter=10000,
                                                          maxfun=10000,
                                                          #callback = self.simplex_callback
                                                          )
            fenergy,fforce = self.FF.get_energy(pointSet)
            
            self.post_force_call_operations(pointSet.pos, pointSet)

            echange = numpy.abs(oldenergy - fenergy)
            oldenergy = final_energy            
            pointSet.final_energy = fenergy
            
            if(steps>0 and steps % self.render_update_freq == 0):
                if(self.callback):self.callback()
                printl("step",steps,"energy",fenergy,"echange",echange)
            printl("step",steps,"energy",fenergy,"echange",echange)
            steps+=1 
            
        
        if(self.updateFlag):self.update_output(pointSet)    
        
    def minimise_lbfgs_python(self,pointSet):
        steps,echange = 0,10000000
        ienergy,iforce = self.FF.get_energy(pointSet)
        oldenergy = ienergy
        printl("initial energy, force",ienergy,magnitude(iforce))
        
        while(steps < self.min_steps  and echange > self.ftol and self.stopmin==0):

            bounds = None

   
            startt = time.time()
            
            pointSet.pos, final_energy, d = fmin_l_bfgs_b(self.minimise_step_operations, 
                                                          pointSet.pos, 
                                                          args = (pointSet,),
                                                          #fprime = self.get_force,
                                                          approx_grad = 0, 
                                                          bounds = bounds, 
                                                          m = 100, 
                                                          factr = 10.0, 
                                                          pgtol = self.ftol, 
                                                          iprint = -1, maxfun = 150000)
            
            printl("time for lbfgs",time.time()-startt,"steps",steps)
            printl("fmin_l_bfgs_b:" , d['task'],d['funcalls'],magnitude(d['grad']))

            fenergy,fforce = self.FF.get_energy(pointSet)
            
            self.post_force_call_operations(pointSet.pos, pointSet)

            echange = numpy.abs(oldenergy - fenergy)
            oldenergy = final_energy            
            pointSet.final_energy = fenergy
            
            if(steps>0 and steps % self.render_update_freq == 0):
                if(self.callback):self.callback()
                printl("step",steps,"energy",fenergy,"echange",echange)
            steps+=1 
        
        if(self.callback):self.callback()  
    
 
        
class DualLatticeMinimiser(Minimiser):
    def __init__(self,*args,**kwargs):#,topology=None):
        Minimiser.__init__(self,*args,**kwargs)
        if(self.structure!=None):
            self.structure.set_dual_lattice_minimiser(self)
        self.req_radius=1.0
        
    def setup_force_field(self,pointSet):
        self.FF.setup(pointSet)
        if(self.structure.type==CAPPEDNANOTUBE):
            '''set the z-cutoff for thomson potential the nanotube '''
            self.FF.set_cutoff(self.structure.cutoff)  
            
    def pre_force_call_operations(self,pos,pointSet):       
        if(self.structure.type==CAPPEDNANOTUBE):
            length=self.structure.nanotube.midpoint_z*2 
        else:
            length=None
            
        clib_interface.scale_points_to_rad(pointSet.npoints,pos,self.req_radius,length=length)          
        
    
    def post_force_call_operations(self,pos,pointSet): 
        if(self.structure.type==CAPPEDNANOTUBE):
            #if cap atoms enter the tube add force... 
            k=1e4
            forcefield.force_on_cap_atoms_in_tube(self.structure.cap.dual_lattice.npoints,
                                                       pos,
                                                       pointSet.force,
                                                       pointSet.energy,
                                                       k)

        forcefield.remove_radial_component_of_force(pointSet.npoints,
                                                         pos,
                                                         pointSet.force
                                                         )    
        pointSet.force*=pointSet.freeflagspos 
        
class CarbonLatticeMinimiser(Minimiser):
    def __init__(self,*args,**kwargs):
        Minimiser.__init__(self,*args,**kwargs)
        if(self.structure!=None):
            self.structure.set_carbon_lattice_minimiser(self)
        
    def setup_force_field(self,pointSet):
        self.FF.setup(pointSet)
    
    def final_operations(self,pointSet):
        super(CarbonLatticeMinimiser, self).final_operations(pointSet)
        self.structure.update_child_structures()
    
    def minimise_onion_step_operations(self,args,onion):
        angles = args[0:(onion.NShells-1)*3]
        onion.carbonAtoms.pos = args[(onion.NShells-1)*3:]
        
        #printl("angles",angles) 
        
        c=0
        for i in range(1,onion.NShells):
            for j in range(0,3):
                angle = angles[c]
                if(j==0):
                    onion.rotate_x(i,angle)
                if(j==1):
                    onion.rotate_y(i,angle)
                if(j==2):
                    onion.rotate_z(i,angle)
                c+=1 
                
        penergy,pforce = self.FF.get_energy(onion.carbonAtoms) 
        
        c = 0 
        f = []
        h = 1e-4
        for i in range(1,onion.NShells):
            for j in range(0,3):
                angle = angles[c]
            
                if(j==0):
                    stime = time.time()
                    #onion.rotate_x(i,angle)
                    #print "r",time.time()-stime
                    stime = time.time()
                    #energy,force = self.FF.get_energy(onion.carbonAtoms) 
                    #print "e",time.time()-stime
                    stime = time.time()
                    #p1 = numpy.copy(onion.carbonAtoms.pos)
                    onion.rotate_x(i,h)
                    #print "r",time.time()-stime
                    stime = time.time()
                    fenergy,fforce = self.FF.get_energy(onion.carbonAtoms)
                    #print "e",time.time()-stime
                    stime = time.time()
                    onion.rotate_x(i,-h)
                    #onion.rotate_x(i,-angle)
                    #print "r",time.time()-stime
                    stime = time.time()
                    f.append((fenergy-penergy)/h)
                if(j==1):
                   # onion.rotate_y(i,angle)
                    energy,force = self.FF.get_energy(onion.carbonAtoms) 
                    onion.rotate_y(i,h)
                    fenergy,fforce = self.FF.get_energy(onion.carbonAtoms) 
                    onion.rotate_y(i,-h)
                    #onion.rotate_y(i,-angle)
                    f.append((fenergy-penergy)/h)
                if(j==2):
                    #onion.rotate_z(i,angle)
                    energy,force = self.FF.get_energy(onion.carbonAtoms) 
                    onion.rotate_z(i,h)
                    fenergy,fforce = self.FF.get_energy(onion.carbonAtoms) 
                    onion.rotate_z(i,-h)
                    #onion.rotate_z(i,-angle)
                    
                    f.append((fenergy-penergy)/h)
                #print "fenergy",fenergy,"energy",energy
                c+=1
        
        
        gout = numpy.append(numpy.array(f),force*-1)
        #printl("energy",penergy,magnitude(gout),angles) 
        #print energy,f
        #return magnitude(gout),gout
        return penergy,gout   
        
    def minimise_onion(self,onion,rot=True,min_type="LBFGS",ftol=1e-10,min_steps=100,update=True,callback=None):  
        self.updateFlag=update
        self.callback=callback
        self.ftol=ftol
        self.min_steps=min_steps
        self.stopmin = 0
        self.min_type=min_type
        self.currentPointSet = onion.carbonAtoms
        
        self.setup_force_field(onion.carbonAtoms)
        angles = numpy.zeros((onion.NShells-1)*3)
        
        
        if rot:
            printl("minimising onion with rotation")
            steps,echange = 0,10000000
            ienergy,iforce = self.FF.get_energy(onion.carbonAtoms)
            oldenergy = ienergy
            printl("initial energy, force",ienergy,magnitude(iforce))
            startt  = time.time()
            
            
            while(steps < self.min_steps  and echange > self.ftol and self.stopmin==0):
                bounds = None
                
                angles = numpy.zeros((onion.NShells-1)*3)
                args = numpy.append(angles,onion.carbonAtoms.pos)
                
                f_args, final_energy, d = fmin_l_bfgs_b(self.minimise_onion_step_operations, 
                                                              args, 
                                                              args = (onion,),
                                                              #fprime = self.get_force,
                                                              approx_grad = False, 
                                                              bounds = bounds, 
                                                              m = 100, 
                                                              factr = 10.0, 
                                                              pgtol = self.ftol, 
                                                              iprint = -1, maxfun = 150000)
                
                angles = f_args[0:(onion.NShells-1)*3]
                
                #print "outdiff",magnitude(onion.carbonAtoms.pos-f_args[(onion.NShells-1)*3:])
                onion.carbonAtoms.pos = f_args[(onion.NShells-1)*3:]
                c=0
                for i in range(1,onion.NShells):
                    for j in range(0,3):
                        angle = angles[c]
                        if(j==0):
                            onion.rotate_x(i,angle)
                        if(j==1):
                            onion.rotate_y(i,angle)
                        if(j==2):
                            onion.rotate_z(i,angle)
                        c+=1 

                
                #onion.write("optimise_onion_step_%04d.xyz"%(steps))
                printl("time for lbfgs",time.time()-startt,"steps",steps)
                printl("fmin_l_bfgs_b:" , d['task'],d['funcalls'],magnitude(d['grad']))
                
                fenergy,fforce = self.FF.get_energy(onion.carbonAtoms)
                printl("final angles",angles,"energy",final_energy,fenergy)
                
                self.post_force_call_operations(onion.carbonAtoms.pos, onion.carbonAtoms)
    
                echange = numpy.abs(oldenergy - final_energy)
                oldenergy = final_energy            
                onion.carbonAtoms.final_energy = final_energy

                if(steps>0 and steps % self.render_update_freq == 0):
                    if(self.callback):self.callback()
                    printl("step",steps,"energy",final_energy,fenergy,"echange",echange)
                steps+=1 
 
                    
            if(self.callback):self.callback()   
                
        else:
            self.minimise(onion.carbonAtoms,min_type="LBFGS")
        self.final_operations(onion.carbonAtoms)
  
    
    def apply_scale(self,gamma,pointSet):
        if(self.structure.type==CAPPEDNANOTUBE):
            length=self.structure.nanotube.midpoint_z*2.0
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