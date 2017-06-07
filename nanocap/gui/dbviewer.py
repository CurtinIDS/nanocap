'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: May 7, 2014
Copyright Marc Robinson  2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

Window to view the current status of 
a database


-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
'''


from nanocap.core.globals import *
import os,sys,math,copy,random,time,threading,Queue,types,re
import numpy

from nanocap.gui.settings import *
from nanocap.gui.common import *
from nanocap.core.util import *
import nanocap.gui.structuretable as structuretable
import nanocap.gui.progresswidget as progresswidget
import nanocap.gui.structureinputoptions as structureinputoptions
import nanocap.gui.minimiserinputoptions as minimiserinputoptions 

from nanocap.gui.frozencoltablewidget import FrozenTableWidget
from nanocap.gui.tablebuttondelegate import  TableItemDelegate
from nanocap.gui.widgets import BaseWidget,HolderWidget

from nanocap.structures import fullerene
from nanocap.structures import cappednanotube

from nanocap.core import minimisation,triangulation,minimasearch,structurelog

from nanocap.db import database

class DataBaseTable(QtGui.QWidget):
    def __init__(self,database):
        QtGui.QWidget.__init__(self)
        self.setSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Expanding)
        
        self.database = database     
        self.general_table = FrozenTableWidget(NFrozen=1,
                                             DelegateIcons=[[0,1,'view_1.png'],
                                                            ]
                                             )
        self.general_table.frozenTableView.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.general_table.tableView.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        #self.general_table.setFixedWidth(100)
        
        
        
        self.users_table = FrozenTableWidget(NFrozen=0,
                                             DelegateIcons=[]
                                             )
                
        self.dual_lattice_table = FrozenTableWidget(NFrozen=0,
                                             DelegateIcons=[]
                                             )
        self.carbon_lattice_table = FrozenTableWidget(NFrozen=0,
                                             DelegateIcons=[]
                                             )

        self.rings_table = FrozenTableWidget(NFrozen=0,
                                             DelegateIcons=[]
                                             )
        
        
        self.tables = {}
        self.tables['users'] = self.users_table
        self.tables['dual_lattices'] = self.dual_lattice_table
        self.tables['carbon_lattices'] = self.carbon_lattice_table
        self.tables['rings'] = self.rings_table
        
        
        
        self.general_table.setStretchLastSection(True)
        self.users_table.setStretchLastSection(False)
        self.dual_lattice_table.setStretchLastSection(False)
        self.carbon_lattice_table.setStretchLastSection(False)
        self.rings_table.setStretchLastSection(False)
        #self.general_table.setMinimumWidth(30)
        
        self.general_table.setHeaders(["View",])
        
        self.headers = {}
        self.headers['users']=[]
        self.headers['dual_lattices']=[]
        self.headers['carbon_lattices']=[]
        self.headers['rings']=[]
        
        for field in self.database.fields['users']:self.headers['users'].append(field.__repr__())      
        self.users_table.setHeaders(self.headers['users'])

        for field in self.database.fields['dual_lattices']:self.headers['dual_lattices'].append(field.__repr__())      
        self.dual_lattice_table.setHeaders(self.headers['dual_lattices'])

        for field in self.database.fields['carbon_lattices']:self.headers['carbon_lattices'].append(field.__repr__())      
        self.carbon_lattice_table.setHeaders(self.headers['carbon_lattices'])

        for field in self.database.fields['rings']:self.headers['rings'].append(field.__repr__())      
        self.rings_table.setHeaders(self.headers['rings'])
           
                
        self.contentlayout = QtGui.QGridLayout(self)
        self.contentlayout.setContentsMargins(5,5,5,5)
        self.contentlayout.setSpacing(0)
        self.contentlayout.setAlignment(QtCore.Qt.AlignHCenter)
        self.setLayout(self.contentlayout)
        
        self.splitter = QtGui.QSplitter()
        self.splitter.setChildrenCollapsible(False)
        self.splitter.addWidget(HolderWidget([QL("",header=True,align=QtCore.Qt.AlignCenter),self.general_table],stack="V"))
        self.splitter.addWidget(HolderWidget([QL("User",header=True,align=QtCore.Qt.AlignCenter),self.users_table],stack="V"))
        self.splitter.addWidget(HolderWidget([QL("Dual Lattice",header=True,align=QtCore.Qt.AlignCenter),self.dual_lattice_table],stack="V"))
        self.splitter.addWidget(HolderWidget([QL("Carbon Lattice",header=True,align=QtCore.Qt.AlignCenter),self.carbon_lattice_table],stack="V"))
        self.splitter.addWidget(HolderWidget([QL("Rings",header=True,align=QtCore.Qt.AlignCenter),self.rings_table],stack="V"))
        self.splitter.setHandleWidth(1)
        self.contentlayout.addWidget(self.splitter,0,0)
        
        #self.general_table.setMinimumWidth(self.general_table.sizeHint().width()) 
        self.general_table.setMinimumWidth(50)
        
        self.general_table.link_table(self.users_table)
        self.users_table.link_table(self.dual_lattice_table)
        self.dual_lattice_table.link_table(self.carbon_lattice_table)
        self.carbon_lattice_table.link_table(self.rings_table)
         
        self.connect(self.general_table,QtCore.SIGNAL("delegatePressed(QModelIndex)"),self.viewStructure)
        
        self.show()
        
    def clear(self):
        self.carbon_lattice_table.reset()   
        self.rings_table.reset()   
        self.general_table.reset()   
        self.dual_lattice_table.reset()   
        self.users_table.reset()   
        
    def populate(self,search_params,orderby,order):
        self.user_ids=[]
        self.dual_lattice_ids=[]
        self.carbon_lattice_ids=[]
        
        args = []
        for key,val in search_params.items():
             p = re.compile('[<=>]')
             a =p.findall(str(val))
             printl(a)
             if(len(a)==0):
                 operator="="
                 comp = val
             else:
                 operator="".join(a)
                 comp = val
                 for ai in a: comp=comp.replace(str(ai)," ")
             
             args.append(key+operator+"'"+str(comp)+"'")
             
        if(len(args)==0):wherestring=""
        else:wherestring = "where " + ' and '.join(args)
        printl("wherestring",wherestring)
        
        sort_string = "order by {} {}".format(orderby,order)
        
        query = '''
        select users.*
        from users 
        inner join dual_lattices on dual_lattices.user_id=users.id 
        left outer join carbon_lattices on carbon_lattices.dual_lattice_id=dual_lattices.id
        left outer join rings on rings.dual_lattice_id=dual_lattices.id
        '''+wherestring+" "+sort_string + ";"
        
        #where dual_lattices.type='Fullerene' or dual_lattices.type='Capped Nanotube';
        
        out = self.database.query(query)
        for row in out:
            self.users_table.addRow(row)
            self.user_ids.append(row[self.database.get_field_column('users','id')]) 
            
        query = '''
        select dual_lattices.*
        from users 
        inner join dual_lattices on dual_lattices.user_id=users.id 
        left outer join carbon_lattices on carbon_lattices.dual_lattice_id=dual_lattices.id
        left outer join rings on rings.dual_lattice_id=dual_lattices.id
        '''+wherestring+" "+sort_string + ";"
        out = self.database.query(query)
        for row in out:
            printl(row)
            self.dual_lattice_table.addRow(row)
            self.dual_lattice_ids.append(row[self.database.get_field_column('dual_lattices','id')]) 
        
        query = '''
        select carbon_lattices.*
        from users 
        inner join dual_lattices on dual_lattices.user_id=users.id 
        left outer join carbon_lattices on carbon_lattices.dual_lattice_id=dual_lattices.id
        left outer join rings on rings.dual_lattice_id=dual_lattices.id
        '''+wherestring+" "+sort_string + ";"
        out = self.database.query(query)
        for row in out:
            self.carbon_lattice_table.addRow(row)
            self.carbon_lattice_ids.append(row[self.database.get_field_column('carbon_lattices','id')]) 
        query = '''
        select rings.*
        from users 
        inner join dual_lattices on dual_lattices.user_id=users.id 
        left outer join carbon_lattices on carbon_lattices.dual_lattice_id=dual_lattices.id
        left outer join rings on rings.dual_lattice_id=dual_lattices.id
        '''+wherestring+" "+sort_string + ";"
        
        out = self.database.query(query)
        for row in out:
            self.rings_table.addRow(row)
        #print out
        for row in out:
            self.general_table.addRow(["null",])
        
         
    def viewStructure(self,index):
        col,row = index.column(),index.row()
        self.emit(QtCore.SIGNAL("viewStructure(int)"),row)    
      
    def sizeHint(self):
 
        return QtCore.QSize(1200,500)
    
class DataBaseViewerWindow(BaseWidget):
    def __init__(self,Gui,MainWindow,ThreadManager):
        self.Gui = Gui
        self.MainWindow = MainWindow
        self.ThreadManager = ThreadManager
        BaseWidget.__init__(self,self.MainWindow,show=False)
        self.setWindowTitle("Database Viewer")
        
        self.props_defaults = ["users.user_name",
                               "users.user_email",
                               "users.id","rings.rings_3",
                               "rings.rings_4",
                               "rings.rings_5",
                               "rings.rings_6",
                               "rings.rings_7",
                               "rings.rings_8",
                               "carbon_lattices.optimiser",
                               "carbon_lattices.energy",
                               "carbon_lattices.energy_constrained",
                               "carbon_lattices.energy_units",
                               "carbon_lattices.energy_per_atom",
                               "carbon_lattices.type",
                               "carbon_lattices.natoms",
                               "carbon_lattices.n_cap",
                               "carbon_lattices.n",
                               "carbon_lattices.m",
                               "carbon_lattices.date",
                               "carbon_lattices.ff_id",
                               "dual_lattices.npoints",
                               "dual_lattices.optimiser",
                               "dual_lattices.seed",
                               "dual_lattices.type",
                               "dual_lattices.n_cap",
                               "dual_lattices.m",
                               "dual_lattices.n",
                               ]
 
        self.nrows = 7
        self.wfactor = 1.1
        
        
        self.setSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Preferred)
        
        self.database = database.Database()
        
        self.banner_holder = BaseWidget(self,group=True,title="Search Properties",name="H1",
                                                        show=True)
        
        self.table_holder = BaseWidget(self,group=True,title="Search Results",name="H1",
                                                        show=True)
        
        #self.addWidget(QL("Search Properties",name="H1"))
        self.addWidget(self.banner_holder)
        #self.addWidget(QL("Search Results",name="H1"))
        self.addWidget(self.table_holder)
        
        self.table = DataBaseTable(self.database)
        self.table_holder.addWidget(self.table)
        
        self.connect(self.table, QtCore.SIGNAL('viewStructure(int)'), self.viewStructure)
        
        self.setup_search_buttons()
        
        self.database.init()
        
        self.banner_holder.show()
        self.table_holder.show()
        
        for table in ['users','dual_lattices','carbon_lattices','rings']:    self.table.tables[table].hide_all_columns()
        
        for key in self.props_defaults:
            table,field = key.split(".")
            self.show_column(table, field)
        
        #self.table.populate({})
    
    def setup_search_buttons(self):
    
        self.draw_prop_entries()
        
        self.order_by_cb = QtGui.QComboBox()
        keys= numpy.sort(numpy.array(self.entries.keys()))
               
        
        grid = self.banner_holder.newGrid()
        
        
        for key in keys:
            self.order_by_cb.addItem(key)
        
        grid.addWidget(HolderWidget([QL("Sort by"),self.order_by_cb]),0,2,10,1)
        
        self.order_cb = QtGui.QComboBox()
        for key in ["Asc","Desc"]:
            self.order_cb.addItem(key)
        
        grid.addWidget(HolderWidget([QL("Order"),self.order_cb]),0,4,10,1)
        
        self.search_bt = QtGui.QPushButton("Search")
        self.connect(self.search_bt, QtCore.SIGNAL('clicked()'), self.new_search)
        #self.banner_holder.addWidget(self.search_bt)
        grid.addWidget(self.search_bt,0,10,10,1)
        
        
        self.clear_bt = QtGui.QPushButton("Clear")
        self.connect(self.clear_bt, QtCore.SIGNAL('clicked()'), self.clear_filters)
        #self.banner_holder.addWidget(self.search_bt)
        grid.addWidget(self.clear_bt,0,11,10,1)
        
        
        self.props_bt = QtGui.QPushButton("Select Properties")
        
        #self.banner_holder.addWidget(self.search_bt)
        grid.addWidget(self.props_bt,0,1,10,1)
        
        
        self.props_window = BaseWidget(popup=True,title="Structure Properties",w=300,h=400,scroll=True,group=False,show=False)
        
        self.connect(self.props_bt, QtCore.SIGNAL('clicked()'), self.props_window.bringToFront)
        
        self.propCB = {}
        for key in keys:
            self.propCB[key] = QtGui.QCheckBox(key)
            
            if(key in self.props_defaults):
                self.propCB[key].setChecked(True)
                #self.toggle_property(True, key)
            else:
                self.propCB[key].setChecked(False)
                #self.toggle_property(False, key)
                
            self.props_window.addWidget(self.propCB[key],align=QtCore.Qt.AlignLeft)
            
            call = lambda flag,key=key : self.toggle_property(flag,key)
            self.connect(self.propCB[key], QtCore.SIGNAL('toggled(bool)'), call)
        
        #self.regrid(table)
        for table in ['users','dual_lattices','carbon_lattices','rings']:    self.regrid(table)
            
        

    def draw_prop_entries(self):
        nrows = self.nrows
        wfactor= self.wfactor
        
        self.holder = {}
        self.grids = {}
        self.entries = {}
        self.labels = {}
        
        holder = HolderWidget(spacing=4,margins=(2,2,2,2))
        for table in ['users','dual_lattices','carbon_lattices','rings']:
            
            self.holder[table] = BaseWidget(self,group=True,title=table,show=True,align=QtCore.Qt.AlignTop,stack="H")
            grid = self.holder[table].newGrid()
            self.grids[table] = grid
            cols = {}
            labs = {}
            for i,field in enumerate(self.database.fields[table]):
                row,col = i % nrows, int(i/nrows)
                self.entries[table+'.'+field.tag] = QtGui.QLineEdit()
                self.entries[table+'.'+field.tag].setFixedWidth(60)

                l = QL(field.__repr__())
                self.labels[table+'.'+field.tag] = l
                try:
                    cols[col].append(l.fontMetrics().boundingRect(l.text()).width())
                    labs[col].append(l)
                except:
                    cols[col] = []
                    cols[col].append(l.fontMetrics().boundingRect(l.text()).width())
                    labs[col] = []
                    labs[col].append(l)

                grid.addWidget(HolderWidget([l,self.entries[table+'.'+field.tag]]),row,col,1,1)
                if(table+'.'+field.tag not in self.props_defaults):
                    l.hide()
                    self.entries[table+'.'+field.tag].hide()
            
            
            for col in cols.keys():
                width = numpy.max(numpy.array(cols[col]))*wfactor
                for lab in labs[col]:lab.setFixedWidth(width)
                
            
            holder.addWidget(self.holder[table])
        
        self.banner_holder.addWidget(holder)
               
    def regrid(self,table):
        nrows = self.nrows
        wfactor= self.wfactor
        grid = self.grids[table]
        cols = {}
        labs = {}
        count = 0
        for i,field in enumerate(self.database.fields[table]):
            #printl(table,field,table+'.'+field.tag,"checked:",self.propCB[table+'.'+field.tag].isChecked())
            if not self.propCB[table+'.'+field.tag].isChecked():continue
            row,col = count % nrows, int(count/nrows)
            l = self.labels[table+'.'+field.tag]
            try:
                cols[col].append(l.fontMetrics().boundingRect(l.text()).width())
                labs[col].append(l)
            except:
                cols[col] = []
                cols[col].append(l.fontMetrics().boundingRect(l.text()).width())
                labs[col] = []
                labs[col].append(l)
                
            grid.addWidget(HolderWidget([l,self.entries[table+'.'+field.tag]]),row,col,1,1)
            
            for col in cols.keys():
                width = numpy.max(numpy.array(cols[col]))*wfactor
                for lab in labs[col]:lab.setFixedWidth(width)
            count+=1
            
        if(count==0):
            self.holder[table].hide()
        else:
            self.holder[table].show()
        
    def toggle_property(self,flag,key):
        table,field = key.split(".")
        if(flag):
            self.entries[key].show()
            self.labels[key].show()
            self.show_column(table,field)
        else:
            self.entries[key].hide()
            self.labels[key].hide()
            self.hide_column(table,field)
            
        self.regrid(table)
        
    
    def hide_column(self,table,field):
        printl("hiding",table,field)
        for tfield in self.database.fields[table]:
            printl(tfield.__repr__(),tfield.tag)
            if(str(tfield.tag)==str(field)):
                printl("found")
                self.table.tables[table].hide_column_from_header(tfield.__repr__())
                return
   
    def show_column(self,table,field):
        for tfield in self.database.fields[table]:
            if(tfield.tag==field):
                self.table.tables[table].show_column_from_header(tfield.__repr__())
                return
             
    def clear_filters(self):
        for entry in self.entries.values():
            entry.clear()
        
    def new_search(self):
        self.database.init()
        self.table.clear()
        
        search_params = {}
        for key,entry in self.entries.items():
            
            val = str(entry.text()).strip()
            printl(key,val)
            if len(val) == 0: continue
            else: search_params[key] = val
            
        orderby = self.order_by_cb.currentText()
        order = self.order_cb.currentText()
        
        
        #self.database.set_database(self.database_entry.text())    
        self.table.populate(search_params,orderby,order)
        
    def viewStructure(self,row):
        #get structure from database row in self.table
        
        
#        
        uid,did,cid = self.table.user_ids[row],self.table.dual_lattice_ids[row],self.table.carbon_lattice_ids[row]
        structure  = self.database.construct_structure(did,cid)
        
        if(structure==None):
            #structure  = self.database.get_parent_structure(did)
            did,cid = self.database.get_parent_ids(did)
            printl("parent ids",did,cid)
            structure  = self.database.construct_structure(did,cid)
        
        if(structure==None):return
        printl("clicked",row,uid,did,cid)
        self.MainWindow.activateWindow()   
        self.MainWindow.gui.dock.toolbar.structurelist.addStructure(structure) 
            
    def bringToFront(self):
        #self.raise_()
        self.setWindowState( (self.windowState() & ~QtCore.Qt.WindowMinimized) | QtCore.Qt.WindowActive)
        self.raise_()
        self.activateWindow()
        self.show()
        
    def sizeHint(self):

        return QtCore.QSize(800,500)       