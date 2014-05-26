'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Apr 22, 2014
Copyright Marc Robinson  2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

nanotube class


-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
'''

from nanocap.core.globals import *
import os,sys,math,copy,random,time,ctypes,fractions
import numpy
import nanocap.core.points as points
from nanocap.structures.structure import Structure
from nanocap.core import triangulation,constructdual,calculateschlegel,ringcalculator
from nanocap.core import ringcalculator 
 
from nanocap.core.util import *

from nanocap.clib import clib_interface
clib = clib_interface.clib

class Nanotube(Structure):
    def __init__(self):
        Structure.__init__(self,STRUCTURE_TYPES[NANOTUBE])
        #self.type = StructureType(NANOTUBE,"NANOTUBE","Nanotube")
        self.radius=0
        self.length=0
        self.periodic = False
        self.periodic_length = 0
        self.unit_cells=0
        self.setup_parameters()
        self.n,self.m = 0,0
        
    def __repr__(self):
        out = super(Nanotube, self).__repr__()
        
#         out += self.col1h.format('structural_info')
#         out += self.col2.format("Length",self.length)
        
        return out
    
    def get_GUI_description(self,carbon_lattice=True,dual_lattice=True,carbonEnergy=True):
        '''
        override this superclass method so we can display capped nanotube specific info
        '''
        if(self.get_dual_lattice_energy()==0):
            des = "C{} ({},{}) {}".format(self.carbon_lattice.npoints,self.n,
                                          self.m,self.type.label)
        else:
            des = "C{} ({},{}) {}: Dual Lattice Energy {} ".format(self.carbon_lattice.npoints,
                                                                   self.nanotube.n,self.nanotube.m,
                                                                   self.type.label,self.get_dual_lattice_energy())
        return des   
        
    def get_structure_data(self):
        self.data = super(Nanotube, self).get_structure_data()

        try:self.data['dual_lattices']['n'] = self.n
        except:pass
        try:self.data['dual_lattices']['m'] = self.m
        except:pass
        try:self.data['carbon_lattices']['uncapped_length'] = self.length
        except:pass
        try:self.data['carbon_lattices']['n'] = self.n
        except:pass
        try:self.data['carbon_lattices']['m'] = self.m
        except:pass
        try:self.data['carbon_lattices']['periodic'] = int(self.periodic)
        except:pass
        try:self.data['carbon_lattices']['periodic_length'] = self.periodic_length
        except:pass
        try:self.data['carbon_lattices']['unit_cells'] = self.unit_cells        
        except:pass
        return self.data
        
    def set_dual_lattice(self,npoints,pos):
        out = super(Nanotube, self).set_dual_lattice(npoints,pos)
        
        self.midpoint_z = self.dual_lattice.getCenter()[2]
        
    
    def setup_parameters(self):
        self.root3 = math.sqrt(3)
        self.root2 = math.sqrt(2)
        self.ac = 1.42
        self.a0 = self.root3*self.ac
        self.a1 = (self.a0/2.0)*numpy.array([self.root3,1])
        self.a2 = (self.a0/2.0)*numpy.array([self.root3,-1])
        
    
    def setup_properties(self,n,m):
        if(n==0) and (m==0):return 
        self.m = m
        self.n = n
        if(m>n):
            self.m = n
            self.n = m 
        
        self.Ch = self.n*self.a1 + self.m*self.a2
        self.Cnorm = normalise(self.Ch)
        
        self.T = normalise(numpy.array([-self.Ch[1],self.Ch[0]]))
        
        self.CTBasis = numpy.matrix([[self.Cnorm[0], self.T[0]], [self.Cnorm[1], self.T[1]]])
        self.CTBasis_inv = numpy.linalg.inv(self.CTBasis)
        
        self.ChTheta  = math.atan((math.sqrt(3) * float(self.m)) /float( 2*self.n+self.m))
        
        printl("({},{}) Chiral Vector {}".format(self.n,self.m,self.Ch))
        printl("({},{}) T Vector {}".format(self.n,self.m,self.T))
        
        self.nm_gcd = fractions.gcd(self.n,self.m)
        
        printl("({},{}) GCD {}".format(self.n,self.m,self.nm_gcd))
        
        self.circumferene = magnitude(self.Ch)
        self.radius = self.circumferene/(math.pi*2.0)
        
#     def construct_dual_lattice(self,n,m,l,input_points=None,radius=1.0,seed=None):
#         '''
#         constructing the dual lattice for a nanotube involves placing a point inside each hexagon
#         '''
#         if(n==0) and (m==0):return 
#         
#         self.construct_2D_lattices(n,m,l)
#         
#         self.setup_3D_lattices()
#                 
#         self.scale_dual_lattice(radius)
#         
#         printl("nanotube length",self.length)
    
    def construct(self,n,m,length=10.0,units=1,periodic=False):
        if(n==0) and (m==0):return 
        
        self.periodic=periodic
        
        if(periodic):
            dr = fractions.gcd(2*n+m, 2*m+n)
            t1 = (2*m+n)/dr
            t2 = -(2*n+m)/dr
            T = t1*self.a1 + t2*self.a2
            
            l = magnitude(T)*units
            self.periodic_length = l
            self.unit_cells = units
            printl("t1,t2,T,L",t1,t2,T,self.a1,self.a2,l)
            printl("base points",2*(n*n + m*m +n*m)/dr)
            
        else:
            l = length
            
        self.construct_2D_lattices(n,m,l)
            
        self.setup_3D_lattices()
        
        self.length = self.get_length()
        
    
    def scale_dual_lattice(self,radius):
        self.scale = radius/self.radius 
        self.dual_lattice.pos*=self.scale
        self.midpoint_z*=self.scale
        self.scaled_length=self.scale*self.length
        
    def xy_to_ct(self,x,y):
        '''
        here we use a change of basis matrix to convert from x,y positions
        to c,t positions
        '''
        newx = x*self.CTBasis_inv[0,0] + y*self.CTBasis_inv[0,1]
        newy = x*self.CTBasis_inv[1,0] + y*self.CTBasis_inv[1,1]
        
        printd(x,y,newx,newy)
        return newx,newy
        
    def construct_2D_lattices(self,n,m,length):
        printl("constructing 2D carbon nanotube")
        
        if(n==0) and (m==0):return
        
        self.setup_properties(n,m)
        
        strip_points = self.get_base_points(length)
        
        self.points2D = points.Points("Nanotube 2D points") 
        self.points2D.initArrays(len(strip_points)/2)
        point3D = numpy.zeros((len(strip_points)/2)*3,NPF)
        point3D[0::3] = strip_points[0::2]
        point3D[1::3] = strip_points[1::2]
        point3D[2::3] = 0.0
        self.points2D.pos = numpy.copy(point3D)
        
        self.carbon_lattice2D = points.Points("Nanotube 2D carbon lattice") 
        self.carbon_lattice2D.initArrays(self.points2D.npoints*2)
        self.carbon_lattice2D.pos[:self.points2D.npoints*3] = numpy.copy(self.points2D.pos)
        self.carbon_lattice2D.pos[self.points2D.npoints*3:] = numpy.copy(self.points2D.pos)
        #Batoms
        self.carbon_lattice2D.pos[self.points2D.npoints*3:][0::3] += self.ac
        
        self.dual_lattice2D = points.Points("Nanotube 2D dual lattice") 
        self.dual_lattice2D.initArrays(self.points2D.npoints)
        self.dual_lattice2D.pos = numpy.copy(self.points2D.pos)
        self.dual_lattice2D.pos[0::3] += 2.0*self.ac
        #alternate dual lattice point basis below:
        #self.dual_lattice2D.pos[0::3] += 0.5*self.ac
        #self.dual_lattice2D.pos[1::3] += self.root3*0.5*self.ac
        
        self.i_lattice2D = points.Points("Nanotube 2D i lattice") 
        self.i_lattice2D.initArrays(self.points2D.npoints*3)
        self.i_lattice2D.pos[:self.points2D.npoints*3] = numpy.copy(self.points2D.pos)
        self.i_lattice2D.pos[self.points2D.npoints*3:self.points2D.npoints*3*2] = numpy.copy(self.points2D.pos)
        self.i_lattice2D.pos[self.points2D.npoints*3*2:] = numpy.copy(self.points2D.pos)
        
        self.i_lattice2D.pos[:self.points2D.npoints*3][0::3] += 0.5*self.ac
        
        self.i_lattice2D.pos[self.points2D.npoints*3:self.points2D.npoints*3*2][0::3] += self.ac*0.25 + self.ac
        self.i_lattice2D.pos[self.points2D.npoints*3:self.points2D.npoints*3*2][1::3] += self.ac*0.25*self.root3
        
        self.i_lattice2D.pos[self.points2D.npoints*3*2:][0::3] += self.ac*0.25 + self.ac
        self.i_lattice2D.pos[self.points2D.npoints*3*2:][1::3] -= self.ac*0.25*self.root3

        self.align_2D_lattice()
        
        miny = numpy.min(self.dual_lattice2D.pos[1::3])
        printl("miny",miny)
        
        self.carbon_lattice2D.pos[1::3] -= miny
        self.dual_lattice2D.pos[1::3] -= miny
        self.i_lattice2D.pos[1::3] -= miny
        self.points2D.pos[1::3] -= miny
        
        self.midpoint2D = points.Points("Nanotube 2D midpoint") 
        self.midpoint2D.initArrays(1)
        distToMid = self.i_lattice2D.pos[1::3] - self.dual_lattice2D.getCenter()[1]
        intersection_point = numpy.argmin(numpy.abs(distToMid))
        self.midpoint2D.pos = self.i_lattice2D.pos[intersection_point*3:intersection_point*3+3]
        
        
        
        if(DEBUG):self.setup_debug_points()
        
        
    def get_length(self):
        x0,y0,z0,x1,y1,z1 = self.carbon_lattice.getBounds()
        return z1-z0
    
    def set_carbon_lattice(self,npoints,pos):
        self.carbon_lattice = points.Points("Nanotube carbon lattice")
        self.carbon_lattice.initArrays(npoints)
        self.carbon_lattice.pos = numpy.copy(pos)
    
    def setup_3D_lattices(self):
        self.dual_lattice = points.Points("Nanotube dual lattice") 
        self.dual_lattice.initArrays(self.dual_lattice2D.npoints,free=False)
        self.dual_lattice.pos = numpy.copy(self.dual_lattice2D.pos)
        
        self.carbon_lattice = points.Points("Nanotube carbon lattice") 
        self.carbon_lattice.initArrays(self.carbon_lattice2D.npoints)
        self.carbon_lattice.pos = numpy.copy(self.carbon_lattice2D.pos)
        
        '''
        y position becomes new z position in 3D
        '''
        y = numpy.copy(self.dual_lattice.pos[1::3])
        self.dual_lattice.pos[2::3] = y
        
        y = numpy.copy(self.carbon_lattice.pos[1::3])
        self.carbon_lattice.pos[2::3] = y
        
        '''
        the next line is very important
        we shift the 2D lattice such that the x axis lies on the midpoint. 
        this means in 3D, the x axis lies on the C2 rotational axis.
        x=x
        y=-y
        z=-z
        '''
        
        self.dual_lattice.pos[0::3]-=self.midpoint2D.pos[0]
        self.carbon_lattice.pos[0::3]-=self.midpoint2D.pos[0]
        self.midpoint_z = self.midpoint2D.pos[1]
        
        
        '''
        Now to convert the 2D lattice into 3D. The position along x translates to
        an angle which is used to determine new x and y positions:
        '''
        angles = (self.dual_lattice.pos[0::3]/self.circumferene)*math.pi*2.0
        
        x = self.radius*numpy.cos(angles)
        y = self.radius*numpy.sin(angles)
        self.dual_lattice.pos[0::3] = x
        self.dual_lattice.pos[1::3] = y
        
        angles = (self.carbon_lattice.pos[0::3]/self.circumferene)*math.pi*2.0
        
        x = self.radius*numpy.cos(angles)
        y = self.radius*numpy.sin(angles)
        self.carbon_lattice.pos[0::3] = x
        self.carbon_lattice.pos[1::3] = y
        

        
        if(DEBUG):
            self.dual_lattice_r = points.Points("Nanotube dual lattice rotated") 
            self.dual_lattice_r.initArrays(self.dual_lattice.npoints)
            self.dual_lattice_r.pos = numpy.copy(self.dual_lattice.pos)
            
            self.dual_lattice_r.pos[2::3] -= self.midpoint_z
            self.dual_lattice_r.pos[1::3]*=-1
            self.dual_lattice_r.pos[2::3]*=-1
            self.dual_lattice_r.pos[2::3] += self.midpoint_z
   
        
    def setup_debug_points(self):
        '''
        debug rotated lattices
        '''
        self.points2D_r = points.Points("Nanotube 2D points rotated") 
        self.points2D_r.initArrays(self.points2D.npoints)     
        self.points2D_r.pos = numpy.copy(self.points2D.pos)    
        self.rotate_2D_lattice(self.points2D_r)
        
        self.carbon_lattice2D_r = points.Points("Nanotube 2D carbon lattice rotated") 
        self.carbon_lattice2D_r.initArrays(self.carbon_lattice2D.npoints)     
        self.carbon_lattice2D_r.pos = numpy.copy(self.carbon_lattice2D.pos)    
        self.rotate_2D_lattice(self.carbon_lattice2D_r)
        
        
        self.dual_lattice2D_r = points.Points("Nanotube 2D dual lattice rotated") 
        self.dual_lattice2D_r.initArrays(self.dual_lattice2D.npoints)     
        self.dual_lattice2D_r.pos = numpy.copy(self.dual_lattice2D.pos)    
        self.rotate_2D_lattice(self.dual_lattice2D_r)
                
    def align_2D_lattice(self):
        '''
        align x,y with c,t
        '''    
        
        for i in range(0,self.points2D.npoints):
            c,t = self.xy_to_ct(self.points2D.pos[i*3],self.points2D.pos[i*3+1])
            self.points2D.pos[i*3],self.points2D.pos[i*3+1] = c,t
        
        for i in range(0,self.carbon_lattice2D.npoints):
            c,t = self.xy_to_ct(self.carbon_lattice2D.pos[i*3],self.carbon_lattice2D.pos[i*3+1])
            self.carbon_lattice2D.pos[i*3],self.carbon_lattice2D.pos[i*3+1] = c,t    
        
        for i in range(0,self.dual_lattice2D.npoints):
            c,t = self.xy_to_ct(self.dual_lattice2D.pos[i*3],self.dual_lattice2D.pos[i*3+1])
            self.dual_lattice2D.pos[i*3],self.dual_lattice2D.pos[i*3+1] = c,t       
        
        for i in range(0,self.i_lattice2D.npoints):
            c,t = self.xy_to_ct(self.i_lattice2D.pos[i*3],self.i_lattice2D.pos[i*3+1])
            self.i_lattice2D.pos[i*3],self.i_lattice2D.pos[i*3+1] = c,t     
            
    def rotate_2D_lattice(self,points,angle=math.pi):    
        '''
        debug routine to rotate a 2D lattice to check
        symmetry
        '''    
        points.pos[0::3] -= self.midpoint2D.pos[0]
        points.pos[1::3] -= self.midpoint2D.pos[1]
        
        cr = math.cos(angle)
        sr = math.sin(angle)
        
        xc = points.pos[0::3]*cr
        xs = points.pos[0::3]*sr
        yc = points.pos[1::3]*cr
        ys = points.pos[1::3]*sr
        points.pos[0::3] = xc - ys
        points.pos[1::3] = xs + yc
        
        points.pos[0::3] += self.midpoint2D.pos[0]
        points.pos[1::3] += self.midpoint2D.pos[1]
    
    def get_base_points(self,length):
        '''
        return the basis points (A atoms) for the current nanotube
        up to length=length.
        '''
        origin = numpy.zeros(2,NPF)
        strip_points = self.get_strip(origin)
        
        #strip_points[0::2],strip_points[1::2] = self.xy_to_ct(strip_points[0::2],strip_points[1::2])
        
        #mp = numpy.argmax(strip_points[1::2])
        cx,ty = self.xy_to_ct(strip_points[0::2],strip_points[1::2])
        self.current_length = numpy.max(ty)
        
        #self.current_length = numpy.max(strip_points[1::2])
        
        printl("current_length",self.current_length,"req",length)
        #here should be allow for lengths that are part of a strip or
        #only full strips.
        
        strip_c = 0
        while(self.current_length<length):
            origin[1]+=self.a0
            newstrip = self.get_strip(origin)
            #mp = numpy.argmax(newstrip[1::2])
            #cx,ty = self.xy_to_ct(newstrip[mp*2],newstrip[mp*2+1])
            
            #cx,ty = self.xy_to_ct(newstrip[0*2],newstrip[0*2+1])
            
            cx,ty = self.xy_to_ct(newstrip[0::2],newstrip[1::2])

            #printl("x,y",newstrip[0*2],newstrip[0*2+1],"c,t",cx,ty)
        
            #if(ty>=length):
                #self.current_length = ty
                #strip_points = numpy.append(strip_points,newstrip)
                #break
            
            #strip_points = numpy.append(strip_points,self.get_strip(origin))
            #mp = numpy.argmax(strip_points[1::2])
            #cx,ty = self.xy_to_ct(strip_points[mp*2],strip_points[mp*2+1])
            #self.current_length = ty
            self.current_length = numpy.max(ty)
            if(self.periodic):
                mp = numpy.where(ty-length>-1e-8)[0]
                printl("mp",mp,ty-length)
                newstrip = numpy.delete(newstrip,numpy.append(mp*2,mp*2+1))
            
            strip_points = numpy.append(strip_points,newstrip)
            printl("current_length",self.current_length,numpy.max(strip_points[1::2]))
            
            printl("strip_c",strip_c)
            strip_c+=1
            
        #self.length = self.current_length
        
        printl("current_length",self.current_length,"req",length)
        
        return strip_points
        
    def get_strip(self,origin):
        '''
        return a single strip of basis points up to
        the chiral vector (n,m)
        i.e. (7,3) = (1,0),(2,0),(3,0),(3,1),(4,1)...
        '''
        npoints = self.n + self.m
        #p = numpy.array(origin)
        out = numpy.zeros(npoints*2,NPF)
        count = 0
        c_n,c_m=0,0
        #Charg = (self.root3 * float(self.m))/float( 2*self.n+self.m)
        
        Ang = float(self.m)/float( 2*self.n+self.m)
        while(count<npoints):
                        
            printd("n,m",c_n,c_m,count)
            p = origin + c_n*self.a1 + c_m*self.a2  
            out[count*2] = p[0]
            out[count*2+1] = p[1]
            count+=1
            
            c_m+=1
            #ChTheta = math.atan((self.root3 * float(c_m)) /float( 2*c_n+c_m))
            Ang_temp = float(c_m)/float( 2*c_n+c_m)
            printd(float(c_m)/float( 2*c_n+c_m),float(self.m)/float( 2*self.n+self.m))
            #if(ChTheta>self.ChTheta):
            if(Ang_temp>Ang):
                c_m-=1
                c_n+=1
    
        printd(out)
        return out
        
    def get_strip_old(self,origin):
        npoints = self.n + self.m
        p = numpy.array(origin)
        out = numpy.zeros(npoints*2,NPF)
        count = 0
        for i in range(0,self.nm_gcd):
            for j in range(0,self.n/self.nm_gcd):
                
                out[count*2] = p[0]
                out[count*2+1] = p[1]
                
                #points.append(numpy.copy(p))   
                count+=1
                p+=self.a1 
            for j in range(0,self.m/self.nm_gcd):    
                
                #points.append(numpy.copy(p)) 
                out[count*2] = p[0]
                out[count*2+1] = p[1]   
                count+=1 
                p+=self.a2    
                
        printl(out)
        return out
        