'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Apr 16, 2014
Copyright Marc Robinson  2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

parent class for fullerenes,
nanotubes, cappednanotubes,
cap etc...


-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
'''
from nanocap.core.globals import *
from nanocap.core.util import *
import os,sys,math,copy,random,time,ctypes,shutil,datetime
import numpy
import yaml
import nanocap.core.points as points
from nanocap.core import triangulation,constructdual,calculateschlegel,ringcalculator,output,input
from nanocap.clib import clib_interface
from nanocap.core.structuredata import *

clib = clib_interface.clib

class Structure(object):
    '''
    
    Important methods:
    
    get_structure_data - returns this structures data as a 
                         dict using the universal structure 
                         data class. This is then used by 
                         structurelogs and the databases.
                         The parent class will define common
                         data but the child specific data needs
                         to be declared in each subclass
                         
    
    
    '''
    def __init__(self,type):
        '''
        must declare:
        dual_lattice
        carbon_lattice 
        '''
        self.type = StructureType(NULL,"NULL","NULL")
        self.type=type
        self.has_triangles = False
        self.has_carbon_bonds = False
        self.has_carbon_rings = False
        self.has_schlegel = False
        self.has_child_structures = False
        
        self.dual_lattice = points.Points(self.type.label+" Dual Lattice Points")
        self.dual_lattice.initArrays(0)
        self.carbon_lattice = points.Points(self.type.label+" Carbon Lattice Points")
        self.carbon_lattice.initArrays(0)
        
        self.carbon_lattice_minimiser = None
        self.dual_lattice_minimiser = None
        
        self.seed = -1
        
        self.parent_structure=None
        
        self.dual_lattice_user  = CONFIG.opts['User']
        self.carbon_lattice_user = CONFIG.opts['User']
        
               
        self.database = None
    
    
    def load_carbon_lattice_from_file(self,file,format):
        
        p = input.read_points(file,format)
        self.set_carbon_lattice(p.npoints,p.pos)
            
    def load_dual_lattice_from_file(self,file,format):     
        p = input.read_points(file,format)
        self.set_dual_lattice(p.npoints,p.pos)
        
    def get_structure_data(self):
        #self.structure_data = StructureData(self)
        
        self.data = copy.deepcopy(DEFAULT_DATA)
        
        printl("initial structure data",self.data)
        
        table = 'dual_lattice_points'
        self.data[table]['x'] = self.dual_lattice.pos[0::3]   
        self.data[table]['y'] = self.dual_lattice.pos[1::3]  
        self.data[table]['z'] = self.dual_lattice.pos[2::3]  
        
        table = 'carbon_lattice_points'
        self.data[table]['x'] = self.carbon_lattice.pos[0::3]    
        self.data[table]['y'] = self.carbon_lattice.pos[1::3]  
        self.data[table]['z'] = self.carbon_lattice.pos[2::3]  
        
        table = 'rings'
        try:
            self.data[table]['rings_3'] =   int(self.ring_info['ringCount'][3])
            self.data[table]['rings_4'] =   int(self.ring_info['ringCount'][4])
            self.data[table]['rings_5'] =   int(self.ring_info['ringCount'][5])
            self.data[table]['rings_6'] =   int(self.ring_info['ringCount'][6])
            self.data[table]['rings_7'] =   int(self.ring_info['ringCount'][7])
            self.data[table]['rings_8'] =   int(self.ring_info['ringCount'][8])
        except:
            pass
        
        table = 'dual_lattices'
        self.data[table]['date'] = datetime.datetime.now()
        self.data[table]['user_name'] = self.dual_lattice_user
        self.data[table]['type'] = self.type.label
        self.data[table]['npoints'] = self.dual_lattice.npoints
        self.data[table]['energy'] = self.get_dual_lattice_energy()
        try:
            self.data[table]['ff_id'] = self.dual_lattice_minimiser.FFID
            self.data[table]['optimiser'] =self.dual_lattice_minimiser.min_type
        except:pass
        

        table = 'carbon_lattices'
        self.data[table]['date'] = datetime.datetime.now()
        self.data[table]['user_name'] = self.carbon_lattice_user
        self.data[table]['type'] = self.type.label
        self.data[table]['natoms'] = self.carbon_lattice.npoints
        self.data[table]['energy'] = self.get_carbon_lattice_energy()
        self.data[table]['energy_constrained'] = self.get_carbon_lattice_scaled_energy()
        self.data[table]['energy_per_atom'] = self.get_carbon_lattice_energy_per_atom()
        self.data[table]['scale'] = self.get_carbon_lattice_scale()
        
        try:
            self.data[table]['ff_id'] = self.carbon_lattice_minimiser.FFID
            self.data[table]['ff_options'] = self.carbon_lattice_minimiser.FF.options
            self.data[table]['optimiser'] = self.carbon_lattice_minimiser.min_type
            self.data[table]['energy_units'] = self.carbon_lattice_minimiser.FF.energy_units
        except:pass
        
        
        
        return self.data
    
    def set_dual_lattice(self,npoints,pos):
        self.dual_lattice = points.Points("{} Dual Lattice Points".format(self.type.label))
        self.dual_lattice.initArrays(npoints)
        self.dual_lattice.pos = numpy.copy(pos)
        
    def set_carbon_lattice(self,npoints,pos):
        self.carbon_lattice = points.Points("{} Carbon Lattice Points".format(self.type.label))
        self.carbon_lattice.initArrays(npoints)
        self.carbon_lattice.pos = numpy.copy(pos)
        self.calculate_child_carbon_lattices()
    
    def calculate_child_carbon_lattices(self):pass
    
    def set_con_carbon_lattice(self,npoints,pos):
        #self.carbon_lattice = points.Points("{} Carbon Lattice Points".format(self.type.label))
        #self.carbon_lattice.initArrays(npoints)
        self.carbon_lattice.constrained_pos = numpy.copy(pos)
        
    def set_carbon_lattice_minimiser(self,minimiser):
        #pass
        self.carbon_lattice_minimiser = minimiser
    
    def set_dual_lattice_minimiser(self,minimiser):
        #pass
        self.dual_lattice_minimiser = minimiser
    
    def get_child_structures(self):
        '''
        if capped nanotube, return the nanotube and cap
        
        '''
        return []
    
    def update_child_structures(self):
        pass
    
    def export(self,folder=".",
               save_info=True,
               save_image=False,
               save_video=False,
               save_carbon_lattice=True,
               save_con_carbon_lattice=True,
               info_file='structure_info.txt',
               save_dual_lattice=True,
               formats=['xyz',]):
        
        path = os.path.abspath(os.path.join(folder,self.get_single_line_description()))
        try:os.makedirs(path)
        except:pass
        
        if(save_image):
            from nanocap.rendering.defaults import SCHLEGEL_G,SCHLEGEL_R
            self.vtkframe.move_camera([0,0,-100],[0,0,0],[0,1,0])
            self.vtkframe.resetCamera()
            self.vtkframe.saveImage(os.path.join(path,"isometric.jpg"),overwrite=True,resolution=None)
            self.calculate_schlegel(SCHLEGEL_G,SCHLEGEL_R)
            self.schlegelframe.saveImage(os.path.join(path,"schlegel.jpg"),overwrite=True,resolution=None)
        
        if(save_dual_lattice):
            filename = os.path.join(path,"dual_lattice")
            self.export_dual_lattice(filename, formats)
        if(save_carbon_lattice):
            filename = os.path.join(path,"carbon_lattice")
            self.export_carbon_lattice(filename, formats)
        if(save_con_carbon_lattice):
            filename = os.path.join(path,"constrained_carbon_lattice")
            self.export_con_carbon_lattice(filename, formats)
        if(save_info):
            filename = os.path.join(path,info_file)
            f= open(filename,"w")
            f.write(self.__repr__())
            f.close()
            f= open(os.path.splitext(filename)[0]+".yaml","w")
            yaml.dump(self.get_structure_data(), f,default_flow_style=False)
            f.close()
                        
            
        
    def export_dual_lattice(self,filename,formats=['xyz',]):
        for format in formats:
            output.write_points(filename,self.dual_lattice,format,constrained=False)
        
        for child in self.get_child_structures():
            child.export_dual_lattice(filename+"_{}".format(child.type.label),formats=formats)
            
    def export_carbon_lattice(self,filename,formats=['xyz',]):
        for format in formats:
            output.write_points(filename,self.carbon_lattice,format,constrained=False)
        for child in self.get_child_structures():
            child.export_carbon_lattice(filename+"_{}".format(child.type.label),formats=formats)    
    def export_con_carbon_lattice(self,filename,formats=['xyz',]):
        for format in formats:
            output.write_points(filename,self.carbon_lattice,format,constrained=True)
        
    def render(self,render_window=None,dual_lattice=True,carbon_lattice=True,rings=True,triangles=True,
               options_holder=None,show=True,render_window_holder=None):
        '''
        here we should render the structure
        if passed a renderer then use that, else pop up a new window. 
        
        have a new class that is a renderwindow with its options. Pass it a structure and the options
        control toggling of points etc. '''
        
        
        try:
            from nanocap.gui.settings import QtGui,QtCore 
            from nanocap.gui.widgets import HolderWidget
            from nanocap.gui import structureoptionswindow
            from nanocap.gui.renderwindow import vtkqtframe
            from nanocap.rendering import structureactors
            
        except:
            printe("could not import GUI/render libraries, will not render")
            return
            
        
        if(options_holder==None and render_window_holder==None):
            app = QtGui.QApplication(sys.argv)
            
        if(render_window==None):     
            self.render_window = QtGui.QTabWidget()       
            self.vtkframe = vtkqtframe.VtkQtFrame(0) 
            self.schlegelframe = vtkqtframe.VtkQtFrame(0)
            self.schlegelframe.move_camera(numpy.array([0,0,10]),numpy.array([0,0,0]),numpy.array([0,1,0]))
            self.render_window.addTab(self.vtkframe,"3D View")
            self.render_window.addTab(self.schlegelframe,"Schlegel View")
            self.render_window.vtkframe = self.vtkframe
            self.render_window.schlegelframe = self.schlegelframe
            
#             if(show):
#                 self.vtkframe.show()
#                 self.schlegelframe.show()
                
        else:self.render_window = render_window
        
        self.structure_actors = structureactors.StructureActors(self)
        self.options_window = structureoptionswindow.StructureOptionsWindow(self)
        #self.options_window = QtGui.QWidget()
        #self.options_window.hide()
        
        #if(render_window!=None):holder.addWidget(self.render_window)
        if(options_holder!=None):
            options_holder.addWidget(self.options_window)
            
        if(render_window_holder!=None):
            render_window_holder.addWidget(self.render_window)
        
        self.render_window.vtkframe.centerCameraOnPointSet(self.carbon_lattice)        
        
        for child_structure in self.get_child_structures():
            printl("setting child_structure actors",child_structure.type.label)
            child_structure.render_window = self.render_window
            child_structure.structure_actors = structureactors.StructureActors(child_structure)
            child_structure.options_window = structureoptionswindow.StructureOptionsWindow(child_structure)
            self.options_window.points_widgets_holder.addHeader(child_structure.type.label,
                                                                bold=True,frame=False)
            self.options_window.points_widgets_holder.addWidget(child_structure.options_window.render_points_table)
        
        if(options_holder==None and render_window_holder==None):
            self.window = HolderWidget()
            self.window.containerLayout.setSpacing(0)
            if(options_holder==None):self.window.addWidget(self.options_window)
            if(render_window_holder==None):self.window.addWidget(self.render_window)
            
            
                #child_structure.render(options_holder=self.window,
                #                       render_window=self.render_window)
            
            if(show):
                
                #app = QtGui.QApplication(sys.argv)
                mw = QtGui.QMainWindow()
                mw.setCentralWidget(self.window)
                mw.show()
                self.window.show()
                app.exec_()
                #sys.exit(app.exec_())
        else:
            if(show):
                pass
#                 self.options_window.show()
#                 for child_structure in self.get_child_structures():
#                     child_structure.options_window.show()
#                 self.render_window.show()
                
        printl("end render")       
                #self.window.show()       
        
    def render_update(self):
        printl("in render update",self.type.label)
        try:
            from nanocap.gui.settings import QtGui,QtCore 
            self.options_window.emit(QtCore.SIGNAL("update_structure()"))
            
            self.structure_actors.update_actors()
            self.vtkframe.center_on_load()
            self.schlegelframe.center_on_load()
        except:
            pass
       
        try:     
            for child_structure in self.get_child_structures():
                child_structure.render_update()
        except:
            pass
        printl("emitted update_structure",self.type.label)
        
            
    
    def show(self):
        self.options_window.show()
        self.render_window.show()
        
    def hide(self):
        self.options_window.hide()
        self.render_window.hide()

        
    def __repr__(self):
        self.twidth = 80
        self.sepformat = "{0:=^"+str(self.twidth)+"} \n"
        
        self.col1 = "{0:<"+str(self.twidth)+"} \n"
        self.col1h = "{0:-^"+str(self.twidth)+"} \n"
        self.col1c = "{0:.^"+str(self.twidth)+"} \n"
        self.col2 = "{0:<"+str(int(self.twidth/2))+"} {1:<"+str(int(self.twidth/2))+"}\n"
        self.col3 = "{0:<"+str(int(self.twidth/3))+"} {1:<"+str(int(self.twidth/3))+"} {2:<"+str(int(self.twidth/3))+"}\n"
        self.col4 = "{0:<"+str(int(self.twidth/4))+"} {1:<"+str(int(self.twidth/4))+"} {2:<"+str(int(self.twidth/4))+"} {3:<"+str(int(self.twidth/4))+"}\n" 
        
        
        out = ""
        out += self.sepformat.format("C"+str(self.carbon_lattice.npoints)+" "+self.type.label)
        
        tables = ['dual_lattices', 
               'carbon_lattices',
               'rings','users']
        
        fdata = self.format_data()
        
        for table in tables:
            out += self.col1c.format(table)
            for key,d in fdata[table].items():
                out += self.col2.format(key,d)  
        
        return out
    
    def format_data(self):
        data = self.get_structure_data()
        
        printl(data.keys())
        
        tables = ['dual_lattices', 
               'carbon_lattices',
               'rings','users']
        exclude = ['type',]

        #for table in data.keys():
  
        out = {}
        for table in tables:
            #out += self.col1c.format(table)
            header = table
            out[header] = {}
            cols = []
            for field in data[table].keys():
                if(field in exclude):continue
                d = data[table][field]
                if(d!=None):
                    #out += self.col2.format(field,d)  
                    if(isinstance(d, datetime.datetime)):
                        d = d.strftime("%Y-%m-%d %H:%M:%S")

                    cols.append((field,d))
            if(len(cols)>0):
                #out += self.col1c.format(table)
                for c in cols:
                    #out += self.col2.format(*c)   
                    out[header][c[0]] = c[1]
        return out
        
    
    def calculate_structural_info(self):
        
        pass
    
    def get_single_line_description(self,carbon_lattice=True,dual_lattice=True,carbonEnergy=True):
        des=self.type.text
            
        if(carbon_lattice):des+="_Nc_"+str(self.carbon_lattice.npoints)
        if(dual_lattice):des+="_Nt_"+str(self.dual_lattice.npoints)
        if(carbonEnergy):
            try:des+="_Energy_"+str(self.get_carbon_lattice_energy())
            except:
                if(self.get_dual_lattice_energy()>0):
                    des+="_Energy_"+str(self.get_dual_lattice_energy())
        else:
            if(self.get_dual_lattice_energy()>0):
                des+="_Energy_"+str(self.get_dual_lattice_energy())
            
        if(self.has_carbon_rings):
            if(self.ring_info['ringCount'][5]>0):
                IPperc = float(self.ring_info['isolatedPentagons'])/float(self.ring_info['ringCount'][5])*100.0
                des+="_IP%_"+str(IPperc)
        return des
    
    def get_GUI_description(self,carbon_lattice=True,dual_lattice=True,carbonEnergy=True):
        if(self.get_dual_lattice_energy()==0):
            des = "C{} {}".format(self.carbon_lattice.npoints,self.type.label)
        else:
            des = "C{} {}: Dual Lattice Energy {} ".format(self.carbon_lattice.npoints,self.type.label,
                                                                  self.get_dual_lattice_energy())
        return des    
    
    def get_points(self,key):
        if(key=="DualLattice"):return self.dual_lattice
        if(key=="CarbonAtoms"):return self.carbon_lattice
        if(key=="DualLattice_S"):
            if(self.has_schlegel):return self.schlegel_dual_lattice
            else:
                printl("Schlegel not calculated")
                return None
        if(key=="CarbonAtoms_S"):
            if(self.has_schlegel):return self.schlegel_carbon_lattice
            else:
                printl("Schlegel not calculated")
                return None
    
    def triangulate_dual_lattice(self):
        self.vertlist,self.ntriangles = triangulation.delaunyTriangulation(self.dual_lattice)
        self.has_triangles=True
        
    def construct_carbon_lattice(self):
        printd("constructing carbon atoms from dual lattice")
        self.triangulate_dual_lattice()
        
        self.carbon_lattice = constructdual.constructDual(self.dual_lattice,self.ntriangles,
                                        self.vertlist,
                                        outlabel=self.type.label+" Carbon Atoms")
    
            
    def calculate_rings(self):
        printl("calculate_rings")
        self.ring_info = ringcalculator.calculate_rings(self.carbon_lattice,MaxNebs=3,MaxVerts=9)   
        self.has_carbon_rings = True
        if(self.ring_info['nrings']==0):self.has_carbon_rings=False
        
    def calculate_schlegel(self,gamma,cutoff):    
        
        self.schlegel_dual_lattice = calculateschlegel.calculate_schlegel_projection(self.dual_lattice,gamma)
        self.schlegel_carbon_lattice = calculateschlegel.calculate_schlegel_projection(self.carbon_lattice,gamma)
        self.schlegel_carbon_lattice_full = copy.deepcopy(self.schlegel_carbon_lattice)


        z = self.carbon_lattice.pos[2::3]
        todelete  = numpy.where(z>cutoff)[0]
        self.schlegel_carbon_lattice.removeIndexes(todelete)

        z = self.dual_lattice.pos[2::3]
        todelete  = numpy.where(z>cutoff)[0]
        self.schlegel_dual_lattice.removeIndexes(todelete)
        
        if(self.has_carbon_rings):
            self.schlegel_ring_info = copy.deepcopy(self.ring_info)
            
            for i in range(0,self.ring_info['nrings']):
                for j in range(0,self.ring_info['VertsPerRingCount'][i]):
                    index = self.ring_info['Rings'][i*self.ring_info['MaxVerts'] + j]
                    if(self.carbon_lattice.pos[index*3+2]>cutoff):
                        self.schlegel_ring_info['VertsPerRingCount'][i] =0 
                        break    
                    
            for i in range(0,self.ring_info['nrings']):
                printl("Schlegel ring {} verts {} ".format(i,self.schlegel_ring_info['VertsPerRingCount'][i]))
                
        self.has_schlegel = True
    
    def calculate_carbon_bonds(self):
        maxbonds = 10
        AvBondLength = numpy.zeros(self.carbon_lattice.npoints,NPF)
        clib.get_average_bond_length(ctypes.c_int(self.carbon_lattice.npoints),
                                     self.carbon_lattice.pos.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                                     AvBondLength.ctypes.data_as(ctypes.POINTER(ctypes.c_double)))
          
        cutoff  = numpy.average(AvBondLength)*1.2
        
        mybonds = numpy.zeros(self.carbon_lattice.npoints*2*maxbonds, NPI)

        clib.calc_carbon_bonds.restype = ctypes.c_int
        nbonds=clib.calc_carbon_bonds(ctypes.c_int(self.carbon_lattice.npoints),
                                            self.carbon_lattice.pos.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                                            mybonds.ctypes.data_as(ctypes.POINTER(ctypes.c_int)),
                                            ctypes.c_double(cutoff))
        
        self.nbonds =   nbonds
        self.bonds =   mybonds     
        self.has_carbon_bonds = True

    def calculate_surface_area_volume(self):
        try:
            self.ring_info['nrings']
        except:
            printl("no rings detects cannot calc surface area and vol")
            self.volume=0
            self.surface_area=0
            return
        
        if(self.ring_info['nrings']==0):
            printl("no rings detects cannot calc surface area and vol")
            self.volume=0
            self.surface_area=0
            return
        
        printl("using nrings",self.ring_info['nrings'],"to determine area and volume")
        '''
        was going to retriangulate the carbon atoms, but there is no need since the
        rings have been calculated. Use these along with the normals to determine the
        volume using Gauss' thereom.    
        '''
        stime = time.time()
        self.surface_area,self.volume = ringcalculator.calculate_volume_from_rings(self.carbon_lattice,
                                                                                  self.ring_info['nrings'],
                                                                                  self.ring_info['MaxVerts'],
                                                                                  self.ring_info['Rings'],
                                                                                  self.ring_info['VertsPerRingCount'])
        
        
        printl("surface_area",self.surface_area,"volume", self.volume)
        printl("C time for vol calc",time.time()-stime)
    
        
    def reset(self,seed=None):
        self.construct_dual_lattice(N_dual=self.dual_lattice.npoints,seed=seed)
            
    def get_dual_lattice_energy(self):
        return float(self.dual_lattice.final_energy)
    
    def get_carbon_lattice_energy(self):
        try:
            if(abs(self.carbon_lattice.final_energy)<1e-5):return float(self.dual_lattice.final_energy)
            else:return float(self.carbon_lattice.final_energy)
        except: 0
        
    def get_carbon_lattice_energy_per_atom(self):
        try:return float(self.carbon_lattice.final_energy)/self.carbon_lattice.npoints
        except: return 0
        
    def get_carbon_lattice_scale(self):
        try:return float(self.carbon_lattice.final_scale)
        except: return 0
        
    def get_carbon_lattice_scaled_energy(self):
        try:return float(self.carbon_lattice.final_scaled_energy)
        except: return 0