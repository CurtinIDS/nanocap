'''
-=-=-=-=-=-=-= NanoCap =-=-=-=-=-=-=-=
Created: Aug 1 2013
Copyright Marc Robinson 2013
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

NanoCap config class.

Holds user info and databse locations

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
'''
import getpass,os,copy

class Config(object):
    def __init__(self):
        self.opts={}
        self.setDefaults()
    
    def setDefaults(self):
        self.opts["User"] = getpass.getuser()
        self.opts["Email"] = ""
        self.opts["Home"] = os.path.join(os.path.expanduser("~"),".nanocap")
        if not (os.path.exists(self.opts["Home"])):
            printl("NanoCap Home does not exist, creating...",self.opts["Home"])
            os.mkdir(self.opts["Home"])
            
        self.opts["LocalDatabase"] = os.path.join(self.opts["Home"],'nanocap.db')
        self.defaults = copy.deepcopy(self.opts)
        
    def setLocalDatabase(self,db=None):
        if(uname!=None):self.opts["LocalDatabase"] = db
        else:self.opts["LocalDatabase"] = os.path.join(self.opts["Home"],'nanocap.db')
    
    def setEmail(self,uname=None):
        if(uname!=None):self.opts["Email"] = uname
        else:self.opts["Email"] = ""
    
    def setUser(self,uname=None):
        if(uname!=None):self.opts["User"] = uname
        else:self.opts["User"] = getpass.getuser()
        #printl("set NanoCap User:",self.opts["User"])
        
    def setHomeDir(self,dir=None):
        if(dir!=None):self.opts["Home"] = dir
        else:self.opts["Home"] = os.path.join(os.path.expanduser("~"),".nanocap")
        #printl("set NanoCap Home:",self.opts["Home"])

        if not (os.path.exists(self.opts["Home"])):
            printl("NanoCap Home does not exist, creating...",self.opts["Home"])
            os.mkdir(self.opts["Home"])
            
    def __str__(self):
        string = "NanoCap Config: \n"
        for key in sorted(self.opts.iterkeys()):
            string+= "%s: %s\n" % (key, self.opts[key])
        return string
    

            