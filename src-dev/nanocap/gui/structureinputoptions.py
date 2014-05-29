'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Apr 29, 2014
Copyright Marc Robinson  2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

input options for each type of structure

this is used in the structure search window
and the main structure options window

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
'''

from nanocap.core.globals import *
import os,sys,math,copy,random,time,threading,Queue,types
import numpy

from nanocap.gui.settings import *
from nanocap.gui.common import *
from nanocap.core import globals
from nanocap.core.util import *
import nanocap.gui.structuretable as structuretable
import nanocap.gui.progresswidget as progresswidget
from nanocap.gui.widgets import BaseWidget,HolderWidget,SpinBox,DoubleSpinBox

from nanocap.structures import fullerene
from nanocap.structures import cappednanotube

from nanocap.core import globals,minimisation,triangulation,minimasearch,structurelog

class NanotubeInputOptions(BaseWidget):
    def __init__(self,structure=None, gen_buttons=False): 
        BaseWidget.__init__(self)
        self.structure = structure
#         self.contentlayout = QtGui.QVBoxLayout(self)
#         self.contentlayout.setContentsMargins(0,0,0,0)
#         self.contentlayout.setSpacing(0)
#         self.contentlayout.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
# 
#         self.setLayout(self.contentlayout)
                
        self.holder = BaseWidget(group=False,title="",show=False, align = QtCore.Qt.AlignHCenter)
         
        self.addWidget(self.holder)
        
        grid = self.holder.newGrid(align=QtCore.Qt.AlignTop,spacing=5)
        self.nanotube_n_entry = SpinBox(10)
        self.nanotube_m_entry = SpinBox(10)
        self.nanotube_l_entry = DoubleSpinBox(20)
        self.nanotube_u_entry = SpinBox(1)
        grid.addWidget(HolderWidget([QL("n"),self.nanotube_n_entry],align=QtCore.Qt.AlignRight),0,0)
        grid.addWidget(HolderWidget([QL("m"),self.nanotube_m_entry,],align=QtCore.Qt.AlignLeft),0,1)        
        
        self.length_group = QtGui.QButtonGroup()
        self.length_group.setExclusive(True)
        
        self.finite_cb = QtGui.QRadioButton("Finite")
        self.finite_cb.setChecked(True)
        self.periodic_cb = QtGui.QRadioButton("Periodic")
        self.connect(self.finite_cb,QtCore.SIGNAL("clicked()"),self.change_length_type)
        self.connect(self.periodic_cb,QtCore.SIGNAL("clicked()"),self.change_length_type)
        
        self.length_group.addButton(self.finite_cb)
        self.length_group.addButton(self.periodic_cb)
        
        grid.addWidget(self.finite_cb,1,0,2,1,QtCore.Qt.AlignRight)
        grid.addWidget(self.periodic_cb,1,1,2,1)
        
        self.finite_widgets =[QL("Length (Angs)"),self.nanotube_l_entry]
        
        grid.addWidget(self.finite_widgets[0],3,0,QtCore.Qt.AlignRight)
        grid.addWidget(self.finite_widgets[1],3,1)

        self.periodic_widgets =[QL("Unit cells"),self.nanotube_u_entry]
        
        grid.addWidget(self.periodic_widgets[0],3,0,QtCore.Qt.AlignRight)
        grid.addWidget(self.periodic_widgets[1],3,1)

        for widget in self.periodic_widgets:widget.hide()
        
        if(gen_buttons):
            bt = QtGui.QPushButton("Initialise")
            #bt.setFixedWidth(80)
            self.connect(bt, QtCore.SIGNAL('clicked()'), self.initialise_structure)
            self.holder.addWidget(HolderWidget(bt),align=QtCore.Qt.AlignCenter)
    
    def change_length_type(self):
        if(self.finite_cb.isChecked()):
            for widget in self.periodic_widgets:widget.hide()
            for widget in self.finite_widgets:widget.show()
        else:
            for widget in self.finite_widgets:widget.hide()
            for widget in self.periodic_widgets:widget.show()
            
    def initialise_structure(self):
        n,m = self.nanotube_n_entry.value(),self.nanotube_m_entry.value()
        l = self.nanotube_l_entry.value()
        u = self.nanotube_u_entry.value()
        p = self.periodic_cb.isChecked()
        if(self.structure==None):
            self.structure = nanotube.Nanotube()
        
        self.structure.construct(n,m,length=l,units=u,periodic=p)
        
        
        self.structure.render_update()
        
    def set_options_from_structure(self,structure):
        self.nanotube_n_entry.setValue(structure.n)
        self.nanotube_m_entry.setValue(structure.m)
        self.nanotube_l_entry.setValue(structure.length)
        self.nanotube_u_entry.setValue(structure.unit_cells)

class CappedNanotubeInputOptions(BaseWidget):
    def __init__(self,structure=None, gen_buttons=False): 
        BaseWidget.__init__(self)
        self.structure = structure

        self.holder = BaseWidget(group=False,show=True,title="",align=QtCore.Qt.AlignTop)

        self.addWidget(self.holder)
        
        grid = self.holder.newGrid()
        self.nanotube_n_entry = SpinBox(10)
        self.nanotube_m_entry = SpinBox(10)
        self.nanotube_l_entry = DoubleSpinBox(20)
        
        grid.addWidget(HolderWidget([QL("n"),self.nanotube_n_entry,QL("m")]),0,0)
        grid.addWidget(HolderWidget([self.nanotube_m_entry,]),0,1)        
        grid.addWidget(QL("Length (Angs)"),1,0)
        grid.addWidget(self.nanotube_l_entry,1,1)

        self.cap_estimate_ck = QtGui.QCheckBox("Estimate Cap Atoms")
        self.cap_estimate_ck.setChecked(True)
        grid.addWidget(self.cap_estimate_ck,3,2,2,1)

        self.cap_carbon_atoms_entry = SpinBox()
        self.cap_carbon_atoms_entry.setMaximum(9999999)
        self.cap_carbon_atoms_entry.setValue(60)
        self.cap_carbon_atoms_entry.setSingleStep(2)
        grid.addWidget(QL("Cap Carbon Atoms"),3,0)
        grid.addWidget(self.cap_carbon_atoms_entry,3,1)

        self.connect(self.cap_carbon_atoms_entry, QtCore.SIGNAL('valueChanged(int)'), self.cap_carbon_atoms_changed)
        
        lb = QtGui.QLabel("Dual Lattice Points")
        self.cap_dual_lattice_points_entry = SpinBox()
        self.cap_dual_lattice_points_entry.setMaximum(9999999)
        self.cap_dual_lattice_points_entry.setValue(32)
        
        self.connect(self.cap_dual_lattice_points_entry, QtCore.SIGNAL('valueChanged(int)'), self.cap_dual_lattice_points_changed)
        
        grid.addWidget(QL("Cap Dual Lattice Points"),4,0)#,alignment=QtCore.Qt.AlignRight)
        grid.addWidget(self.cap_dual_lattice_points_entry,4,1,alignment=QtCore.Qt.AlignLeft)
        

        
        self.cap_dual_lattice_seed_entry = SpinBox()
        self.cap_dual_lattice_seed_entry.setMaximum(9999999)
        self.cap_dual_lattice_random_seed_cb = QtGui.QCheckBox("Random")
        self.cap_dual_lattice_random_seed_cb.setChecked(True)      
        grid.addWidget(QL("Seed"),5,0)
        grid.addWidget(self.cap_dual_lattice_seed_entry,5,1)       
        grid.addWidget(self.cap_dual_lattice_random_seed_cb,5,2)

        self.nanotube_custom_force_cutoff_entry = DoubleSpinBox()
        self.nanotube_auto_force_cutoff_cb = QtGui.QCheckBox("Auto Force Cutoff")
        self.nanotube_auto_force_cutoff_cb.setChecked(True)      
        grid.addWidget(QL("Force Cutoff (Angs) "),6,0)
        grid.addWidget(self.nanotube_custom_force_cutoff_entry,6,1)       
        grid.addWidget(self.nanotube_auto_force_cutoff_cb,6,2)
        
        if(gen_buttons):
            bt = QtGui.QPushButton("Initialise")
            bt.setFixedWidth(80)
            self.connect(bt, QtCore.SIGNAL('clicked()'), self.initialise_structure)
            self.holder.addWidget(bt,align=QtCore.Qt.AlignHCenter)
        
    def cap_carbon_atoms_changed(self,val):
        #print val,NDual_from_NAtoms(val,surface="cap")
        self.cap_dual_lattice_points_entry.setValue(NDual_from_NAtoms(val,surface="cap"))
        
    def cap_dual_lattice_points_changed(self,val):
        #print val,NAtoms_from_NDual(val,surface="cap")
        self.cap_carbon_atoms_entry.setValue(NAtoms_from_NDual(val,surface="cap"))
    
    def initialise_structure(self):
        
        n,m = self.nanotube_n_entry.value(),self.nanotube_m_entry.value()
        l = self.nanotube_l_entry.value()
        cap_estimate = self.cap_estimate_ck.isChecked()
        
        if(self.cap_dual_lattice_random_seed_cb.isChecked()):
            seed = random.randint(0,1000000)
            self.cap_dual_lattice_seed_entry.setValue(seed)
        else:
            seed = self.cap_dual_lattice_seed_entry.value()
        
        auto_force_cutoff = self.nanotube_auto_force_cutoff_cb.isChecked()
        custom_force_cutoff = self.nanotube_custom_force_cutoff_entry.value()  
        
        N_cap_dual = self.cap_dual_lattice_points_entry.value()
        
        if(self.structure==None):
            self.structure = cappednanotube.CappedNanotube()
        
        self.structure.setup_nanotube(n,m,l=l)
        
        if(cap_estimate):
            N_cap_dual = self.structure.get_cap_dual_lattice_estimate(n,m)
            self.cap_dual_lattice_points_entry.setValue(N_cap_dual)
        
        self.structure.construct_dual_lattice(N_cap_dual=N_cap_dual,seed=seed)
        self.structure.update_caps()
        
        if(auto_force_cutoff):
            self.structure.set_Z_cutoff(N_cap_dual=N_cap_dual)
        else:
            self.structure.set_Z_cutoff(cutoff=custom_force_cutoff)
            self.nanotube_custom_force_cutoff_entry.setValue(self.structure.cutoff)  
            
        printl("self.structure.nanotube",self.structure.nanotube.carbon_lattice.pos) 
        
        self.structure.render_update()
        
    def set_options_from_structure(self,structure):
        self.cap_dual_lattice_seed_entry.setValue(structure.cap.seed)
        self.dual_lattice_points_entry.setValue(structure.dual_lattice.npoints)
        self.nanotube_n_entry.setValue(structure.n)
        self.nanotube_m_entry.setValue(structure.m)
        self.nanotube_l_entry.setValue(structure.length)

class FullereneInputOptions(BaseWidget):
    def __init__(self,structure=None, gen_buttons=False): 
        BaseWidget.__init__(self)
        self.structure = structure
        
        #self.holder = BaseWidget(group=False,title="",show=True,align=QtCore.Qt.AlignCenter)
        
        #self.addWidget(self.holder)
        
        grid = self.newGrid()

        self.carbon_atoms_entry = SpinBox()
        self.carbon_atoms_entry.setMaximum(9999999)
        self.carbon_atoms_entry.setValue(60)
        self.carbon_atoms_entry.setSingleStep(2)
        #self.carbon_atoms_entry.setFixedWidth(60)  
        grid.addWidget(QL("Carbon Atoms"),0,0)#,alignment=QtCore.Qt.AlignRight)
        grid.addWidget(self.carbon_atoms_entry,0,1)#,alignment=QtCore.Qt.AlignLeft)

        
        lb = QtGui.QLabel("Dual Lattice Points")
        self.dual_lattice_points_entry = SpinBox()
        self.dual_lattice_points_entry.setMaximum(9999999)
        self.dual_lattice_points_entry.setValue(32)
        #self.dual_lattice_points_entry.setFixedWidth(60)  
        self.connect(self.dual_lattice_points_entry, QtCore.SIGNAL('valueChanged(int)'), self.dual_lattice_changed)
        self.connect(self.carbon_atoms_entry, QtCore.SIGNAL('valueChanged(int)'), self.carbon_atoms_changed)
        self.dual_lattice_points_entry.setValue(32)
        
        grid.addWidget(QL("Dual Lattice Points"),1,0)#,alignment=QtCore.Qt.AlignRight)
        grid.addWidget(self.dual_lattice_points_entry,1,1,alignment=QtCore.Qt.AlignLeft)
        
        lb = QtGui.QLabel("Seed")
        self.dual_lattice_seed_entry = SpinBox()
        self.dual_lattice_seed_entry.setMaximum(9999999)
        self.dual_lattice_random_seed_cb = QtGui.QCheckBox("random")
        self.dual_lattice_random_seed_cb.setChecked(True)    
        grid.addWidget(QL("Seed"),2,0)#,alignment=QtCore.Qt.AlignRight)
        grid.addWidget(self.dual_lattice_seed_entry,2,1)       
        grid.addWidget(self.dual_lattice_random_seed_cb,2,2)

        lb = QtGui.QLabel("NFixed Equator")
        lb.setFixedWidth(100) 
        self.dual_lattice_n_fixed_equator = SpinBox()
        self.dual_lattice_n_fixed_equator.setMaximum(9999999)
        self.dual_lattice_fix_pole_cb = QtGui.QCheckBox("Fix Pole")
        self.dual_lattice_fix_pole_cb.setChecked(True) 
        grid.addWidget(lb,3,0)
        grid.addWidget(self.dual_lattice_n_fixed_equator,3,1)              
        grid.addWidget(self.dual_lattice_fix_pole_cb,3,2)    
        
        if(self.structure!=None):self.set_options_from_structure(self.structure)
        
        if(gen_buttons):
            bt = QtGui.QPushButton("Initialise")
            self.connect(bt, QtCore.SIGNAL('clicked()'), self.initialise_structure)
            self.addWidget(bt,align=QtCore.Qt.AlignCenter)
            
            
    def initialise_structure(self):
        printl("initialise_structure",self.structure)
        NCarbon = self.carbon_atoms_entry.value()
        use_random_seed = self.dual_lattice_random_seed_cb.isChecked()
        if(use_random_seed):
            seed = random.randint(0,1000000)
            self.dual_lattice_seed_entry.setValue(seed)
        else:
            seed = self.dual_lattice_seed_entry.value()
        
        if(self.structure==None):
            self.structure = fullerene.Fullerene()
        
        fix_pole = self.dual_lattice_fix_pole_cb.isChecked()
        n_fix_equator = self.dual_lattice_n_fixed_equator.value()
        
        self.structure.construct_dual_lattice(N_carbon=NCarbon,seed=seed)
        self.structure.set_fix_pole(fix_pole)    
        self.structure.set_nfixed_to_equator(n_fix_equator)
        self.structure.construct_carbon_lattice()
        self.structure.calculate_carbon_bonds()
        self.structure.calculate_rings()
        
        self.structure.render_update()
         
    def set_options_from_structure(self,structure):
        self.dual_lattice_seed_entry.setValue(structure.seed)
        if(structure.dual_lattice.npoints>0):
            self.dual_lattice_points_entry.setValue(structure.dual_lattice.npoints)
        
    def carbon_atoms_changed(self,val):
        #print val,NDual_from_NAtoms(val,surface="sphere")
        self.dual_lattice_points_entry.setValue(NDual_from_NAtoms(val,surface="sphere"))
        
    def dual_lattice_changed(self,val):
        #print val,NAtoms_from_NDual(val,surface="sphere")
        self.carbon_atoms_entry.setValue(NAtoms_from_NDual(val,surface="sphere"))