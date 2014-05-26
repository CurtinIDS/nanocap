'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Oct 3 2013
Copyright Marc Robinson 2013
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

The StructureLog holds the currently
found structures from a structure search

Uses the StructureData to determine the 
columns to display

Has the functionality to compare against 
the local database 

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
'''


from nanocap.core.globals import *
import nanocap.core.globals as globals
from nanocap.structures.structure import Structure
from nanocap.db import database
import os,sys,math,copy,random,time,threading,Queue,ctypes,types
 
import numpy
from nanocap.core.util import *
from nanocap.core.structuredata import *

import sqlite3
        
class StructureLog(object):
    def __init__(self,type):
        self.structures = []
        self.type = type
        self.lastAdded = None
        self.locklog = False
        printl("StructureLog",type)
        self.logpad = 4

        self.general_headers = ["ID",]
        self.dual_lattice_headers = [ field.tag for field in FIELDS['dual_lattices']]
        self.carbon_lattice_headers = [ field.tag for field in FIELDS['carbon_lattices']] 
        self.rings_headers= [ field.tag for field in FIELDS['rings']] 

    def reset(self):
        self.structures = []
    
    def check_for_uniqueness(self,instructure):
        unique  = True
        e2 = instructure.dual_lattice.final_energy
        for structure in self.structures:
            e1 = structure.dual_lattice.final_energy
            if(numpy.abs(e1-e2) < numpy.abs(1e-8)):
                 unique  = False 
                 
        return unique
        
    def add_structure(self,structobject,cap=None,
                     NCapDualLattice=None,NTubeDualLattice=None,NCapCarbonAtoms=None,
                     NTubeCarbonAtoms=None,rings=None):
        
        self.locklog = True
        printl(self.type) 
        structure = copy.deepcopy(structobject)

        self.lastAdded = len(self.structures)
        self.structures.append(structure)
        
        self.locklog = False
        printl("structure added")
    
    def compare_dual_lattice_local_database(self,structure):
        printl("compare_structure_local_database")
        db = database.Database()
        db.init()
        duplicates = db.check_dual_lattice_duplicates(structure)
        return duplicates
        
    def add_dual_lattice_local_database(self,structure):
        printl("add_structure_local_database")
        db = database.Database()
        db.add_dual_lattice_structure(structure)
    
    def compare_carbon_lattice_local_database(self,structure):
        printl("compare_structure_local_database")
        db = database.Database()
        db.init()
        duplicates = db.check_carbon_lattice_duplicates(structure)
        return duplicates
        
    def add_carbon_lattice_local_database(self,structure):
        printl("add_structure_local_database")
        db = database.Database()
        db.init()
        db.add_carbon_lattice_structure(structure)
        
    def get_data(self,i):
        while(self.locklog):
            pass
        
        structure =self.structures[i]
        structure_data = structure.get_structure_data()
 
        data = {}
        data['general']= [i,]
        for table in DATA_TABLES:
            #printl(table,structure_data[table])
            data[table] = [ structure_data[table][field.tag] for field in FIELDS[table]] 
            
            #printl("getting data from structure",table,data[table])
            
        #printl(len(data),data)
        return data    
    
    def get_structure_at_position(self,index,sorted=False):
        if(sorted):return self.structures[self.get_sorted_indexes()[index]]
        else:return self.structures[index]
        
    def get_sorted_indexes(self):
        while(self.locklog):
            pass
        
        energies = numpy.zeros(len(self.structures))
        for index,structure in enumerate(self.structures):
            #energies[index] = numpy.sum(structure.dual_lattice.energy)
            energies[index] = structure.get_dual_lattice_energy()
        order = numpy.argsort(energies)
        return order    
    
    def write_log(self,folder,filename="StructureLog.txt"):
        printl("writing log",folder,filename)
#        if os.path.exists(os.path.join(folder,filename)):
        write=False
        while not write:
            try:
                f = open(os.path.join(folder,filename),"w")
                for (title,headers,table) in [('General',self.general_headers,'general'),
                                              ('Dual Lattice',self.dual_lattice_headers,'dual_lattices'),
                                              ('Carbon Lattice',self.carbon_lattice_headers,'carbon_lattices'),
                                              ('Rings',self.rings_headers,'rings')]:
                    print title,headers,table
                    widths = self.get_col_widths(headers, table)
                    print "widths",widths
                    log = self.get_header_string(title,headers,widths)
                    print "get_header_string",log
                    f.write(log)
                    log = self.get_log_string(widths,table)
                    f.write(log)
                    
                f.close()
                write = True                         
            except:
                time.sleep(0.5)
    
    def write_log_old(self,folder,filename="StructureLog.txt",append=False):
        printl("writing log",folder,filename,append)
#        if os.path.exists(os.path.join(folder,filename)):
        write=False
        while not write:
            try:
                if(append):
                    if os.path.exists(os.path.join(folder,filename)):
                        f = open(os.path.join(folder,filename),"a")
                        #log = self.get_log_string()
                        log = self.get_append_log_string()
                        f.write(log)
                        f.close()
                        write = True
                    else:
                        f = open(os.path.join(folder,filename),"w")
                        log = self.get_header_string()
                        f.write(log)
                        log = self.get_log_string()
                        f.write(log)
                        f.close()
                        write = True
                else:
                    f = open(os.path.join(folder,filename),"w")
                    log = self.get_header_string()
                    f.write(log)
                    log = self.get_log_string()
                    f.write(log)
                    f.close()
                    write = True                         
            except:
                time.sleep(0.5)
    
    def get_header_string_old(self):
        printl("get_header_string")
        line1 = ""

        l=0
        for header in self.general_headers:
            l+=len(header)+self.logpad
        
        line1+=("{:^"+str(l)+"}").format('General')    
        
        l=0
        for header in self.dual_lattice_headers:
            l+=len(header)+self.logpad
        line1+=("{:^"+str(l)+"}").format('Dual Lattice')        
        l=0
        for header in self.carbon_lattice_headers:
            l+=len(header)+self.logpad
        line1+=("{:^"+str(l)+"}").format('Carbon Lattice')     
        l=0
        for header in self.rings_headers:
            l+=len(header)+self.logpad
        line1+=("{:^"+str(l)+"}").format('Rings')    
        printl("line1",line1)
        
        
        line2 = ""
        for header in self.general_headers:
            line2+=("{:"+str(len(header)+self.logpad)+"}").format(header)    
        

        for header in self.dual_lattice_headers:
            line2+=("{:"+str(len(header)+self.logpad)+"}").format(header)         

        for header in self.carbon_lattice_headers:
            line2+=("{:"+str(len(header)+self.logpad)+"}").format(header)    
 
        for header in self.rings_headers:
            line2+=("{:"+str(len(header)+self.logpad)+"}").format(header)   
        
        printl(line2)
        log = line1+"\n"+line2

        
        return log
    
    def get_col_widths(self,headers,table):

        col_widths = [ len(header) for header in headers] 
        #print col_widths
        order = self.get_sorted_indexes()
        for i in order:
            data = self.get_data(i)
            data = data[table] 
            #print "data",data
            for j,d in enumerate(data):
                
                if len(str(d))>col_widths[j]: col_widths[j] = len(str(d))
        
        #print "returning",col_widths
        
        return col_widths
    
    def get_header_string(self,title,headers,widths):
        printl("get_header_string",title)
        line1 = ""
        
        
        l=0
        for w in widths:
            l+=w+self.logpad
        
        line1+=("{:^"+str(l)+"}").format(title)+"\n"    
        
        format =""
        for w in widths:
            format +="{:<"+str(w+self.logpad)+"} "  
        
        line2 = ""
        #for w,header in enumerate(headers):
        line2+= (format+"\n").format(*headers)    

        
        printl(line2)
        log = line1+line2

        
        return log
    

    def get_log_string(self,widths,table):
        
        order = self.get_sorted_indexes()
        printl("order",order)
        format =""
        
        for w in widths:
            format +="{:<"+str(w+self.logpad)+"} "   
        
        printl("log string format",format)

        log=""
        for i in order:
            data = self.get_data(i)
            data = data[table]
            data = [ d.strftime("%Y-%m-%d %H:%M:%S")  if isinstance(d, datetime.datetime) else d for d in data]
                    
            
            log+=  (format+"\n").format(*data)
            printl(log)
            
            
        return log 

    def get_append_log_string(self):
        format =""

        for header in self.general_headers:
            format +="{:"+str(len(header)+self.logpad)+"} "   
        for header in self.dual_lattice_headers:
            format +="{:"+str(len(header)+self.logpad)+"} "   
        for header in self.carbon_lattice_headers:
            format +="{:"+str(len(header)+self.logpad)+"} "   
        for header in self.rings_headers:
            format +="{:"+str(len(header)+self.logpad)+"} "   
        
        printl("format",format)
        log=""
        data = self.get_data(len(self.structures)-1)
        data = data['general']+ data['dual_lattices']+ data['carbon_lattices']+ data['rings']
        log+=  (format+"\n").format(*data)
        printl(log)
        return log 

    def get_log_string_old(self):
        
        order = self.get_sorted_indexes()
        printl("order",order)
        format =""

        for header in self.general_headers:
            format +="{:"+str(len(header)+self.logpad)+"} "   
        for header in self.dual_lattice_headers:
            format +="{:"+str(len(header)+self.logpad)+"} "   
        for header in self.carbon_lattice_headers:
            format +="{:"+str(len(header)+self.logpad)+"} "   
        for header in self.rings_headers:
            format +="{:"+str(len(header)+self.logpad)+"} "   
        
        printl("format",format)

        log=""
        for i in order:
            data = self.get_data(i)
            data = data['general']+ data['dual_lattices']+ data['carbon_lattices']+ data['rings']
            log+=  (format+"\n").format(*data)
            printl(log)
            
            
        return log    
        
    def print_log(self):
        return
        log = self.get_header_string()
        log += self.get_log_string()
        print log    
        