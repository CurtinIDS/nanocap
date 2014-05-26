'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: May 10, 2014
Copyright Marc Robinson  2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

Unified Structure Data that can be easily
manipulated for SQL

Also used by the StructureLog and the GUI

If the database(s) are deleted, this 
can be modified to add new columns(fields)
to the db.

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
'''

import os,sys,shutil,datetime,numpy
from nanocap.core.globals import *
from nanocap.core.util import *

class Field(object):
    '''
    a data field has: sql_tag, sql_dtype, label, default
    '''
    def __init__(self,sql_tag, sql_dtype, label=None,default=None):
        self.tag=sql_tag
        self.dtype=sql_dtype
        self.default = default
        if(label==None):
            #self.label = sql_tag.replace('_'," ")
            #self.label = self.label[0].capitalize() + self.label[1:]
            self.label = self.pretify(sql_tag)
        else:self.label=label
        
    @staticmethod
    def pretify(label):
        label = label.replace('_'," ")
        label = label[0].capitalize() + label[1:]
        return label
    
    def _pretify(self,label):
        return pretify.__func__(pretify)
#         label = label.replace('_'," ")
#         label = label[0].capitalize() + label[1:]
#         return label
    
    
        
    def __repr__(self):
        return str(self.label) 
    
    def get_yaml(self):
        return {"tag":self.tag,"dtype":self.dtype, "label":self.label}
         

DATA_TABLES = ['dual_lattices', 
               'carbon_lattices',
               'rings','users',
               'dual_lattice_points',
               'carbon_lattice_points',
               'carbon_lattice_points_con']
        
FIELDS = {}
FIELDS['dual_lattice_points'] = [Field('dual_lattice_id', 'INTEGER',default=None),
                                 Field('x', 'REAL',default=numpy.zeros(0,NPF)),
                                 Field('y', 'REAL',default=numpy.zeros(0,NPF)),
                                 Field('z', 'REAL',default=numpy.zeros(0,NPF))
                                 ]

FIELDS['carbon_lattice_points'] = [Field('carbon_lattice_id', 'INTEGER',default=None),
                                   Field('x', 'REAL',default=numpy.zeros(0,NPF)),
                                   Field('y', 'REAL',default=numpy.zeros(0,NPF)),
                                   Field('z', 'REAL',default=numpy.zeros(0,NPF))
                                  ]

FIELDS['carbon_lattice_points_con'] = [Field('carbon_lattice_id', 'INTEGER',default=None),
                                   Field('x', 'REAL',default=numpy.zeros(0,NPF)),
                                   Field('y', 'REAL',default=numpy.zeros(0,NPF)),
                                   Field('z', 'REAL',default=numpy.zeros(0,NPF))
                                  ]

FIELDS['users'] = [Field('id', 'INTEGER PRIMARY KEY AUTOINCREMENT',default=None),
                   Field('user_name', 'TEXT',default=None),
                   Field('user_email', 'TEXT',default=None)
                   ]


FIELDS['rings'] = [Field('id', 'INTEGER PRIMARY KEY AUTOINCREMENT',default=None),
                  Field('rings_3', 'INT',"3",default=0),
                  Field('rings_4', 'INT',"4",default=0),
                  Field('rings_5', 'INT',"5",default=0),
                  Field('rings_6', 'INT',"6",default=0),
                  Field('rings_7', 'INT',"7",default=0),
                  Field('rings_8', 'INT',"8",default=0),
                  Field('dual_lattice_id', 'INTEGER',default=None),
                  ]

FIELDS['dual_lattices'] = [Field('id', 'INTEGER PRIMARY KEY AUTOINCREMENT',default=None),
                            Field('date', 'TIMESTAMP',default=None),
                            Field('user_id', 'INTEGER',default=None),
                            Field('type', 'TEXT',default=None),
                            Field('npoints', 'INT',default=None),
                            Field('n', 'INT',"n",default=None),
                            Field('m', 'INT',"m",default=None),
                            Field('seed', 'INT',default=None),
                            Field('nfixed_equator', 'INT',default=None),
                            Field('fix_pole', 'INT',default=None),
                            Field('n_cap', 'INT',default=None),
                            Field('n_tube', 'INT',default=None),
                            Field('force_cutoff', 'REAL',default=None),
                            Field('energy','REAL',default=None),
                            Field('ff_id','TEXT',"Force Field",default=None),
                            Field('optimiser','REAL',default=None),
                            Field('parent_dual_lattice_id','INTEGER',default=None)]

FIELDS['carbon_lattices'] = [Field('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
                            Field('date', 'TIMESTAMP'),
                            Field('type', 'TEXT'),
                            Field('natoms', 'INT'),
                            Field('n', 'INT',"n"),
                            Field('m', 'INT',"m"),
                            Field('length', 'REAL'),
                            Field('uncapped_length', 'REAL'),
                            Field('n_cap', 'INT'),
                            Field('n_tube', 'INT'),
                            Field('ff_id', 'TEXT',"Force Field"),
                            Field('ff_options', 'TEXT',"Force Field Options"),
                            Field('optimiser', 'TEXT'),
                            Field('energy', 'REAL'),
                            Field('energy_constrained', 'REAL'),
                            Field('energy_units', 'TEXT'),
                            Field('energy_per_atom', 'REAL'),
                            Field('scale','REAL'),
                            Field('periodic','INT'),
                            Field('periodic_length','REAL'),
                            Field('unit_cells','INT'),
                            Field('user_id', 'INTEGER'),
                            Field('dual_lattice_id', 'INTEGER'),
                            Field('parent_carbon_lattice_id','INTEGER')
                              ]

DEFAULT_DATA  = {}
for table in DATA_TABLES:
    DEFAULT_DATA[table] = {}
    for field in FIELDS[table]:
        DEFAULT_DATA[table][field.tag] = field.default