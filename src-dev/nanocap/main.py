'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: July 20 2012
Copyright Marc Robinson 2013
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

Main GUI window and threadManagers

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
'''
import sys,os
sys.path.append(os.path.abspath(os.getcwd()+"/../"))
print sys.path
from nanocap.core.globals import *
import os,sys,threading,Queue,types
import nanocap.core.globals
QtGui, QtCore = nanocap.core.globals.QT.QtGui, nanocap.core.globals.QT.QtCore
import numpy

from nanocap.gui.structurewindow import StructureWindow
import nanocap.rendering.vtkqtrenderwidgets as vtkqtrenderwidgets
import nanocap.rendering.objectactors as objectactors
import nanocap.gui.dock as dock 
import nanocap.gui.operations as operations
import nanocap.core.processes as processes
from nanocap.resources import Resources
from nanocap.core.util import *
from nanocap.core import globals
from nanocap.core import util
from nanocap.core import config


class threadManager(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        #self.setDaemon(1)
        self.queue = Queue.Queue()
        self.running=1
        self.start()
        
    def run(self):
        while self.running==1:
            #thread = threading.Thread(target=self.processQueue)
            #thread.setDaemon(1)
            #thread.start()
            self.processQueue()
            time.sleep(0.1) 
            
    def stop(self):
        #self._stop.set()
        self.running=0
        
    def processQueue(self):   
        while self.queue.qsize():

            print "processQueue found item"
            try:
                callable, args, kwargs = self.queue.get(0)
                if(kwargs.has_key('emit')):
                        signal = kwargs["emit"]
                        del kwargs['emit']
                print "callable",callable,args,kwargs
                # Check contents of message and do what it says
                # As a test, we simply print it
                callable(*args, **kwargs)
                #self.vtkframe.VTKRenderWindowInteractor.ReInitialize()
            except Queue.Empty:
                pass
        
    def submit_to_queue(self,callable, *args, **kwargs):
        self.queue.put((callable, args, kwargs))   


class nonThreadManager():
    def __init__(self):
        self.queue = Queue.Queue()        
    def processQueue(self):   
        while self.queue.qsize():
            print "processQueue found item"
            try:
                callable, args, kwargs = self.queue.get(0)
                if(kwargs.has_key('emit')):
                        signal = kwargs["emit"]
                        del kwargs['emit']
                print "callable",callable,args,kwargs
                # Check contents of message and do what it says
                # As a test, we simply print it
                callable(*args, **kwargs)
                #self.vtkframe.VTKRenderWindowInteractor.ReInitialize()
            except Queue.Empty:
                pass
    
    def stop(self):
        pass
        
    def submit_to_queue(self,callable, *args, **kwargs):
        self.queue.put((callable, args, kwargs))   
	self.processQueue()

class QThreadManager(QtCore.QThread):
    #end_call = QtCore.pyqtSignal(object)
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
#                    while(globals.RenderLock):
#                        time.sleep(0.01)

                    #self.end_call.emit(False)
                    
                    callable, args, kwargs = self.queue.get(0)
                    if(kwargs.has_key('emit')):
                        signal = kwargs["emit"]
                        del kwargs['emit']
                        printl("***FOUND SIGNAL",signal)    
                        
                    printl("calling",callable,args,kwargs)
                    callable(*args, **kwargs)
                    print("end call",callable,args,kwargs)
                    
                    #self.end_call.emit(True)
#                    if(signal!=None):
#                        printl("*"*20+"emitting signal",signal)
#                        self.emit(QtCore.SIGNAL(signal))  

                    signal = None
                except Queue.Empty:
                    pass
            time.sleep(0.01)

    def submit_to_queue(self,callable, *args, **kwargs):
        self.queue.put((callable, args, kwargs))  

class QThreadSignalManager(QtCore.QThread):
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
                try:
                    signal= self.queue.get(0)
                    printl("signalQueue found signal",signal)
                    #waitGUIlock()
                    self.emit(QtCore.SIGNAL(signal))  
                except Queue.Empty:
                    pass
            time.sleep(0.01)

    def emitSignal(self,*args,**kwargs):
        printl(args,kwargs)
        signal = kwargs['signal']
        self.queue.put(signal)  

class MDIArea(QtGui.QMdiArea):
    def __init__(self):
        QtGui.QMdiArea.__init__(self)
        
    
    def sizeHint(self):
        return QtCore.QSize(800,700)
     
                  
class gui():    
    def __init__(self,root):
        #threading.Thread.__init__(self)
        #self.root=root
        
        self.config = config.Config()
        self.config.setUser()
        self.config.setHomeDir()
        
        
        self.dockWidth =350
        self.dockHeight = 500
        self.mainwindow = root
        self.mainwidget = QtGui.QWidget(self.mainwindow)
        self.vtklayout = QtGui.QHBoxLayout(self.mainwidget)
        
        self.mdiarea = MDIArea()

        self.vtklayout.addWidget(self.mdiarea)
        
        self.vtkframe = vtkqtrenderwidgets.VtkQtFrame(0, self.mainwindow,self) 
        self.vtkframe.hide()
        print self.vtkframe  
        #self.vtklayout.addWidget(self.vtkframe)
        self.vtkWindow = self.mdiarea.addSubWindow(self.vtkframe) 
        self.vtkWindow.setWindowTitle("3D View")

        self.schlegelframe = vtkqtrenderwidgets.VtkQtFrame(0, self.mainwindow,self)
        
        self.schlegelframe.move_camera(numpy.array([0,0,10]),numpy.array([0,0,0]),numpy.array([0,1,0]))
        
        self.schlegelWindow = self.mdiarea.addSubWindow(self.schlegelframe) 
        self.schlegelWindow.setWindowTitle("Schlegel View")
        #self.schlegelframe.VTKRenderWindow.Finalize()
        self.schlegelframe.hide()
        self.schlegelframe.BottomMenu.hide()
        self.mdiarea.setViewMode(QtGui.QMdiArea.TabbedView)
        
        #self.vtklayout.addWidget(self.schlegelframe)
        print "setting output widget"
        self.setOutputWidget(self.vtkframe.BottomMenu.InfoOptionsWidget.infoText)
        printd("Loaded VtkQtFrame")
        
        self.mdiarea.setActiveSubWindow(self.vtkWindow)
        
        self.vtklayout.setContentsMargins(0, 0, 0, 0)
        self.mainwindow.setCentralWidget(self.mainwidget)
        #print self,self.MainWindow, 200, 600,"Toolbar"
        
        #self.threadManager = threadManager()
        self.threadManager = QThreadManager() 
        #self.threadManager.end_call.connect(self.threadStatus)
        
        self.signalManager = QThreadSignalManager() 
        #self.threadManager = nonThreadManager()
        #self.processor = processes.processor(self,self.threadManager)
        self.processor = processes.Processor(self.config)
        
        self.processor.outputSignal = types.MethodType(self.signalManager.emitSignal, self.processor)
        
        self.structureWindows = {}
        self.structureWindows["Fullerene"]  = StructureWindow(self,self.mainwindow,self.processor,
                                                              self.threadManager,self.signalManager,"Fullerene")
        self.structureWindows["Nanotube"]  = StructureWindow(self,self.mainwindow,self.processor,
                                                             self.threadManager,self.signalManager,"Nanotube")
        
       
        
         
#        self.structureWindows["Fullerene"].setupHeaders(self.processor.structureLog["Fullerene"].headers)
#        self.structureWindows["Nanotube"].setupHeaders(self.processor.structureLog["Nanotube"].headers)
        
        self.objectActors = objectactors.ObjectActors(self.config,self.vtkframe,self.schlegelframe)
        
        self.operations = operations.Operations(self,self.mainwindow)
        #self.operations.connect(self.signalManager, QtCore.SIGNAL("render_update()"), self.vtkframe.resetCamera)
        #self.mainwindow.connect(self.processor, QtCore.SIGNAL('reset_camera()'), self.vtkframe.resetCamera)

        self.dock = dock.dock(self,self.mainwindow,self.dockWidth, self.dockHeight,"Toolbar") 
        
        self.mainwindow.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.vtkframe.BottomMenu)
        #self.mainwindow.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.schlegelframe.BottomMenu)
        self.mainwindow.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.dock)
        self.mainwindow.setCorner(QtCore.Qt.BottomLeftCorner,QtCore.Qt.LeftDockWidgetArea)
        printl("Welcome to the Python Carbon Nano-structures generator")
        
        self.running = 1
        self.rotateFlag = 0
        self.rotateCameraFlag = 0
        #self.queue = Queue.Queue()
        self.renWinInteract = self.vtkframe.VTKRenderWindowInteractor
        self.ren = self.vtkframe.VTKRenderer


        if(DEBUG==True):
            import vtk
            self.renWinInteract = self.vtkframe.VTKRenderWindowInteractor
            self.ren = self.vtkframe.VTKRenderer
            cone = vtk.vtkConeSource()
            cone.SetResolution(8)
        
            coneMapper = vtk.vtkPolyDataMapper()
            coneMapper.SetInput(cone.GetOutput())
        
            self.coneActor = vtk.vtkActor()
            self.coneActor.SetMapper(coneMapper)
            self.coneActor.GetProperty().SetColor((0.8,0,0))
            self.ren.AddActor(self.coneActor)
            
            row = self.dock.container.newRow()
            self.RotateBT = QtGui.QPushButton('Rotate')
            self.mainwindow.connect(self.RotateBT, QtCore.SIGNAL('clicked()'), self.SubmitRotate)
            row.addWidget(self.RotateBT)
        
        else:    
            self.dock.draw()
        
        #self.periodicCall()
        self.mainwindow.show()
        self.vtkframe.show()
        self.schlegelframe.show()
        
        #self.threadManager.start()
        #self.thread1 = threading.Thread(target=self.periodicCall)
        #self.thread1.setDaemon(1)
        #self.thread1.start()
        
        #self.periodicCall()
        #self.periodicCall()
        #
        #self.root.mainloop()       
    
    def threadStatus(self,fin):
        printl("thread status",fin)
    
    def SubmitRotate(self):
        self.threadManager.submit_to_queue(self.Rotate)  
    
    def saveCurrentStructure(self,folder=None,makeVideo=True):
        if(folder == None):return
        
        self.processor.saveCurrentStructure(folder,update=False)
        
        if(makeVideo):
            self.vtkframe.makeRotationImages(folder, degPerRotation=2)
            self.threadManager.submit_to_queue(encodeImages,
                                               folder+"/rotation_images/", folder,
                                               framerate=25, ffmpeg="ffmpeg"
                                               )  
            
        self.vtkframe.VTKRenderer.ResetCamera()  
        fp = self.vtkframe.VTKCamera.GetFocalPoint()
        #self.gui.vtkframe.move_camera((0,0,-10),fp,(1,0,0))
        self.vtkframe.saveImage(str(folder)+"/view.jpg",overwrite=True,resolution=None)
        
        self.mdiarea.setActiveSubWindow(self.schlegelWindow)
        self.schlegelframe.VTKRenderer.ResetCamera()  
        fp = self.schlegelframe.VTKCamera.GetFocalPoint()
        self.schlegelframe.move_camera((0,0,-10),(0,0,0),(1,0,0))
        self.schlegelframe.saveImage(str(folder)+"/schlegel_view.jpg",overwrite=True,resolution=None)
        self.mdiarea.setActiveSubWindow(self.vtkWindow)
    
    
    def Rotate(self):
        step = 360/360
        #for i in numpy.arange(0,360,step):
        while(1):    
            self.coneActor.RotateZ(step)
            self.renWinInteract.Render()
            self.renWinInteract.ReInitialize()
            
            time.sleep(0.05)
	    print "Rotating"   
    
    
    def setOutputWidget(self,widget):
        util.outputWidget = widget
        
    def callback(self):
        #printl("callback")
        sys.exit()


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setMinimumWidth(1100)
        self.setMinimumHeight(750)
        self.setStyleSheet(styleSheetString)
        self.show()
    
    def setGUI(self,gui):
        self.gui = gui
        
    def closeEvent(self, event):
        print("event")
        
        self.gui.threadManager.stop()
        QtGui.QApplication.quit()
            
        return
        
        reply = QtGui.QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            event.accept()
            self.gui.threadManager.stop()
            QtGui.QApplication.quit()

        else:
            event.ignore()
            
 
def start():
    app = QtGui.QApplication(sys.argv)
#    app.setPalette(QtGui.QPalette())

    #if(PLATFORM=="win"):app.setStyle(QtGui.QStyleFactory.create("cleanlooks"))
    strdir = QtGui.QApplication.applicationDirPath()
    #MainAppWindow = QtGui.QMainWindow()
    MainAppWindow = MainWindow()
    #MainAppWindow.setMinimumWidth(1000)
    #MainAppWindow.setMinimumHeight(700)
    #MainAppWindow.setStyleSheet(styleSheetString)
    #MainAppWindow.show()
    ngui = gui(MainAppWindow)
    MainAppWindow.setGUI(ngui) 
    
    try:
        sys.exit(app.exec_())
    except SystemExit as e:
        if e.code != 0:
            raise()
        os._exit(0)
               
if __name__=="__main__":
    global root
    
    start()

