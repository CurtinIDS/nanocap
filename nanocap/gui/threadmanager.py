'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Apr 10, 2014
Copyright Marc Robinson  2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

class that handles any threading
be careful with OpenGL instances

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
'''
import Queue,time,threading
from nanocap.gui.settings import *
from nanocap.core.globals import *
from nanocap.core.util import *

class threadManager(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(1)
        self.queue = Queue.Queue()
        self.running=1
        self.start()
        
    def run(self):
        while self.running==1:
            self.processQueue()
            time.sleep(0.1) 
            
    def stop(self):
        self.running=0
        
    def processQueue(self):   
        while self.queue.qsize():
            print "processQueue found item"
            try:
                callable, args, kwargs = self.queue.get(0)
                if(kwargs.has_key('emit')):
                        signal = kwargs["emit"]
                        del kwargs['emit']
                callable(*args, **kwargs)
            except Queue.Empty:
                pass
        
    def submit_to_queue(self,callable, *args, **kwargs):
        self.queue.put((callable, args, kwargs))   

class QThreadManager(QtCore.QThread):
    '''
    lets have an info string that describes the job being threaded
    
    this should only do non-gui, non-rendering processes, such as
    minimisation, triangulation etc. 
    
    '''
    def __init__(self, parent = None):
        QtCore.QThread.__init__(self, parent)
        self.queue = Queue.Queue()
        self.running=1
        self.start()
        
    def stop(self):
        pass
        
    def run(self):
        signal = None
        while self.running==1:
            while self.queue.qsize():
                print "processQueue found item"
                try:
                    callable, args, kwargs = self.queue.get(0)
                    printl("calling",callable,args,kwargs)
                    callable(*args, **kwargs)
                    print("end call",callable,args,kwargs)

                    signal = None
                except Queue.Empty:
                    pass
            time.sleep(0.01)

    def submit_to_queue(self,callable, *args, **kwargs):
        self.queue.put((callable, args, kwargs))  