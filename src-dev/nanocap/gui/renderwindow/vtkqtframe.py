'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: May 9, 2014
Copyright Marc Robinson  2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

Main renderwindow widget which holds
QVTKrenderwindowinteractor


-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
'''

from nanocap.core.globals import *
import sys, os, pickle,copy,math,cPickle,threading
from nanocap.gui.settings import *
QtGui, QtCore = QT.QtGui, QT.QtCore

from nanocap.gui.renderwindow.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from nanocap.gui.renderwindow.saveimagerotationoptionswindow import SaveImageRotationOptionsWindow
from nanocap.gui.renderwindow.saveimageoptionswindow import SaveImageOptionsWindow

from vtk import vtkActorCollection,vtkCellPicker,vtkRenderer,vtkAxesActor,\
                vtkCamera,vtkInteractorStyleSwitch,vtkWindowToImageFilter,\
                vtkJPEGWriter,vtkTIFFWriter,vtkPNGWriter,vtkRenderWindow

from nanocap.core.util import *
from nanocap.core import globals

import nanocap.resources.Resources as Resources


class VtkQtFrame(QtGui.QWidget):
    def __init__(self, ID,renderer=None):
        QtGui.QWidget.__init__(self)    
        self.layout = QtGui.QGridLayout(self)
        self.ID = ID
        self.MouseMoving = 0
        self.MouseLeftDrag = 0
        self.AAFrames = 0
        self.mutex = QtCore.QMutex()
        self.initial_load=0
        
        #self.hide()
        
        self.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)

        self.SelectedAtoms = []
        self.SelectionActors = vtkActorCollection()
        self.topToolbar = QtGui.QToolBar()
        self.topToolbar.setOrientation(QtCore.Qt.Horizontal)
        
        self.takeSnapshot = QtGui.QAction(QtGui.QIcon(str(IconDir) + 'ava-snapshot.png'), 'Take screen shot', self)
        self.takeSnapshot.setStatusTip('Take screen shot')
        self.connect(self.takeSnapshot, QtCore.SIGNAL('triggered()'), self.showSaveImageOptions)
        self.topToolbar.addAction(self.takeSnapshot)
        
        self.rotationSnapshots = QtGui.QAction(QtGui.QIcon(str(IconDir) + 'ava-snapshot-rotate.png'), 'Rotate and save images', self)
        self.rotationSnapshots.setStatusTip('Rotate and save images')
        self.connect(self.rotationSnapshots, QtCore.SIGNAL('triggered()'), self.showSaveRotationImageOptions)
        self.topToolbar.addAction(self.rotationSnapshots)
        
        self.RotateButton = QtGui.QAction(QtGui.QIcon(str(IconDir) + 'ava-rotate.png'), 'Toggle Rotate', self)
        self.RotateButton.setStatusTip('Toggle Rotate')
        self.RotateButton.setCheckable(1)
        self.RotateButton.setChecked(0)
        self.connect(self.RotateButton, QtCore.SIGNAL('triggered()'), self.toggleRotate)
        #self.topToolbar.addAction(self.RotateButton)
        
        self.perspectiveButton = QtGui.QAction(QtGui.QIcon(str(IconDir) + 'perspective-ava.png'), 'Perspective Camera', self)
        self.perspectiveButton.setStatusTip('Toggle perspective view')
        self.perspectiveButton.setCheckable(1)
        self.perspectiveButton.setChecked(1)
        self.connect(self.perspectiveButton, QtCore.SIGNAL('triggered()'), self.togglePerspective)
        self.topToolbar.addAction(self.perspectiveButton)
        
        self.ResetCameraButton = QtGui.QAction(QtGui.QIcon(str(IconDir) + 'reset-camera.png'), 'Reset Camera', self)
        self.ResetCameraButton.setStatusTip('Reset Camera')
        self.ResetCameraButton.setCheckable(0)
        self.connect(self.ResetCameraButton, QtCore.SIGNAL('triggered()'), self.resetCamera)
        self.topToolbar.addAction(self.ResetCameraButton)
        
        self.topToolbar.addSeparator()
        
        self.AAButton = QtGui.QAction(QtGui.QIcon(str(IconDir) + 'ava-0xAA-icon.png'), 'Toggle AA', self)
        self.AAButton.setStatusTip('Toggle AA')
        self.AAButton.setCheckable(0)
        self.AAButton.setChecked(0)
        self.connect(self.AAButton, QtCore.SIGNAL('triggered()'), self.toggleAA)
        self.topToolbar.addAction(self.AAButton)
        
        self.backgroundColourButton = QtGui.QAction(QtGui.QIcon(str(IconDir) + 'background-colour-ava.png'), 'Change Background Colour', self)
        self.backgroundColourButton.setStatusTip('Change Background Colour')
        self.connect(self.backgroundColourButton, QtCore.SIGNAL('triggered()'), self.toggleBackgroundColour)
        self.topToolbar.addAction(self.backgroundColourButton)
        

        self.AxesButton = QtGui.QAction(QtGui.QIcon(str(IconDir) + 'axis_icon2.png'), 'Toggle Axes', self)
        self.AxesButton.setStatusTip('Toggle Axes')
        self.AxesButton.setCheckable(1)
        self.AxesButton.setChecked(1)
        self.connect(self.AxesButton, QtCore.SIGNAL('triggered()'), self.toggleAxes)
        self.topToolbar.addAction(self.AxesButton)
        
        self.layout.addWidget(self.topToolbar,0,0)
        
        if(renderer==None):
            self.VTKRenderer = vtkRenderer()
        else:
            self.VTKRenderer = renderer
            
        self.VTKRenderer.SetBackground(1, 1, 1)
        self.VTKRenderWindow = vtkRenderWindow()
        #self.VTKRenderWindow = self.VTKRenderWindowInteractor.GetRenderWindow()
        #self.VTKRenderWindow.SetOffScreenRendering(1) 
        self.VTKRenderWindow.AddRenderer(self.VTKRenderer)    
        
        self.VTKRenderWindowInteractor = QVTKRenderWindowInteractor(self,rw=self.VTKRenderWindow)
        self.layout.addWidget(self.VTKRenderWindowInteractor,1,0)
        self.VTKRenderWindowInteractor.Initialize()
        self.VTKRenderWindowInteractor.Start()
        #self.VTKRenderWindowInteractor.setMouseTracking(True)
        printd("assigned VTKRenderWindowInteractor")
        self.VTKPicker = vtkCellPicker() 
        self.VTKPicker.SetTolerance(0.000001)
        self.VTKPicker.AddObserver("EndPickEvent", self.picked)
        self.VTKRenderWindowInteractor.SetPicker(self.VTKPicker)
        
        self.rotateCameraFlag = 0
        
        self.CameraLabel = QtGui.QLabel("Camera Position")
#        self.layout.addWidget(self.CameraLabel)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.AxesActor = vtkAxesActor()
        tprop = self.AxesActor.GetXAxisCaptionActor2D().GetCaptionTextProperty()
        tprop.SetColor(0,0,0)
        tprop.SetFontSize(11)
        tprop.SetItalic(0)
        tprop.SetBold(1)
        tprop.SetShadow(0)
        
        self.AxesActor.GetXAxisCaptionActor2D().SetCaptionTextProperty(tprop)
        self.AxesActor.GetYAxisCaptionActor2D().SetCaptionTextProperty(tprop)
        self.AxesActor.GetZAxisCaptionActor2D().SetCaptionTextProperty(tprop)
        self.AxesActor.SetShaftTypeToCylinder()
        self.AxesActor.SetCylinderRadius(0.05)
        self.AxesActor.SetCylinderResolution(50) 
        self.AxesActor.SetConeRadius(0.6)   
        self.AxesActor.SetConeResolution(20)
        self.AxesActor.SetTotalLength(10,10,10)
        self.AxesActor.SetNormalizedLabelPosition(1.4,1.4,1.4)
        
        
        self.axis_VTKRenderer = vtkRenderer()
        self.axis_VTKRenderer.SetBackground(1, 1, 1)
        self.axis_VTKRenderer.AddActor(self.AxesActor)
        
        self.VTKRenderer.SetViewport( 0, 0, 1, 1)
        self.axis_VTKRenderer.SetViewport( 0.85, 0, 1, 0.2)
        
        self.VTKCamera = vtkCamera()
        self.VTKCamera.SetClippingRange(0.1,1000)
        self.VTKCamera2 = vtkCamera()
        self.VTKCamera2.SetClippingRange(0.1,1000)
        self.VTKRenderer.SetActiveCamera(self.VTKCamera)
        self.axis_VTKRenderer.SetActiveCamera(self.VTKCamera2)
        
        self.VTKInteractorStyleSwitch = vtkInteractorStyleSwitch()
        self.VTKInteractorStyleSwitch.SetCurrentStyleToTrackballCamera()       
        
        self.LeftPressed = 0
        self.RightPressed = 0
        self.MouseMove = 0
        self.Bg = 'White'
        self.VTKRenderWindow = self.VTKRenderWindowInteractor.GetRenderWindow()
        self.VTKRenderWindow.AddRenderer(self.VTKRenderer)    
        self.VTKRenderWindow.AddRenderer(self.axis_VTKRenderer)      
        printd("Got render window and assigned rendered")
        self.VTKRenderWindowInteractor.SetInteractorStyle(self.VTKInteractorStyleSwitch)
        self.VTKRenderWindowInteractor.AddObserver('LeftButtonPressEvent',self.Left_Press)
        self.VTKRenderWindowInteractor.AddObserver('RightButtonPressEvent',self.Right_Press)
        self.VTKRenderWindowInteractor.AddObserver('MouseWheelForwardEvent',self.Camera_Event)
        self.VTKRenderWindowInteractor.AddObserver('MouseWheelBackwardEvent',self.Camera_Event)
        
        self.connect(self.VTKRenderWindowInteractor, QtCore.SIGNAL('LeftButtonReleaseOverride(QEvent)'), self.Left_Release)
        self.connect(self.VTKRenderWindowInteractor, QtCore.SIGNAL('RightButtonReleaseOverride(QEvent)'), self.Right_Release)
        self.connect(self.VTKRenderWindowInteractor, QtCore.SIGNAL('MouseMoveOverride(QEvent)'), self.mouseMoveEvent)
        
        try:self.centerCameraOnCell()
        except:pass
        self.VTKRenderWindowInteractor.Initialize()
        self.VTKRenderWindowInteractor.Start()
        self.VTKRenderWindowInteractor.ReInitialize()
        
        printd("Started VTKRenderWindowInteractor")
        self.setMouseTracking(True)
        self.AssociatedPipelines = {}
        self.SaveImageOptionsWindow =SaveImageOptionsWindow(self)#,self.MainWindow)
        self.SaveImageRotationOptionsWindow =SaveImageRotationOptionsWindow(self)#,self.MainWindow)
        printd("End init vtkFrame")
        self.VTKCamera.Azimuth(90)
        
        self.setLayout(self.layout)
    
    def center_on_load(self):
        if(self.VTKRenderer.GetActors().GetNumberOfItems()>0):
            if(self.initial_load==0):
                self.resetCamera()
                self.initial_load=1
        
    def makeRotationImages(self,folder,degPerRotation=1,prefix="rotation_images"):   
        numberRotations = int(360/degPerRotation)
        try:os.mkdir(folder+"/"+prefix+"/")
        except:pass
        for i in numpy.arange(0,numberRotations+1,1):        
            Filename = "%s%04d%s" % (folder+"/"+prefix+"/image",i,".jpg")    
            self.saveImage(Filename,overwrite=True,resolution=None)
            self.VTKCamera.Azimuth(degPerRotation)
            self.VTKCamera.SetClippingRange(0.1,1000)
    
    def toggleAxes(self):
        if(self.AxesButton.isChecked()):
            self.VTKRenderWindow.AddRenderer(self.axis_VTKRenderer)
        else:
            self.VTKRenderWindow.RemoveRenderer(self.axis_VTKRenderer)  
        self.refreshWindow()
              
    def resetCamera(self):
        printl("self.mutex.lock()")
        
        self.VTKRenderer.ResetCamera()  
        self.resetAxesCamera() 
        #self.VTKRenderWindowInteractor.ReInitialize() 
        self.refreshWindow()
        
    
    def toggleRotate(self):
        if(self.RotateButton.isChecked()):
            #self.Gui.threadManager.submit_to_queue(self.rotateCamera)
            #self.emit(QtCore.SIGNAL("rotateCamera(QWidget)"),self)
#             self.thread = QtCore.QThread()
#             self.moveToThread(self.thread )
#             self.thread.started.connect(self.rotateCamera)
#             self.thread.start()
            import threading
            threading.Thread(target=self.rotateCamera).start()
            self.rotateCameraFlag = 1
        else:
            self.rotateCameraFlag = 0  
            #self.thread.quit()
        #   .self.ThreadManager.submit_to_queue(self.VTKFrame.rotateCamera)
        
    def toggleAA(self):
        if(self.AAFrames==0):
            self.AAFrames = 2
            self.AAButton.setIcon(QtGui.QIcon(str(IconDir) + 'ava-2xAA-icon.png'))
        elif(self.AAFrames==2):
            self.AAFrames = 4
            self.AAButton.setIcon(QtGui.QIcon(str(IconDir) + 'ava-4xAA-icon.png'))
        elif(self.AAFrames==4):
            self.AAFrames = 8  
            self.AAButton.setIcon(QtGui.QIcon(str(IconDir) + 'ava-8xAA-icon.png'))  
        else:
            self.AAFrames = 0
            self.AAButton.setIcon(QtGui.QIcon(str(IconDir) + 'ava-0xAA-icon.png'))
            

        self.VTKRenderWindow.SetAAFrames(self.AAFrames)
        self.VTKRenderWindowInteractor.ReInitialize()
            
    def showSaveImageOptions(self):
        printl("will show image options")
        self.SaveImageOptionsWindow.center()
        self.SaveImageOptionsWindow.show()
    
    def showSaveRotationImageOptions(self):
        printl("will show image rotation options")
        self.SaveImageRotationOptionsWindow.center()
        self.SaveImageRotationOptionsWindow.show()
    
    def rotate(self,deg):
        self.VTKCamera.Azimuth(deg)
        self.VTKCamera2.Azimuth(deg)
    
    def rotateCamera(self):
        printl("in rotate camera")
        step = 360/360
        while(self.rotateCameraFlag):  
            self.VTKCamera.Azimuth(step)
            time.sleep(0.05)
            self.refreshWindow()
    
    def refreshWindow(self):
        self.VTKRenderWindowInteractor.update()
        self.resetAxesCamera() 
        
    def saveImage(self,f,overwrite=False,resolution=None):
        printl("saving",f)
        renWin = self.VTKRenderWindowInteractor.GetRenderWindow()
        if(resolution!=None):
            oldRes= renWin.GetSize()
            renWin.SetSize( resolution[0], resolution[1])
            self.VTKRenderWindowInteractor.ReInitialize()
        ftype = f.split(".")[-1]
        w2if = vtkWindowToImageFilter()
        w2if.SetInput(renWin);
        #print ftype
        if(ftype=="jpg"):
            tiffw = vtkJPEGWriter()
            tiffw.SetQuality(100)
        elif(ftype=="tif"):    
            tiffw = vtkTIFFWriter()
        elif(ftype=="png"):              
            tiffw = vtkPNGWriter()
        else:
            tiffw = vtkJPEGWriter()
            tiffw.SetQuality(100)     
            ftype = "jpg"
        fsuffix = f[0:len(f)-3]
        
        #tiffw.SetCompressionToNoCompression()
        tiffw.SetInput(w2if.GetOutput());
        fname = f
        #printl("saving 2",fname)
        if(overwrite==False):
            saved = 0
            count=0
            while(saved==0):
                if(os.path.exists(fname)):
                    count+=1
                    fname = "%s%s%d%s%s" % (fsuffix,"(",count,").",ftype)
                    print fname
                else:
                    saved=1          
        tiffw.SetFileName(fname)
        tiffw.Write()
        if(resolution!=None):renWin.SetSize(oldRes)
    
    def mouseMoveEvent(self,event):
        self.MouseMoving = 1
        if(self.LeftPressed==1 or self.RightPressed==1 ):
            self.update_Camera_info()
        if(self.LeftPressed==1):
            self.MouseLeftDrag=1
        else:
            self.MouseLeftDrag=0
        
        self.resetAxesCamera()
    
    def resetAxesCamera(self):    
        pos = self.VTKCamera.GetPosition()
        fp = self.VTKCamera.GetFocalPoint()
        pfvec =  numpy.array(pos) - numpy.array(fp)
        
        reqdist = 50.0
        npos =  reqdist * normalise(pfvec)
        self.VTKCamera2.SetPosition(npos)
        self.VTKCamera2.SetViewUp(self.VTKCamera.GetViewUp())    
        self.VTKCamera2.SetFocalPoint(0,0,0)      
        self.VTKCamera2.SetClippingRange(0.1,1000)  
        #printl(self.VTKCamera.GetPosition(),self.VTKCamera.GetPosition())
    
    def addPipeline(self,pipeline):
        self.AssociatedPipelines[pipeline.PipelineID] = pipeline
    def removePipeline(self,pipeline):
        try:self.AssociatedPipelines.pop(pipeline.PipelineID)
        except:pass
        
    def picked(self,object, event):
        printl("PICKED")
        if self.VTKPicker.GetCellId() < 0:
            return
        selPt = self.VTKPicker.GetSelectionPoint()
        pickPos = self.VTKPicker.GetPickPosition()
        printl("pickPos",pickPos)
         
    def toggleBackgroundColour(self):
        col = QtGui.QColorDialog.getColor()
        if col.isValid():
            self.BackgoundColour = col
            r=0
            g=0
            b=0
            r= "%0.2f" % (float(self.BackgoundColour.red())/255.0)
            g= "%0.2f" % (float(self.BackgoundColour.green())/255.0)
            b= "%0.2f" % (float(self.BackgoundColour.blue())/255.0)
            self.BackgoundColourRGB = (float(r),float(g),float(b))
            self.VTKRenderer.SetBackground(self.BackgoundColourRGB)
            self.axis_VTKRenderer.SetBackground(self.BackgoundColourRGB)
            self.VTKRenderWindowInteractor.ReInitialize()
    
    def togglePerspective(self):    
        if(self.perspectiveButton.isChecked()):
            self.VTKCamera.SetParallelProjection(False)
        else:
            self.VTKCamera.SetParallelProjection(True)    
        self.VTKRenderWindowInteractor.ReInitialize()    
        
    def removeActorsInCollection(self,AtomsActorList,refresh=True):
        AtomsActorList.InitTraversal()
        AtomsActor = AtomsActorList.GetNextItem()
        while(AtomsActor != None):
            try:self.VTKRenderer.RemoveActor(AtomsActor)
            except:pass
            AtomsActor = AtomsActorList.GetNextItem()
        if(refresh==True):self.VTKRenderWindowInteractor.ReInitialize() 

    def addActorsInCollection(self,AtomsActorList,refresh=True):
        AtomsActorList.InitTraversal()
        AtomsActor = AtomsActorList.GetNextItem()
        while(AtomsActor != None):
            try:self.VTKRenderer.AddActor(AtomsActor)    
            except:pass
            AtomsActor = AtomsActorList.GetNextItem()        
        if(refresh==True):self.VTKRenderWindowInteractor.ReInitialize()
    
    def removeActorsInArray(self,array):
        try:
            for actor in array:
                self.VTKRenderer.RemoveActor(actor)   
        except:pass
        self.refreshWindow()
        
    def addActorsInArray(self,array):
        try:
            for actor in array:
                self.VTKRenderer.AddActor(actor)   
        except:pass
        self.refreshWindow()
        
    def Camera_Event(self,object,event):
        self.update_Camera_info()
    
    def centerCameraOnPointSet(self,pointSet):
        '''
        can't use VTKRenderer.ResetCamera when threaded for some reason
        possibly it tries to get the bounds of the props across the thread?
        anyhow reposition the camera in here for a given pointSet.
        Basically the same routine as in VTK.
        '''
        xmin,ymin,zmin,xmax,ymax,zmax = pointSet.getBounds()
       
        vn  = self.VTKCamera.GetViewPlaneNormal()
        printl("vn",vn)
        center = pointSet.getCenter()

        w1 = xmax-xmin
        w2 = ymax-ymin
        w3 = zmax-zmin
        w1 *= w1;
        w2 *= w2;
        w3 *= w3;
        radius = w1 + w2 + w3;
        
        if(radius==0.0):radius = 1
        radius = math.sqrt(radius)*0.5;
        
        
        distance = radius/math.sin(self.VTKCamera.GetViewAngle()*math.pi/360.0);
        
        
        vup = self.VTKCamera.GetViewUp();
        if ( numpy.dot(numpy.array(vup),numpy.array(vn)) > 0.999 ):
            self.VTKCamera.SetViewUp(-vup[2], vup[0], vup[1])
        
        self.VTKCamera.SetFocalPoint(center[0],center[1],center[2]);
        self.VTKCamera.SetPosition(center[0]+distance*vn[0],
                                        center[1]+distance*vn[1],
                                        center[2]+distance*vn[2]);
        
        self.VTKCamera.SetClippingRange(0.1,1000)
        self.refreshWindow()

    def move_camera(self,pos,foc,vu):
        self.VTKCamera.SetPosition(pos)
        self.VTKCamera.SetFocalPoint(foc)
        self.VTKCamera.SetViewUp(vu)
        self.VTKCamera.SetClippingRange(0.1,1000)
        self.update_Camera_info()
        self.refreshWindow() 
        
    def update_Camera_info(self):        
        pos = self.VTKCamera.GetPosition()
        posstring = "%0.2f,%0.2f,%0.2f" % (pos[0],pos[1],pos[2])
        foc = self.VTKCamera.GetFocalPoint()
        focstring = "%0.2f,%0.2f,%0.2f" % (foc[0],foc[1],foc[2])
        self.CameraLabel.setText("Camera: POS: "+str(posstring)+" FP: "+str(focstring))
                    
    def Left_Press(self,object,event):
        self.LeftPressed = 1
        self.MouseMoving = 0 
        
    def Left_Release(self,event):
        self.LeftPressed = 0
        self.MouseLeftDrag = 0
        if(self.MouseMoving ==0):
            pos = self.VTKRenderWindowInteractor.GetEventPosition()
            self.VTKPicker.Pick(pos[0], pos[1], 0, self.VTKRenderer) 
        
    def Right_Press(self,object,event):
        self.RightPressed = 1
        
    def Right_Release(self,event):
        self.RightPressed = 0   
         
    def resetRenderWindow(self):
        self.VTKRenderer.Render() 
        self.VTKRenderWindow.Render()   
        #self.VTKRenderWindowInteractor._Iren.EnterEvent()
        self.VTKRenderWindowInteractor.update()
        #self.VTKRenderWindowInteractor.Initialize()
        #self.VTKRenderWindowInteractor.Start()
        self.VTKRenderWindowInteractor.ReInitialize()
        self.VTKRenderWindowInteractor.Render() 
    
    def closeEvent(self, event):
        event.accept() 
        
    def sizeHint(self):
        return QtCore.QSize(800,700)