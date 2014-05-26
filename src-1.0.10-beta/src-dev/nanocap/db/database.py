'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: May 1, 2014
Copyright Marc Robinson  2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

database ops


Tables and Fields from nanocap.core.structuredata



-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
'''
import os,sys,shutil,datetime,copy,numpy
from nanocap.core.globals import *
from nanocap.core.util import *
from nanocap.structures import fullerene,cappednanotube,nanotube
from nanocap.core import minimisation
from nanocap.core.structuredata import *

import sqlite3 as lite

class Database(object):
    def __init__(self):
        self.dbname = os.path.join(CONFIG.opts["Home"],'nanocap.db')
        self.databases = ['nanocap.db']
        self.tables = ['dual_lattices', 'carbon_lattices','rings','users',
                       'dual_lattice_points','carbon_lattice_points','carbon_lattice_points_con']
        
        self.fields = copy.deepcopy(FIELDS)
        self.foreign_keys = {}

        self.foreign_keys['dual_lattice_points'] = ['FOREIGN KEY(dual_lattice_id) REFERENCES dual_lattices(id)',]
        

        self.foreign_keys['carbon_lattice_points'] = ['FOREIGN KEY(carbon_lattice_id) REFERENCES carbon_lattices(id)',]
        

        self.foreign_keys['carbon_lattice_points_con'] = ['FOREIGN KEY(carbon_lattice_id) REFERENCES carbon_lattices(id)',]
        
        self.foreign_keys['users'] = []

        self.foreign_keys['rings'] = ['FOREIGN KEY(dual_lattice_id) REFERENCES dual_lattices(id)',]
        
        self.foreign_keys['dual_lattices'] = ['FOREIGN KEY(parent_dual_lattice_id) REFERENCES dual_lattices(id)',
                                              'FOREIGN KEY(user_id) REFERENCES user(id)',]
        

        self.foreign_keys['carbon_lattices'] = ['FOREIGN KEY(user_id) REFERENCES user(id)',
                                                'FOREIGN KEY(parent_carbon_lattice_id) REFERENCES carbon_lattices(id)',
                                                'FOREIGN KEY(dual_lattice_id) REFERENCES dual_lattices(id)',]
         
    def get_field_column(self,table,tag):
        count = 0
        for field in self.fields[table]:
            if field.tag == tag:return count
            count+=1
        
    
    def get_parent_ids(self,did):
        con = self.connect()
        cur = con.cursor() 
        q = '''
        select dual_lattices.parent_dual_lattice_id 
        from dual_lattices 
        where dual_lattices.id=?
        '''
        cur.execute(q,  (str(did),))
        out = cur.fetchall()
        parent_did = out[0][0]
        
        con = self.connect()
        cur = con.cursor() 
        q = '''
        select carbon_lattices.id 
        from carbon_lattices 
        where carbon_lattices.dual_lattice_id=?
        '''
        cur.execute(q,  (str(parent_did),))
        out = cur.fetchall()
        if(len(out)==0):
            parent_cid=None
        else:parent_cid = out[0][0]
        
        return parent_did,parent_cid
        
    
    def construct_structure(self,dual_lattice_id,carbon_lattice_id=None):
        printl("dual_lattice_id",dual_lattice_id)      
        con = self.connect()
        cur = con.cursor() 
        q = '''
        select dual_lattices.type 
        from dual_lattices 
        where dual_lattices.id=?
        '''
        cur.execute(q,  (str(dual_lattice_id),))
        out = cur.fetchall()
        type = out[0][0]
        #type = self.query(query)[0]
        printl(type)
        
        if(type==STRUCTURE_TYPES[FULLERENE].label):
            structure = fullerene.Fullerene()
        
        if(type==STRUCTURE_TYPES[CAPPEDNANOTUBE].label):
            structure = cappednanotube.CappedNanotube()
        
        if(type==STRUCTURE_TYPES[NANOTUBE].label):
            structure = nanotube.Nanotube()
        if(type==STRUCTURE_TYPES[CAP].label):
            return None
        if(type==STRUCTURE_TYPES[CAP_R].label):
            return None
        
        q = '''
        select dual_lattice_points.x, dual_lattice_points.y, dual_lattice_points.z 
        from dual_lattice_points 
        where dual_lattice_points.dual_lattice_id=?
        '''
        printl(q,str(dual_lattice_id))
        cur.execute(q,  (str(dual_lattice_id),))
        out = cur.fetchall()
        
        pos = numpy.array(out)
        pos = pos.flatten()
        
        structure.set_dual_lattice(len(pos)/3,pos)
        
        q = '''
        select dual_lattices.force_cutoff,dual_lattices.ff_id, dual_lattices.optimiser , dual_lattices.energy, dual_lattices.n, dual_lattices.m,
        dual_lattices.user_id
        from dual_lattices 
        where dual_lattices.id=?
        '''
        printl(q,str(dual_lattice_id))
        cur.execute(q,  (str(dual_lattice_id),))
        out = cur.fetchall()
        force_cutoff = out[0][0]
        ff_id = out[0][1]
        optimiser = out[0][2]
        energy = out[0][3]
        n = out[0][4]
        m = out[0][5]
        user_id = out[0][6]
        structure.cutoff = force_cutoff
        structure.dual_lattice.final_energy=energy        
        structure.dual_lattice_minimiser = minimisation.DualLatticeMinimiser(ff_id,structure = structure)
        structure.dual_lattice_minimiser.min_type = optimiser    
        structure.dual_lattice_user_id = user_id                                         
        if(type==STRUCTURE_TYPES[CAPPEDNANOTUBE].label):
            structure.nanotube.n=n
            structure.nanotube.m=m
        
        q = '''
        select users.user_name
        from users
        where users.id=?
        '''
        cur.execute(q,  (str(structure.dual_lattice_user_id),))    
        out = cur.fetchall()    
        print q,  (str(structure.dual_lattice_user_id),)
        structure.dual_lattice_user_name = out[0][0]
            
        #now child structures dual lattices
        
        if(structure.has_child_structures):
            q = '''
            select type, id
            from dual_lattices 
            where parent_dual_lattice_id=?
            '''
            printl(q,str(dual_lattice_id))
            cur.execute(q,  (str(dual_lattice_id),))
            out = cur.fetchall()
            
            for o in out:
                child_type, child_dual_lattice_id = o
                q = '''
                select dual_lattice_points.x, dual_lattice_points.y, dual_lattice_points.z 
                from dual_lattice_points 
                where dual_lattice_points.dual_lattice_id=?
                '''
                printl(q,str(child_dual_lattice_id))
                cur.execute(q,  (str(child_dual_lattice_id),))
                out2 = cur.fetchall()
                
                pos = numpy.array(out2)
                pos = pos.flatten()
                
                if(child_type==STRUCTURE_TYPES[NANOTUBE].label):
                    structure.nanotube.set_dual_lattice(len(pos)/3,pos)
                if(child_type==STRUCTURE_TYPES[CAP].label):
                    structure.cap.set_dual_lattice(len(pos)/3,pos)
                if(child_type==STRUCTURE_TYPES[CAP_R].label):
                    structure.reflected_cap.set_dual_lattice(len(pos)/3,pos)
        
        #now carbon lattices
        
        if(carbon_lattice_id!=None):
            q = '''
            select x, y, z 
            from carbon_lattice_points 
            where carbon_lattice_points.carbon_lattice_id=?
            '''
            printl(q,str(dual_lattice_id))
            cur.execute(q,  (str(carbon_lattice_id),))
            out = cur.fetchall()
            
            pos = numpy.array(out)
            pos = pos.flatten()
            structure.set_carbon_lattice(len(pos)/3,pos)
            structure.calculate_rings()
            structure.calculate_carbon_bonds()
            
            q = '''
            select x, y, z 
            from carbon_lattice_points_con 
            where carbon_lattice_points_con.carbon_lattice_id=?
            '''
            printl(q,str(dual_lattice_id))
            cur.execute(q,  (str(carbon_lattice_id),))
            out = cur.fetchall()
            
            pos = numpy.array(out)
            pos = pos.flatten()
            structure.set_con_carbon_lattice(len(pos)/3,pos)
            
            
            q = '''
            select carbon_lattices.ff_id, carbon_lattices.optimiser , carbon_lattices.energy, 
            carbon_lattices.length, carbon_lattices.uncapped_length, carbon_lattices.scale, 
            carbon_lattices.energy_constrained,carbon_lattices.energy_units,carbon_lattices.n,
            carbon_lattices.m,carbon_lattices.periodic,carbon_lattices.periodic_length,
            carbon_lattices.unit_cells,carbon_lattices.user_id
            from carbon_lattices 
            where carbon_lattices.id=?
            '''
            cur.execute(q,  (str(carbon_lattice_id),))
            out = cur.fetchall()
            ff_id = out[0][0]
            optimiser = out[0][1]
            energy = out[0][2]
            length = out[0][3]
            uncapped_length = out[0][4]
            scale = out[0][5]
            energy_constrained = out[0][6]
            energy_units = out[0][7]
            n = out[0][8]
            m = out[0][9]
            periodic = out[0][10]
            periodic_length = out[0][11]
            unit_cells = out[0][12] 
            user_id  = out[0][13]
            
            structure.periodic = periodic
            structure.periodic_length = periodic_length
            structure.unit_cells = unit_cells
            structure.m,structure.n = m,n
            structure.carbon_lattice.final_scale = scale
            structure.carbon_lattice.final_scaled_energy = energy_constrained
            structure.carbon_lattice.final_energy=energy        
            structure.carbon_lattice_minimiser = minimisation.CarbonLatticeMinimiser(ff_id,structure = structure)
            structure.carbon_lattice_minimiser.min_type = optimiser     
            structure.carbon_lattice_minimiser.FF.energy_units    = energy_units  
            structure.carbon_lattice_user_id = user_id
            
            printl("type",type,STRUCTURE_TYPES[CAPPEDNANOTUBE].label)
            #raw_input()
            if(type==STRUCTURE_TYPES[CAPPEDNANOTUBE].label):
                structure.nanotube.length=uncapped_length 
                printl("setting nanotube length")
            if(type==STRUCTURE_TYPES[NANOTUBE].label):
                structure.length=uncapped_length 
                printl("setting nanotube length")    #raw_input()
            
            q = '''
            select users.user_name
            from users
            where users.id=?
            '''
            cur.execute(q,  (str(structure.carbon_lattice_user_id),))    
            out = cur.fetchall()    
            structure.carbon_lattice_user_name = out[0][0]
            #now child carbon lattices
            
            if(structure.has_child_structures):
                q = '''
                select type, id
                from carbon_lattices 
                where parent_carbon_lattice_id=?
                '''
                print q,str(carbon_lattice_id)
                cur.execute(q,  (str(carbon_lattice_id),))
                out = cur.fetchall()
                
                for o in out:
                    type, id = o
                    q = '''
                    select carbon_lattice_points.x, carbon_lattice_points.y, carbon_lattice_points.z 
                    from carbon_lattice_points 
                    where carbon_lattice_points.carbon_lattice_id=?
                    '''
                    print q,str(id)
                    cur.execute(q,  (str(id),))
                    out2 = cur.fetchall()
                    
                    pos = numpy.array(out2)
                    pos = pos.flatten()
                    
                    if(type==STRUCTURE_TYPES[NANOTUBE].label):
                        structure.nanotube.set_carbon_lattice(len(pos)/3,pos)
                    if(type==STRUCTURE_TYPES[CAP].label):
                        structure.cap.set_carbon_lattice(len(pos)/3,pos)
                    if(type==STRUCTURE_TYPES[CAP_R].label):
                        structure.reflected_cap.set_carbon_lattice(len(pos)/3,pos)
            
        structure.database=self.dbname
        printl( structure)
        return structure
        
    def init(self,db=None):
        if(db==None):self.dbname = CONFIG.opts["LocalDatabase"]
        else:self.dbname=db

        if not (os.path.exists(self.dbname)):
            self.create_database()
        
        if not self.check_tables():
            self.create_tables()
        
        self.add_user()

    def check_tables(self):
        query = "SELECT * FROM sqlite_master WHERE type='table'"
               
        con = self.connect()
        cur = con.cursor()    
        cur.execute(query)
        out = cur.fetchall()
        printl("check tables",out)
        con.close()  
        if len(out)==0:return False
        else: return True
    
    def query(self,*args):
        if(len(args)==1):
            sql = args[0]
            printl("sql",sql)
            con = self.connect()
            cur = con.cursor() 
            cur.execute(sql)    
            out = cur.fetchall()
        if(len(args)==2):
            sql,data = args[0],args[1]
            printl("sql",sql)
            con = self.connect()
            cur = con.cursor() 
            cur.execute(sql,tuple(data))    
            out = cur.fetchall()
        return out
            
    def make_backup(self):
        dbname = os.path.join(CONFIG.opts["Home"],'nanocap.db')
        
        shutil.copy(dbname,dbname+'.bk')
    
    def set_database(self,db):
        self.dbname = db
    
    def connect(self):
        printl("connecting",self.dbname)
        con = lite.connect(self.dbname,detect_types=lite.PARSE_DECLTYPES)
        return con
    
    def delete_database(self,db=None):
        if(db==None):dbname = os.path.join(CONFIG.opts["Home"],'nanocap.db')
        else:dbname=db
        os.remove(dbname) 
                
    def create_database(self):
        con = self.connect()
        con.close()  
        self.create_tables()
        
    def create_tables(self):
        con = self.connect()
        cur = con.cursor()    
        for table in self.tables:
            cur.execute("DROP TABLE IF EXISTS {}".format(table))
            cmd = "CREATE TABLE {}".format(table)
            cmd += "("
            for field in self.fields[table]:
                print field
                cmd += "{} {},".format(field.tag,field.dtype)
            for fkey in self.foreign_keys[table]:
                print fkey
                cmd += "{},".format(fkey)    
            cmd = cmd[:-1]
            cmd += ")"
            printl("cmd",cmd)
            cur.execute(cmd)
        
        
        con.commit()  
        con.close()  
        
    def add_user(self):
        con = self.connect()
        cur = con.cursor() 
        cur.execute('SELECT * FROM users WHERE user_name=?',(CONFIG.opts['User'],))
        out = cur.fetchall()
        printl(out)
        if len(out)>0:
            printl("user already found in database, will not add")
            con.close()  
            return
        else:
            cur.execute("INSERT INTO users VALUES(?,?,?)",(None,CONFIG.opts['User'],CONFIG.opts['Email']))
            con.commit()
            con.close()  

    
    def check_carbon_lattice_duplicates(self,structure):
        printl("checking carbon lattice duplicates")        
        con = self.connect()
        cur = con.cursor() 
        structure_data = structure.get_structure_data()
        
        if(structure.type==FULLERENE):
            tables = ["carbon_lattices"]
            selects = ["*",]
            checks = {}
            checks["carbon_lattices"] = ['type','natoms','energy','ff_id']
                     
            sql,data = self.construct_query(structure_data,tables,selects,checks,extra=[])  
            
            printl("SQL",sql,data)
            cur.execute(sql,tuple(data))
            out = cur.fetchall()
            printl(out,len(out))
            if len(out)>0:   
                tables = ["carbon_lattices"]
                selects = ["energy",]
                checks = {}
                checks["carbon_lattices"] = ['type','natoms','energy','ff_id']
                         
                sql,data = self.construct_query(structure_data,tables,selects,checks,extra=[])  
                printl("SQL",sql)
                cur.execute(sql,tuple(data))
                out = cur.fetchall()
                printl("found duplicate carbon lattice",out)
                con.close()   
                return True
            else:
                tables = ["carbon_lattices"]
                selects = ["energy",]
                checks = {}
                checks["carbon_lattices"] = ['type','natoms','ff_id']
                         
                sql,data = self.construct_query(structure_data,tables,selects,checks,extra=[])  


                printl("SQL",sql,tuple(data))
                cur.execute(sql,tuple(data))
                
                #cur.execute('SELECT energy FROM carbon_lattices WHERE type=? AND natoms=? AND ff_id=?',(structure.type.label,npoints,ff_id))    
                out = cur.fetchall()
                printl(out)
                for s in out:
                    diff = abs(structure.dual_lattice.final_energy-s[0])
                    if(diff<1e-8):
                        printl("duplicate carbon lattice found in database",out[0][0],"diff",diff)
                        con.close()   
                        return True
                con.close()   
                printl("carbon lattice structure not found in database",out)
                return False
        
        if(structure.type==NANOTUBE):
#             npoints = structure.carbon_lattice.npoints
#             uncapped_length = structure.length
#             n,m = structure.n,structure.m
            
#             tables = ["carbon_lattices",]
#             
#             table = "carbon_lattices"
#             selects = ["*",]
#             checks = ['uncapped_length','natoms','m','n']
#             ws = []
#             data = []
#             for check in checks: 
#                 if(structure_data[table][check]==None):
#                     ws.append(table+"."+check+" is ?")
#                 else:
#                     ws.append(table+"."+check+"=?")
#                 data.append(structure_data[table][check])
#                 
#             sql = 'SELECT {} FROM {} WHERE '.format(",".join(selects),",".join(tables),) + " AND ".join(ws)
            tables = ["carbon_lattices"]
            selects = ["*",]
            checks = {}
            checks["carbon_lattices"] = ['uncapped_length','natoms','m','n']
                 
            sql,data = self.construct_query(structure_data,tables,selects,checks,extra=[])  

            printl("SQL",sql)
            cur.execute(sql,tuple(data))
            
            
#             cur.execute('SELECT * FROM dual_lattices, carbon_lattices WHERE dual_lattices.id =carbon_lattices.dual_lattice_id AND \
#                          dual_lattices.type=? AND carbon_lattices.natoms=? AND carbon_lattices.uncapped_length=? AND carbon_lattices.n=? AND carbon_lattices.m=?',
#                         (structure.type.label,npoints,uncapped_length,n,m))    
            #printl(structure.type.label,npoints,uncapped_length,n,m)
            out = cur.fetchall()
            if len(out)>0:
                printl("duplicate carbon lattice found in database",out)
                con.close()   
                return True
            
        if(structure.type==CAPPEDNANOTUBE):

#             npoints = structure.carbon_lattice.npoints
#             cenergy = structure.get_carbon_lattice_energy()
#             try:ff_id = structure.carbon_lattice_minimiser.FFID
#             except:ff_id = None
#             n_cap=structure.cap.carbon_lattice.npoints
#             n_tube=structure.nanotube.carbon_lattice.npoints
#             uncapped_length = structure.nanotube.length
#             n,m=structure.nanotube.n,structure.nanotube.m
# #             cur.execute('SELECT * FROM dual_lattices, carbon_lattices WHERE dual_lattices.id =carbon_lattices.dual_lattice_id AND \
# #                          dual_lattices.type=? AND dual_lattices.energy=? AND dual_lattices.npoints=? AND dual_lattices.n_cap=? AND dual_lattices.n_tube=? AND carbon_lattices.uncapped_length=?',
# #                         (structure.type.label,denergy,npoints,n_cap,n_tube,uncapped_length))    
#             
#             cur.execute('SELECT energy FROM carbon_lattices WHERE \
#                          carbon_lattices.type=? AND carbon_lattices.natoms=? \
#                          AND carbon_lattices.n_cap=? AND carbon_lattices.n_tube=? AND carbon_lattices.uncapped_length=? \
#                          AND ff_id=? AND n=? AND m=?',
#                         (structure.type.label,npoints,n_cap,n_tube,uncapped_length,ff_id,n,m)) 
#             printl(structure.type.label,npoints,n_cap,n_tube,uncapped_length,ff_id,n,m)
            
#             tables = ["carbon_lattices",]
#             
#             table = "carbon_lattices"
#             selects = ["energy",]
#             checks = ['type','uncapped_length','natoms','m','n','n_cap','n_tube','ff_id']
#             ws = []
#             data = []
#             for check in checks: 
#                 if(structure_data[table][check]==None):
#                     ws.append(table+"."+check+" is ?")
#                 else:
#                     ws.append(table+"."+check+"=?")
#                 data.append(structure_data[table][check])
#                 
#             sql = 'SELECT {} FROM {} WHERE '.format(",".join(selects),",".join(tables),) + " AND ".join(ws)
#             
            tables = ["carbon_lattices"]
            selects = ["energy",]
            checks = {}
            checks["carbon_lattices"] = ['type','uncapped_length','natoms','m','n','n_cap','n_tube','ff_id']
                 
            sql,data = self.construct_query(structure_data,tables,selects,checks,extra=[])  
            
            printl("SQL",sql)
            cur.execute(sql,tuple(data))

            out = cur.fetchall()
            printl(out)
            for s in out:
                diff = abs(structure.get_carbon_lattice_energy()-s[0])
                if(diff<1e-8):
                    printl("duplicate carbon lattice found in database",out[0][0],"diff",diff)
                    con.close()   
                    return True
            
#             if len(out)>0:
#                 printl("duplicate found in database",out)
#                 con.close()   
#                 return True
#             else:
            con.close()
            printl("carbon lattice structure not found in database",out)   
            return False
    
    def construct_query(self,structure_data,tables,selects,checks,extra=[]):
        ws = []
        data = []
        for table in tables:
            for check in checks[table]: 
                if(structure_data[table][check]==None):
                    ws.append(table+"."+check+" is ?")
                else:
                    ws.append(table+"."+check+"=?")
                data.append(structure_data[table][check])
        wstring =   " AND ".join(extra+ws)      
        sql = 'SELECT {} FROM {} WHERE {}'.format(",".join(selects),",".join(tables),wstring) 
        return sql,data
    
    def check_dual_lattice_duplicates(self,structure):
        printl("checking dual lattice duplicates")
        con = self.connect()
        cur = con.cursor() 
        structure_data = structure.get_structure_data()
        
        if(structure.type==FULLERENE):
#             npoints = structure.dual_lattice.npoints
#             denergy = structure.get_dual_lattice_energy()
#             cur.execute('SELECT * FROM dual_lattices WHERE type=? AND energy=? AND npoints=?',(structure.type.label,denergy,npoints))   
#             tables = ["dual_lattices",]
#             
#             table = "dual_lattices"
#             selects = ["*",]
#             checks = ['energy','npoints','type']
#             ws = []
#             data = []
#             for check in checks: 
#                 if(structure_data[table][check]==None):
#                     ws.append(table+"."+check+" is ?")
#                 else:
#                     ws.append(table+"."+check+"=?")
#                 data.append(structure_data[table][check])
#                 
#             sql = 'SELECT {} FROM {} WHERE '.format(",".join(selects),",".join(tables),) + " AND ".join(ws)
            tables = ["dual_lattices"]
            selects = ["*",]
            checks = {}
            checks["dual_lattices"] = ['type','npoints','energy']
                     
            sql,data = self.construct_query(structure_data,tables,selects,checks,extra=[])  
            
            printl("SQL",sql)
            cur.execute(sql,tuple(data))
 
            out = cur.fetchall()
            printl(out)
            if len(out)>0:
#                 printl("duplicate found in database",out)
#                 tables = ["dual_lattices",]
#             
#                 table = "dual_lattices"
#                 selects = ["energy",]
#                 checks = ['type','npoints']
#                 ws = []
#                 data = []
#                 for check in checks: 
#                     if(structure_data[table][check]==None):
#                         ws.append(table+"."+check+" is ?")
#                     else:
#                         ws.append(table+"."+check+"=?")
#                     data.append(structure_data[table][check])
#                     
#                 sql = 'SELECT {} FROM {} WHERE '.format(",".join(selects),",".join(tables),) + " AND ".join(ws)
#                 
                
                tables = ["dual_lattices"]
                selects = ["energy",]
                checks = {}
                checks["dual_lattices"] = ['type','npoints']
                         
                sql,data = self.construct_query(structure_data,tables,selects,checks,extra=[])  
                
                printl("SQL",sql)
                cur.execute(sql,tuple(data))
            
                #cur.execute('SELECT energy FROM dual_lattices WHERE type=? AND npoints=?',(structure.type.label,npoints))    
                out = cur.fetchall()
                printl(out)
                con.close()   
                return True
            else:
                #cur.execute('SELECT energy FROM dual_lattices WHERE type=? AND npoints=?',(structure.type.label,npoints)) 
#                 tables = ["dual_lattices",]
#             
#                 table = "dual_lattices"
#                 selects = ["energy",]
#                 checks = ['type','npoints']
#                 ws = []
#                 data = []
#                 for check in checks: 
#                     if(structure_data[table][check]==None):
#                         ws.append(table+"."+check+" is ?")
#                     else:
#                         ws.append(table+"."+check+"=?")
#                     data.append(structure_data[table][check])
#                     
#                 sql = 'SELECT {} FROM {} WHERE '.format(",".join(selects),",".join(tables),) + " AND ".join(ws)
#                 printl("SQL",sql)
                tables = ["dual_lattices"]
                selects = ["energy",]
                checks = {}
                checks["dual_lattices"] = ['type','npoints']
                         
                sql,data = self.construct_query(structure_data,tables,selects,checks,extra=[])  
                
                cur.execute(sql,tuple(data))
                   
                out = cur.fetchall()
                for s in out:
                    diff = abs(structure.dual_lattice.final_energy-s[0])
                    if(diff<1e-8):
                        printl("duplicate found in database",out[0][0],"diff",diff)
                        con.close()   
                        return True
                con.close()   
                printl("structure not found in database",out)
                return False
        
        if(structure.type==NANOTUBE):
#             npoints = structure.dual_lattice.npoints
#             uncapped_length = structure.length
#             n,m = structure.n,structure.m
            
            tables = ["dual_lattices","carbon_lattices"]
            selects = ["*",]
            checks = {}
            checks["dual_lattices"] = ['type','npoints']
            checks["carbon_lattices"] = ['type','m','n','uncapped_length']
                   
            sql,data = self.construct_query(structure_data,tables,selects,checks,extra=["dual_lattices.id =carbon_lattices.dual_lattice_id",])  
            
#             tables = ["dual_lattices","carbon_lattices"]
#             ws = []
#             data = []
#             selects = ["*",]
#                         
#             table = "dual_lattices"
#             checks = ['type','npoints']
#             for check in checks: 
#                 if(structure_data[table][check]==None):
#                     ws.append(table+"."+check+" is ?")
#                 else:
#                     ws.append(table+"."+check+"=?")
#                 data.append(structure_data[table][check])
#             
#             table = "carbon_lattices"
#             checks = ['m','n','uncapped_length']
#             for check in checks: 
#                 if(structure_data[table][check]==None):
#                     ws.append(table+"."+check+" is ?")
#                 else:
#                     ws.append(table+"."+check+"=?")
#                 data.append(structure_data[table][check])
#                 
#             sql = 'SELECT {} FROM {} WHERE dual_lattices.id =carbon_lattices.dual_lattice_id AND '.format(",".join(selects),",".join(tables),) + " AND ".join(ws)
#             printl("SQL",sql)
            cur.execute(sql,tuple(data))
                
            
            #cur.execute('SELECT * FROM dual_lattices, carbon_lattices WHERE dual_lattices.id =carbon_lattices.dual_lattice_id AND \
            #             dual_lattices.type=? AND dual_lattices.npoints=? AND carbon_lattices.uncapped_length=? AND carbon_lattices.n=? AND carbon_lattices.m=?',
            #            (structure.type.label,npoints,uncapped_length,n,m))    
            
            out = cur.fetchall()
            if len(out)>0:
                printl("duplicate found in database",out)
                con.close()   
                return True
            
        if(structure.type==CAPPEDNANOTUBE):
#             npoints = structure.dual_lattice.npoints
#             denergy = structure.get_dual_lattice_energy()
#             n_cap=structure.cap.dual_lattice.npoints
#             n_tube=structure.nanotube.dual_lattice.npoints
#             uncapped_length = structure.nanotube.length
#             cur.execute('SELECT * FROM dual_lattices, carbon_lattices WHERE dual_lattices.id =carbon_lattices.dual_lattice_id AND \
#                          dual_lattices.type=? AND carbon_lattices.type=? AND dual_lattices.energy=? AND dual_lattices.npoints=? AND \
#                            dual_lattices.n_cap=? AND dual_lattices.n_tube=? AND carbon_lattices.uncapped_length=?',
#                         (structure.type.label,structure.type.label,denergy,npoints,n_cap,n_tube,uncapped_length))   
#             tables = ["dual_lattices","carbon_lattices"]
#             ws = []
#             data = []
#             selects = ["*",]
#                         
#             table = "dual_lattices"
#             checks = ['type','npoints','n_cap','n_tube','energy']
#             for check in checks: 
#                 if(structure_data[table][check]==None):
#                     ws.append(table+"."+check+" is ?")
#                 else:
#                     ws.append(table+"."+check+"=?")
#                 data.append(structure_data[table][check])
#             
#             table = "carbon_lattices"
#             checks = ['type','m','n','uncapped_length']
#             for check in checks: 
#                 if(structure_data[table][check]==None):
#                     ws.append(table+"."+check+" is ?")
#                 else:
#                     ws.append(table+"."+check+"=?")
#                 data.append(structure_data[table][check])
#             
#             sql = 'SELECT {} FROM {} WHERE dual_lattices.id =carbon_lattices.dual_lattice_id AND '.format(",".join(selects),",".join(tables),) + " AND ".join(ws)
#             
            tables = ["dual_lattices","carbon_lattices"]
            selects = ["*",]
            checks = {}
            checks["dual_lattices"] = ['type','npoints','n_cap','n_tube','energy']
            checks["carbon_lattices"] = ['type','m','n','uncapped_length']
                   
            sql,data = self.construct_query(structure_data,tables,selects,checks,extra=["dual_lattices.id =carbon_lattices.dual_lattice_id",])  
            
            printl("SQL",sql)
            cur.execute(sql,tuple(data))
            
            out = cur.fetchall()
            printl(out)
            if len(out)>0:
                printl("duplicate found in database",out)
                con.close()   
                return True
            else:

#                 ws = []
#                 data = []                            
#                 table = "dual_lattices"
#                 checks = ['type','npoints','n_cap','n_tube']
#                 for check in checks: 
#                     if(structure_data[table][check]==None):
#                         ws.append(table+"."+check+" is ?")
#                     else:
#                         ws.append(table+"."+check+"=?")
#                     data.append(structure_data[table][check])
#                 
#                 table = "carbon_lattices"
#                 checks = ['type','m','n','uncapped_length']
#                 for check in checks: 
#                     if(structure_data[table][check]==None):
#                         ws.append(table+"."+check+" is ?")
#                     else:
#                         ws.append(table+"."+check+"=?")
#                     data.append(structure_data[table][check])
                
                tables = ["dual_lattices","carbon_lattices"]
                selects = ["dual_lattices.energy", "carbon_lattices.uncapped_length"]
                checks = {}
                checks["dual_lattices"] = ['type','npoints','n_cap','n_tube']
                checks["carbon_lattices"] = ['type','m','n','uncapped_length']
                       
                sql,data = self.construct_query(structure_data,tables,selects,checks,extra=["dual_lattices.id =carbon_lattices.dual_lattice_id",])    
                #sql =  'SELECT {} FROM {} WHERE dual_lattices.id =carbon_lattices.dual_lattice_id AND'+  
                
                #sql = 'SELECT {} FROM {} WHERE dual_lattices.id =carbon_lattices.dual_lattice_id AND '.format(",".join(selects),",".join(tables),) + " AND ".join(ws)
                printl("SQL",sql,tuple(data))
                cur.execute(sql,tuple(data))
                
#                 cur.execute('SELECT dual_lattices.energy, carbon_lattices.uncapped_length FROM dual_lattices, carbon_lattices WHERE dual_lattices.id =carbon_lattices.dual_lattice_id AND \
#                          dual_lattices.type=? AND carbon_lattices.type=? AND dual_lattices.npoints=? AND dual_lattices.n_cap=? AND dual_lattices.n_tube=?',
#                          (structure.type.label,structure.type.label,npoints,n_cap,n_tube))  
#                 printl('SELECT dual_lattices.energy FROM dual_lattices, carbon_lattices WHERE dual_lattices.id =carbon_lattices.dual_lattice_id AND \
#                          dual_lattices.type=? AND carbon_lattices.type=? AND dual_lattices.npoints=? AND dual_lattices.n_cap=? AND dual_lattices.n_tube=? AND carbon_lattices.uncapped_length=?',
#                         (structure.type.label,structure.type.label,npoints,n_cap,n_tube,uncapped_length))  
                out = cur.fetchall()
                printl(out)
                for s in out:
                    tenergy,tlength = s
                    diff = abs(structure.dual_lattice.final_energy-tenergy)
                    diff2 = abs(structure_data['carbon_lattices']['uncapped_length']-tlength)
                    if(diff<1e-8 and diff2<1e-8):
                        printl("duplicate found in database",out[0],"diff",diff)
                        con.close()   
                        return True
                con.close()
                printl("structure not found in database",out)   
                return False
    
    def add_carbon_lattice_structure(self,structure):
        self.add_structure(structure, add_dual_lattice=False,add_carbon_lattice=True)
          
    def add_dual_lattice_structure(self,structure):    
        self.add_structure(structure, add_dual_lattice=True,add_carbon_lattice=False)
    
    
    def get_dual_lattice_id(self,structure,cur=None):
        if(cur==None):
            con = self.connect()
            cur = con.cursor() 
        
        structure_data = structure.get_structure_data()
        type = structure_data['dual_lattices']['type']
        npoints = structure_data['dual_lattices']['npoints']
        
        if(structure.parent_structure!=None):
            #we have a child structure which has no energy to compare, have to look for parent ID
            
            cur.execute('SELECT id,parent_dual_lattice_id FROM dual_lattices WHERE type=? AND npoints=? ',(type,npoints)) 
            out = cur.fetchall()
            parent_id = self.get_dual_lattice_id(structure.parent_structure, cur)
            for o in (out):
                 id,pid=o
                 if(pid==parent_id):
                     return id
            
        
        #if(structure.dual_lattice.final_energy)
            
        cur.execute('SELECT id,energy FROM dual_lattices WHERE type=? AND npoints=? ',(type,npoints)) 
        out = cur.fetchall()
        printl(out)
        for o in (out):
            id,e = o
            if(abs(e-structure.dual_lattice.final_energy)<1e-8):
                printl("id found",id)    
                return id
        else:
            printl("could not find dual lattice id, maybe the dual lattice hasnt been added to the db yet?")
            return None
    
    def add_structure(self,structure,add_dual_lattice=True,add_carbon_lattice=False):
        if(add_carbon_lattice):
            if(self.check_carbon_lattice_duplicates(structure)):
                printl("carbon lattice exists, assuming dual lattice exists")
                return    
        self.make_backup()
        self.add_user()
        
        
        if(add_dual_lattice):  
            if(self.check_dual_lattice_duplicates(structure)):
                dual_lattice_id = self.get_dual_lattice_id(structure)
            else:
                dual_lattice_id = self.add_dual_lattice(structure)
        else:
            dual_lattice_id = self.get_dual_lattice_id(structure)
            if(dual_lattice_id==None):
                printl("cannot add carbon lattice without associated dual lattice...")
                return
            
        if(add_carbon_lattice):
            if(self.check_carbon_lattice_duplicates(structure)):return      
            carbon_lattice_id = self.add_carbon_lattice(structure,dual_lattice_id)
    
    def get_user_id(self,uname=None):
        if(uname==None):uname = CONFIG.opts['User']
        con = self.connect()
        cur = con.cursor() 
        cur.execute('SELECT * FROM users WHERE user_name=?',(CONFIG.opts['User'],))
        out = cur.fetchall()        
        user_id = out[0][0]
        con.close()
        return user_id
            
    def add_dual_lattice(self,structure,parent_dual_lattice_id=None):  
        user_id = self.get_user_id()
              
        con = self.connect()
        cur = con.cursor() 

        structure_data = structure.get_structure_data()
        
        table = 'dual_lattices'
        
        structure_data[table]['user_id'] =  user_id
        structure_data[table]['parent_dual_lattice_id'] =  parent_dual_lattice_id
        
        cols = []
        data = []
        printl(self.fields)
        for field in self.fields[table]:
            cols.append(field.tag)
            data.append(structure_data[table][field.tag])
            
        data = tuple(data)
        cols = tuple(cols)
        printl("cols",cols)
        printl("data",data)
 
        #if(add_dual_lattice):
        datamask = "("+ ",".join(["?"]*len(data))+")"
        colmask = "("+ ",".join(cols)+")"                                                            
        cur.execute("INSERT INTO {table} {cols} VALUES {vals}".format(table=table,
                                                                      cols=colmask,
                                                                      vals=datamask),data)
        
        dual_lattice_id = cur.lastrowid
        
        table = 'dual_lattice_points'
        x,y,z = structure_data[table]['x'],structure_data[table]['y'],structure_data[table]['z']
        for i in range(0,structure.dual_lattice.npoints):
            data = (  dual_lattice_id,
                      float(x[i]),
                      float(y[i]),
                      float(z[i]))
            mask = "("+ ",".join(["?"]*len(data))+")"
            cur.execute("INSERT INTO {} VALUES{}".format(table,mask),data)
        
        table = 'rings'
        structure_data[table]['dual_lattice_id'] =  dual_lattice_id
        cols = []
        data = []
        printl(self.fields)
        for field in self.fields[table]:
            cols.append(field.tag)
            data.append(structure_data[table][field.tag])
            
        data = tuple(data)
        cols = tuple(cols)
        datamask = "("+ ",".join(["?"]*len(data))+")"
        colmask = "("+ ",".join(cols)+")"                                                            
        cur.execute("INSERT INTO {table} {cols} VALUES {vals}".format(table=table,
                                                                      cols=colmask,
                                                                      vals=datamask),data)

        
        con.commit()
        con.close()  
        
        
        if(structure.has_child_structures):
            parent_dual_lattice_id = dual_lattice_id            
            for child_structure in structure.get_child_structures():
                child_dual_lattice_id = self.add_dual_lattice(child_structure,parent_dual_lattice_id)
        
        printl("added dual_lattice_id",dual_lattice_id)
        return dual_lattice_id

    def add_carbon_lattice(self,structure,dual_lattice_id,parent_carbon_lattice_id=None):
        user_id = self.get_user_id()
        
        con = self.connect()
        cur = con.cursor() 
        
        table = 'carbon_lattices'       
        
        structure_data = structure.get_structure_data()
        structure_data[table]['user_id'] =  user_id
        structure_data[table]['dual_lattice_id'] =  dual_lattice_id
        structure_data[table]['parent_carbon_lattice_id'] =  parent_carbon_lattice_id
         
        cols = []
        data = []
        printl(self.fields)
        for field in self.fields[table]:
            cols.append(field.tag)
            data.append(structure_data[table][field.tag])
            
        data = tuple(data)
        cols = tuple(cols)
        
        datamask = "("+ ",".join(["?"]*len(data))+")"
        colmask = "("+ ",".join(cols)+")"  
        cur.execute("INSERT INTO {table} {cols} VALUES {vals}".format(table=table,
                                                                      cols=colmask,
                                                                      vals=datamask),data)
        
        carbon_lattice_id = cur.lastrowid
    
    
        table = 'carbon_lattice_points'
        x,y,z = structure_data[table]['x'],structure_data[table]['y'],structure_data[table]['z']
        for i in range(0,structure.carbon_lattice.npoints):
           data = (  carbon_lattice_id,
                     float(x[i]),
                     float(y[i]),
                     float(z[i]))
           mask = "("+ ",".join(["?"]*len(data))+")"
           cur.execute("INSERT INTO {} VALUES{}".format(table,mask),data)
        
        try: 
           table = 'carbon_lattice_points_con'
           x,y,z = structure_data[table]['x'],structure_data[table]['y'],structure_data[table]['z']
           for i in range(0,structure.carbon_lattice.npoints):
               data = (  carbon_lattice_id,
                         float(x[i]),
                         float(y[i]),
                         float(z[i]))
               mask = "("+ ",".join(["?"]*len(data))+")"
               cur.execute("INSERT INTO {} VALUES{}".format(table,mask),data)
        except:pass
        
        con.commit()
        con.close()
        
        if(structure.has_child_structures):
            parent_carbon_lattice_id = carbon_lattice_id         
            for child_structure in structure.get_child_structures():
                child_dual_lattice_id = self.add_carbon_lattice(child_structure,dual_lattice_id,parent_carbon_lattice_id)

        
        
        printl("added carbon_lattice_id",carbon_lattice_id)    
        return carbon_lattice_id 
                

if __name__=="__main__":
    if(len(sys.argv)>1):
        if sys.argv[1]=="delete":
            db = Database()
            db.delete_database()    
            