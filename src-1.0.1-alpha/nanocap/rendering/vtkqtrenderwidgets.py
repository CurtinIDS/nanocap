'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: July 12 2012
Copyright Marc Robinson 2013
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

Main VTKQt render widget

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
'''
from nanocap.core.globals import *
import sys, os, pickle,copy,math,cPickle,threading
from nanocap.core.globals import QT
QtGui, QtCore = QT.QtGui, QT.QtCore

from nanocap.gui.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from vtk import vtkActorCollection,vtkCellPicker,vtkRenderer,vtkAxesActor,\
                vtkCamera,vtkInteractorStyleSwitch,vtkWindowToImageFilter,\
                vtkJPEGWriter,vtkTIFFWriter,vtkPNGWriter

from nanocap.core.util import *
from nanocap.core import globals
from nanocap.gui.forms import GenericForm,TitleBar,OptionsWindow

#import resources.Resources as Resources

  
class VtkQtFrame(QtGui.QWidget):
    def __init__(self, ID, MainWindow, Gui):
        QtGui.QWidget.__init__(self,MainWindow)    
        #@self.layout = QtGui.QVBoxLayout(self)
        self.layout = QtGui.QGridLayout(self)
        #self.layout.set 
        self.ID = ID
        self.MainWindow = MainWindow
        self.Gui = Gui
        self.MouseMoving = 0
        self.MouseLeftDrag = 0
        self.AAFrames = 0
        self.mutex = QtCore.QMutex()
        
        #self.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)

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
        self.topToolbar.addAction(self.RotateButton)
        
        self.perspectiveButton = QtGui.QAction(QtGui.QIcon(str(IconDir) + 'perspective-ava.png'), 'Perspective Camera', self)
        self.perspectiveButton.setStatusTip('Toggle perspective view')
        self.perspectiveButton.setCheckable(1)
        self.perspectiveButton.setChecked(1)
        self.connect(self.perspectiveButton, QtCore.SIGNAL('triggered()'), self.togglePerspective)
        self.topToolbar.addAction(self.perspectiveButton)
        
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
        
        self.VTKRenderWindowInteractor = QVTKRenderWindowInteractor(self)
        self.layout.addWidget(self.VTKRenderWindowInteractor,1,0)
        self.VTKRenderWindowInteractor.Initialize()
        #self.VTKRenderWindowInteractor.Start()
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

        self.BottomMenu = RenderWindowBottomMenu(self,self.MainWindow)
        
        self.VTKRenderer = vtkRenderer()
        self.VTKRenderer.SetBackground(1, 1, 1)
        
        
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
        
        
        self.VTKRenderer2 = vtkRenderer()
        self.VTKRenderer2.SetBackground(1, 1, 1)
        self.VTKRenderer2.AddActor(self.AxesActor)
        
        self.VTKRenderer.SetViewport( 0, 0, 1, 1)
        self.VTKRenderer2.SetViewport( 0.85, 0, 1, 0.2)
        
        self.VTKCamera = vtkCamera()
        self.VTKCamera.SetClippingRange(0.1,1000)
        self.VTKCamera2 = vtkCamera()
        self.VTKCamera2.SetClippingRange(0.1,1000)
        self.VTKRenderer.SetActiveCamera(self.VTKCamera)
        self.VTKRenderer2.SetActiveCamera(self.VTKCamera2)
        
        self.VTKInteractorStyleSwitch = vtkInteractorStyleSwitch()
        self.VTKInteractorStyleSwitch.SetCurrentStyleToTrackballCamera()       
        
        self.LeftPressed = 0
        self.RightPressed = 0
        self.MouseMove = 0
        self.Bg = 'White'
        self.VTKRenderWindow = self.VTKRenderWindowInteractor.GetRenderWindow()
        self.VTKRenderWindow.AddRenderer(self.VTKRenderer)    
        self.VTKRenderWindow.AddRenderer(self.VTKRenderer2)      
        printd("Got render window and assigned rendered")
#        self.Menu2 = MenuBar(self)
#        self.layout.setMenuBar(self.Menu2)
        self.VTKRenderWindowInteractor.SetInteractorStyle(self.VTKInteractorStyleSwitch)
        #self.VTKRenderWindowInteractor.AddObserver('MouseMoveEvent',self.Mouse_Move)
        #self.VTKRenderWindowInteractor.AddObserver('LeftButtonReleaseEvent',self.Left_Release)
        self.VTKRenderWindowInteractor.AddObserver('LeftButtonPressEvent',self.Left_Press)
        #self.VTKRenderWindowInteractor.AddObserver('RightButtonReleaseEvent',self.Right_Release)
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
        printd("Started VTKRenderWindowInteractor")
        self.setMouseTracking(True)
        self.AssociatedPipelines = {}
        self.SaveImageOptionsWindow =SaveImageOptionsWindow(self,self.MainWindow)
        self.SaveImageRotationOptionsWindow =SaveImageRotationOptionsWindow(self,self.MainWindow)
        printd("End init vtkFrame")
        self.VTKCamera.Azimuth(90)
        
        self.setLayout(self.layout)
        
#    def sizeHint(self):
#        return QtCore.QSize(700,700)

    
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
            self.VTKRenderWindow.AddRenderer(self.VTKRenderer2)
        else:
            self.VTKRenderWindow.RemoveRenderer(self.VTKRenderer2)  
        self.refreshWindow()
              
    def resetCamera(self):
        printl("self.mutex.lock()")
        
        self.VTKRenderer.ResetCamera()  
        self.resetAxesCamera() 
        #self.VTKRenderWindowInteractor.ReInitialize() 
        self.refreshWindow()
        
    
    def toggleRotate(self):
        if(self.RotateButton.isChecked()):
            self.Gui.threadManager.submit_to_queue(self.rotateCamera)
            self.rotateCameraFlag = 1
        else:
            self.rotateCameraFlag = 0   
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
    
    def rotateCamera(self):
        step = 360/360
        while(self.rotateCameraFlag):  
            self.VTKCamera.Azimuth(step)
            time.sleep(0.05)
            self.refreshWindow()
    
    def refreshWindow(self):
        #self.VTKRenderWindowInteractor.Render()
        #self.VTKRenderer.Render()
        self.MainWindow.update()
        self.VTKRenderWindowInteractor.update()
        self.resetAxesCamera() 
    	#self.update_Camera_info()
    	#self.VTKRenderWindowInteractor._Iren.KeyPressEvent()
            #self.VTKRenderWindowInteractor._Iren.CharEvent()
    	#self.VTKRenderWindowInteractor.repaint()
    	#self.VTKRenderWindowInteractor.ReInitialize()
    	#self.VTKRenderWindowInteractor._Iren.ReInitialize()
    	#keyevent = QtGui.QKeyEvent(QtCore.QEvent.KeyRelease,QtCore.Qt.Key_W,QtCore.Qt.NoModifier)
    	#self.VTKRenderWindowInteractor.keyReleaseEvent(keyevent)
    	
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
        #printl("saving 3",fname)                
        tiffw.SetFileName(fname)
        tiffw.Write()
        if(resolution!=None):renWin.SetSize(oldRes)
    
    def mouseMoveEvent(self,event):
        #print "MOUSE MOVING QT"
        self.MouseMoving = 1
        if(self.LeftPressed==1 or self.RightPressed==1 ):
            self.update_Camera_info()
        if(self.LeftPressed==1):
            self.MouseLeftDrag=1
        #print "MOUSE MouseLeftDrag"
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
        
#         fp = numpy.array(pointSet.getCenter())
#        pos =  fp - numpy.array([5.0*(xmax-xmin),0,0])
#        vu = [0,1,0]
#        self.move_camera(pos, fp, vu)
        
    def move_camera(self,pos,foc,vu):
        self.VTKCamera.SetPosition(pos)
        self.VTKCamera.SetFocalPoint(foc)
        self.VTKCamera.SetViewUp(vu)
        self.VTKCamera.SetClippingRange(0.1,1000)
        self.update_Camera_info()
        self.refreshWindow() 
        
    def update_Camera_info(self):        
        #print "MOVING INTERACTOR" 
        pos = self.VTKCamera.GetPosition()
        posstring = "%0.2f,%0.2f,%0.2f" % (pos[0],pos[1],pos[2])
        foc = self.VTKCamera.GetFocalPoint()
        focstring = "%0.2f,%0.2f,%0.2f" % (foc[0],foc[1],foc[2])
        self.CameraLabel.setText("Camera: POS: "+str(posstring)+" FP: "+str(focstring))
        #self.BottomMenu.CameraOptionsWidget.updateCamera(self.VTKCamera)
            
    def Left_Press(self,object,event):
        self.LeftPressed = 1
        self.MouseMoving = 0 
        #print "LEFT PRESS"
        
    def Left_Release(self,event):
        self.LeftPressed = 0
        self.MouseLeftDrag = 0
        #print "LEFT RELEASE MOUSE MOVING?",self.MouseMoving
        if(self.MouseMoving ==0):
            pos = self.VTKRenderWindowInteractor.GetEventPosition()
            self.VTKPicker.Pick(pos[0], pos[1], 0, self.VTKRenderer) 
        
    def Right_Press(self,object,event):
        #print "RIGHT PRESS"
        self.RightPressed = 1
        
    def Right_Release(self,event):
        #print "RIGHT RELEASE"
        self.RightPressed = 0   
         
    def resetRenderWindow(self):
        self.VTKRenderer.Render()
#        self.VTKRenderWindow = self.VTKRenderWindowInteractor.GetRenderWindow()
#        self.VTKRenderWindow.AddRenderer(self.VTKRenderer)  
         
        self.VTKRenderWindowInteractor.Initialize()
        self.VTKRenderWindowInteractor.Start()
        self.VTKRenderWindowInteractor.ReInitialize()
    
    def closeEvent(self, event):
        #self.MainWindow.RenderWindowCount-=1
        self.MainWindow.RenderWindowVisMask[self.ID] = 0
        self.MainWindow.FilterDockWidget.updateAllPipelineTargets()
        printd("self.MainWindow.RenderWindowCount",self.MainWindow.RenderWindowCount)
        printd("self.MainWindow.RenderWindowVisMask",self.MainWindow.RenderWindowVisMask)
        event.accept() 
        
class RenderWindowBottomMenu(QtGui.QDockWidget):
    def __init__(self,vtkwidget,MainWindow):
        self.VTKWidget = vtkwidget
        self.MainWindow = MainWindow
        #OptionsWindow.__init__(self,self.MainWindow,"Options Window",popup = False,parent=self.VTKWidget)
        QtGui.QDockWidget.__init__(self, None)
        self.setTitleBarWidget(QtGui.QWidget())
        self.container = GenericForm(isScrollView=False,isGroup=False)
        #self.setTitleBarWidget(QtGui.QWidget())
        self.container.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Maximum)
        #self.container.setMinimumHeight(200)
        self.setWidget(self.container)
        
        #self.CameraOptionsWidget = CameraOptionsWidget(self)
        ##self.CameraTitle = TitleBar("Camera",self.CameraOptionsWidget,noicons=True,switchIcons=True)
        #self.CameraTitle.MinimiseBT.setChecked(1)
        #self.connect(self.CameraTitle, QtCore.SIGNAL('minimiseTitlePressed(QString)'), self.showPressed)
        
        self.InfoOptionsWidget = InfoOptionsWidget(self)
        self.InfoTitle = TitleBar("Output",self.InfoOptionsWidget,noicons=True,switchIcons=True)
        self.InfoTitle.MinimiseBT.setChecked(1)
        self.connect(self.InfoTitle, QtCore.SIGNAL('minimiseTitlePressed(QString)'), self.showPressed)
        
        mainRow = self.container.newRow(align="Center")
        mainRow.addWidgets((self.InfoTitle,))#self.CameraTitle,))
        
        self.subRow = self.container.newRow(align="Center")
        self.subRow.addWidgets((self.InfoOptionsWidget,))#self.CameraOptionsWidget,))
        self.show()
    
    def sizeHint(self):
        return QtCore.QSize(20,700)
        
    def showPressed(self,title):
        #printd("showPressed","Output",self.InfoTitle.MinimiseBT.isChecked(),"Camera",self.CameraTitle.MinimiseBT.isChecked())
        
        if(str(title)=="Output"):
            if(self.InfoTitle.MinimiseBT.isChecked()==False):
                self.InfoTitle.showWidget()
                self.container.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding,QtGui.QSizePolicy.MinimumExpanding)
                #self.CameraTitle.MinimiseBT.setChecked(True)
                #self.CameraTitle.hideWidget()
            else:
                self.InfoTitle.hideWidget()   
                self.container.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding,QtGui.QSizePolicy.Maximum)
                
#        if(str(title)=="Camera"):
#            if(self.CameraTitle.MinimiseBT.isChecked()==False):
#                self.CameraTitle.showWidget()
#                self.InfoTitle.MinimiseBT.setChecked(True)
#                self.InfoTitle.hideWidget()
#                self.container.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding,QtGui.QSizePolicy.MinimumExpanding)
#            else:
#                self.CameraTitle.hideWidget() 
#                self.container.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding,QtGui.QSizePolicy.Maximum)
#                #self.resize(20,20)
                
        
class SaveImageRotationOptionsWindow(OptionsWindow):
    def __init__(self,VtkQtFrame,MainWindow):
        self.VtkQtFrame = VtkQtFrame
        self.MainWindow = MainWindow
        OptionsWindow.__init__(self,self.MainWindow,"Save Image Rotations") 
        
        self.Resolution = [0]*2
        
        row=self.newRow(align="HTCenter")
        
        self.group = GenericForm(title="Save Image Roations of 'Render Window "+str(self.VtkQtFrame.ID)+"'",doNotShrink=True,show=True)
        row.addWidget(self.group) 
        
        row=self.group.newRow(align="HTCenter")
        self.RenderTypebuttongroup = QtGui.QButtonGroup(self)
        self.RenderTypebuttongroup.setExclusive(1)
        self.POVButton = QtGui.QPushButton(QtGui.QIcon(str(IconDir)+'pov-icon.png'), 'POV-Ray')
        self.POVButton.setCheckable(1)
        self.VTKButton = QtGui.QPushButton(QtGui.QIcon(str(IconDir)+'vtk-icon.png'), 'VTK')
        self.VTKButton.setCheckable(1)
        self.VTKButton.setChecked(1)
        self.RenderTypebuttongroup.addButton(self.POVButton)
        self.RenderTypebuttongroup.addButton(self.VTKButton)
        self.connect(self.RenderTypebuttongroup, QtCore.SIGNAL('buttonClicked(int)'), self.setRenderType)
        row.addWidgets((self.POVButton,self.VTKButton))
        
        row=self.group.newRow(align="HTCenter")
        self.UseCurrentResolutionCB = QtGui.QCheckBox("Use current resoluton")
        self.UseCurrentResolutionCB.setEnabled(1)
        self.UseCurrentResolutionCB.setChecked(1)
        self.connect(self.UseCurrentResolutionCB, QtCore.SIGNAL('stateChanged(int)'), self.setUseResolution)
        row.addWidget(self.UseCurrentResolutionCB)
       
        row=self.group.newRow(align="HTCenter")
        self.reslab= QtGui.QLabel("Resolution")
        self.reslab.setEnabled(0)
        self.ImageWidthSB = QtGui.QSpinBox()
        self.ImageWidthSB.setMaximum(2500)
        self.ImageWidthSB.setValue(800)
        
        self.ImageWidthSB.setEnabled(0)
        self.reslab2= QtGui.QLabel("x")
        self.reslab2.setEnabled(0)
        self.ImageHeightSB = QtGui.QSpinBox()
        self.ImageHeightSB.setMaximum(2500)
        self.ImageHeightSB.setValue(600)
        self.ImageHeightSB.setEnabled(0)
        
        self.connect(self.ImageWidthSB, QtCore.SIGNAL('valueChanged(int)'), self.changeResolutionW)
        self.connect(self.ImageHeightSB, QtCore.SIGNAL('valueChanged(int)'), self.changeResolutionH)
        row.addWidgets((self.reslab,self.ImageWidthSB,self.reslab2,self.ImageHeightSB))
        
        #SetSize( 1024, 1024 )
        
        row=self.group.newRow(align="HTCenter")
        lab= QtGui.QLabel("Folder:")
        self.FolderEntry = QtGui.QLineEdit()
        self.FolderEntry.setMinimumWidth(80)
        self.GetFolderButton = QtGui.QPushButton("Browse")
        self.connect(self.GetFolderButton, QtCore.SIGNAL('clicked()'), self.getFolder)
        row.addWidgets((lab,self.FolderEntry,self.GetFolderButton))
        
        row=self.group.newRow(align="HTCenter")
        lab= QtGui.QLabel("Filename:")
        self.FilenameEntry = QtGui.QLineEdit()
        self.FilenameEntry.setMinimumWidth(80)
        lab2= QtGui.QLabel("<image_number>")
        row.addWidgets((lab,self.FilenameEntry,lab2))
        
        row=self.group.newRow(align="HTCenter")
        self.ImageWidthSB.setEnabled(0)
        self.DegLab= QtGui.QLabel("Degree Increment")
        
        self.DegreeStepSB = QtGui.QSpinBox()
        self.DegreeStepSB.setMaximum(360)
        self.DegreeStepSB.setValue(5)
        self.DegreeStepSB.setEnabled(1)
        row.addWidgets((self.DegLab,self.DegreeStepSB))
        
        
        row=self.group.newRow(align="HTCenter")
        self.GoButton = QtGui.QPushButton("Go!")
        self.connect(self.GoButton, QtCore.SIGNAL('clicked()'), self.go_rotation)
        #self.SaveAsButton = QtGui.QPushButton("Save As")
        #self.connect(self.SaveAsButton, QtCore.SIGNAL('clicked()'), self.saveAs)
        row.addWidget(self.GoButton)
        
        row=self.group.newRow(align="HTCenter")
        
        self.VidLab= QtGui.QLabel("Video Options  ")
        Lab= QtGui.QLabel("Frame Rate")
        self.FrameRateSB = QtGui.QSpinBox()
        self.FrameRateSB.setMaximum(360)
        self.FrameRateSB.setValue(5)
        self.FrameRateSB.setEnabled(1)
        Lab2= QtGui.QLabel("ffmpeg")
        self.FFmpegBin = QtGui.QLineEdit()
        self.FFmpegBin.setMinimumWidth(80)
        self.FFmpegBin.setText("/sw/bin/ffmpeg") 
        row.addWidgets((self.VidLab,Lab,self.FrameRateSB,Lab2,self.FFmpegBin))

        row=self.group.newRow(align="HTCenter")
        self.EncodeVideoButton = QtGui.QPushButton("Encode Video")
        self.connect(self.EncodeVideoButton, QtCore.SIGNAL('clicked()'), self.encode_roationVideo)
        #self.SaveAsButton = QtGui.QPushButton("Save As")
        #self.connect(self.SaveAsButton, QtCore.SIGNAL('clicked()'), self.saveAs)
        row.addWidget(self.EncodeVideoButton)
        
        
    def changeResolutionH(self,val):    
        self.Resolution[1] = val
        
    def changeResolutionW(self,val):
        self.Resolution[0] = val
        
    def setUseResolution(self,val):
        printd("RES CHECK")
        if(self.UseCurrentResolutionCB.isChecked()):
            self.reslab.setEnabled(0)
            self.ImageWidthSB.setEnabled(0)
            self.reslab2.setEnabled(0)
            self.ImageHeightSB.setEnabled(0)
        else:
            self.reslab.setEnabled(1)
            self.ImageWidthSB.setEnabled(1)
            self.reslab2.setEnabled(1)
            self.ImageHeightSB.setEnabled(1)
    def setRenderType(self,val):
        if(self.POVButton.isChecked()):
            self.RenderType = "POV"
            #self.VideoImageType = "png"
            #self.VideoPngCheck.setChecked(1)
            #self.ImageType = "png"
            #self.PngCheck.setChecked(1)
        
        if(self.VTKButton.isChecked()):
            self.RenderType = "VTK"

    def getFolder(self):
        fdiag = QtGui.QFileDialog()
        fdiag.setModal(1)
        #fdiag.setAcceptMode(fdiag.AcceptSave)
        #fdiag.setFilters([".jpg",".png"])
        fdiag.setFileMode(fdiag.Directory)
        
        ret = fdiag.exec_()
        if  ret == QtGui.QDialog.Accepted:
            f=fdiag.selectedFiles()[0]
            self.SaveFolder = f
            self.FolderEntry.setText(f)
            #ftype = str(fdiag.selectedFilter()).split("(")[0].rstrip()
        else:
            return
        fdiag.close()
       
    def go_rotation(self):   
        wd = str(self.FolderEntry.text())  
        try:os.mkdir(wd+"/Rotation_Images")
        except:pass
        degPerRotation = int(self.DegreeStepSB.value())
        numberRotations = int(360/degPerRotation)
        
        
        for i in numpy.arange(0,numberRotations+1,1):        
            f = self.FilenameEntry.text()
            Filename = "%s%04d%s" % (wd+"/Rotation_Images/"+str(f),i,".jpg")    
            
            if(self.UseCurrentResolutionCB.isChecked()):
                self.VtkQtFrame.saveImage(Filename,overwrite=False,resolution=None)
            else:
                self.VtkQtFrame.saveImage(Filename,overwrite=False,resolution=self.Resolution)
            
            self.VtkQtFrame.VTKCamera.Azimuth(degPerRotation)
            
    def encode_roationVideo(self):  
        olddir = os.getcwd()
        wd = str(self.FolderEntry.text())
                 
        os.chdir(wd+"/Rotation_Images")
        framerate = self.FrameRateSB.value()
        fid = self.FilenameEntry.text()
        ffmpeg = self.FFmpegBin.text()
        
        output = fid+"_movie.mpg"
        systemcall = str(ffmpeg)+" -r " + str(framerate) + " -y -i " + str(fid)
        systemcall += '%04d.jpg'
        systemcall += " -sameq "
        systemcall += str(output)
        print systemcall
        os.system(systemcall)  
        os.chdir(olddir)      

class SaveImageOptionsWindow(OptionsWindow):
    def __init__(self,VtkQtFrame,MainWindow):
        self.VtkQtFrame = VtkQtFrame
        self.MainWindow = MainWindow
        OptionsWindow.__init__(self,self.MainWindow,"Save Image") 
        
        self.Resolution = [0]*2

        row=self.newRow(align="HTCenter")
        
        self.group = GenericForm(title="Save Image of 'Render Window "+str(self.VtkQtFrame.ID)+"'",doNotShrink=True,show=True)
        row.addWidget(self.group) 

        row=self.group.newRow(align="HTCenter")
        self.RenderTypebuttongroup = QtGui.QButtonGroup(self)
        self.RenderTypebuttongroup.setExclusive(1)
        self.POVButton = QtGui.QPushButton(QtGui.QIcon(str(IconDir)+'pov-icon.png'), 'POV-Ray')
        self.POVButton.setCheckable(1)
        self.VTKButton = QtGui.QPushButton(QtGui.QIcon(str(IconDir)+'vtk-icon.png'), 'VTK')
        self.VTKButton.setCheckable(1)
        self.VTKButton.setChecked(1)
        self.RenderTypebuttongroup.addButton(self.POVButton)
        self.RenderTypebuttongroup.addButton(self.VTKButton)
        self.connect(self.RenderTypebuttongroup, QtCore.SIGNAL('buttonClicked(int)'), self.setRenderType)
        row.addWidgets((self.POVButton,self.VTKButton))
        
        row=self.group.newRow(align="HTCenter")
        self.UseCurrentResolutionCB = QtGui.QCheckBox("Use current resoluton")
        self.UseCurrentResolutionCB.setEnabled(1)
        self.UseCurrentResolutionCB.setChecked(1)
        self.connect(self.UseCurrentResolutionCB, QtCore.SIGNAL('stateChanged(int)'), self.setUseResolution)
        row.addWidget(self.UseCurrentResolutionCB)
       
        row=self.group.newRow(align="HTCenter")
        self.reslab= QtGui.QLabel("Resolution")
        self.reslab.setEnabled(0)
        self.ImageWidthSB = QtGui.QSpinBox()
        self.ImageWidthSB.setMaximum(2500)
        self.ImageWidthSB.setValue(800)
        
        self.ImageWidthSB.setEnabled(0)
        self.reslab2= QtGui.QLabel("x")
        self.reslab2.setEnabled(0)
        self.ImageHeightSB = QtGui.QSpinBox()
        self.ImageHeightSB.setMaximum(2500)
        self.ImageHeightSB.setValue(600)
        self.ImageHeightSB.setEnabled(0)
        
        self.connect(self.ImageWidthSB, QtCore.SIGNAL('valueChanged(int)'), self.changeResolutionW)
        self.connect(self.ImageHeightSB, QtCore.SIGNAL('valueChanged(int)'), self.changeResolutionH)
        row.addWidgets((self.reslab,self.ImageWidthSB,self.reslab2,self.ImageHeightSB))
        
        row=self.group.newRow(align="HTCenter")
        lab= QtGui.QLabel("Filename:")
        self.FilenameEntry = QtGui.QLineEdit()
        self.FilenameEntry.setMinimumWidth(80)
        row.addWidgets((lab,self.FilenameEntry))
        
        row=self.group.newRow(align="HTCenter")
        self.SaveButton = QtGui.QPushButton("Save")
        self.connect(self.SaveButton, QtCore.SIGNAL('clicked()'), self.save)
        self.SaveAsButton = QtGui.QPushButton("Save As")
        self.connect(self.SaveAsButton, QtCore.SIGNAL('clicked()'), self.saveAs)
        row.addWidgets((self.SaveButton,self.SaveAsButton))
        
    def changeResolutionH(self,val):    
        self.Resolution[1] = val
        
    def changeResolutionW(self,val):
        self.Resolution[0] = val

    def setUseResolution(self,val):
        printd("RES CHECK")
        if(self.UseCurrentResolutionCB.isChecked()):
            self.reslab.setEnabled(0)
            self.ImageWidthSB.setEnabled(0)
            self.reslab2.setEnabled(0)
            self.ImageHeightSB.setEnabled(0)
        else:
            self.reslab.setEnabled(1)
            self.ImageWidthSB.setEnabled(1)
            self.reslab2.setEnabled(1)
            self.ImageHeightSB.setEnabled(1)
    def setRenderType(self,val):
        if(self.POVButton.isChecked()):
            self.RenderType = "POV"
            #self.VideoImageType = "png"
            #self.VideoPngCheck.setChecked(1)
            #self.ImageType = "png"
            #self.PngCheck.setChecked(1)
        
        if(self.VTKButton.isChecked()):
            self.RenderType = "VTK"

    
    def saveAs(self):
        printd("SAVING")
        fdiag = QtGui.QFileDialog()
        fdiag.setModal(1)
        fdiag.setAcceptMode(fdiag.AcceptSave)
        #fdiag.setFilters([".jpg",".png"])
        fdiag.setFileMode(fdiag.AnyFile)
        
        ret = fdiag.exec_()
        if  ret == QtGui.QDialog.Accepted:
            f=fdiag.selectedFiles()[0]
            #ftype = str(fdiag.selectedFilter()).split("(")[0].rstrip()
        else:
            return
        if(self.UseCurrentResolutionCB.isChecked()):
            self.VtkQtFrame.saveImage(str(f),overwrite=True,resolution=None)
        else:
            self.VtkQtFrame.saveImage(str(f),overwrite=False,resolution=self.Resolution) 
        self.FilenameEntry.setText(f)
        fdiag.close()
       
    def save(self):     
        f = self.FilenameEntry.text()
        if(self.UseCurrentResolutionCB.isChecked()):
            self.VtkQtFrame.saveImage(str(f),overwrite=False,resolution=None)
        else:
            self.VtkQtFrame.saveImage(str(f),overwrite=False,resolution=self.Resolution) 
        
class CameraOptionsWidget(GenericForm):
    def __init__(self, OptionsWindow): 
        self.optionswindow= OptionsWindow
        GenericForm.__init__(self,self.optionswindow,title="Camera Options",doNotShrink=False,isGroup=False)
        
        self.addSeparator()
        self.PosSB = []
        self.FPSB = []
        self.VUSB = []
        Labels = [QtGui.QLabel("Position"),QtGui.QLabel("Focal Point"),QtGui.QLabel("View Up Vector")]
        for i in range(0,3):
            self.PosSB.append(QtGui.QDoubleSpinBox())
            self.PosSB[-1].setSingleStep(0.01)
            self.PosSB[-1].setMinimum(-1000)
            self.PosSB[-1].setMaximum(1000)
            self.PosSB[-1].setMaximumWidth(100)
            self.connect(self.PosSB[-1], QtCore.SIGNAL('editingFinished ()'), self.updateVTKCamera)
            self.FPSB.append(QtGui.QDoubleSpinBox())
            self.FPSB[-1].setSingleStep(0.01)
            self.FPSB[-1].setMinimum(-1000)
            self.FPSB[-1].setMaximum(1000)
            self.FPSB[-1].setMaximumWidth(100)
            self.connect(self.FPSB[-1], QtCore.SIGNAL('editingFinished ()'), self.updateVTKCamera)
            self.VUSB.append(QtGui.QDoubleSpinBox())
            self.VUSB[-1].setSingleStep(0.01)
            self.VUSB[-1].setMinimum(-1000)
            self.VUSB[-1].setMaximum(1000)
            self.VUSB[-1].setMaximumWidth(100)
            self.connect(self.VUSB[-1], QtCore.SIGNAL('editingFinished ()'), self.updateVTKCamera)
            
        row=self.newRow()
        row.addWidget(Labels[0])
        posrow=self.newRow(align="Center")  
        row=self.newRow()
        row.addWidget(Labels[1])
        fprow=self.newRow(align="Center")
        row=self.newRow()
        row.addWidget(Labels[2])
        vurow=self.newRow(align="Center")
        for i in range(0,3):
            posrow.addWidget(self.PosSB[i])
        for i in range(0,3):    
            fprow.addWidget(self.FPSB[i])
        for i in range(0,3):    
            vurow.addWidget(self.VUSB[i])
        row=self.newRow()

        self.addSeparator()    
        self.hide()
        
    def updateCamera(self,VTKCamera): 
        pos = VTKCamera.GetPosition()
        #posstring = "%0.2f,%0.2f,%0.2f" % (pos[0],pos[1],pos[2])
        foc = VTKCamera.GetFocalPoint()
        #focstring = "%0.2f,%0.2f,%0.2f" % (foc[0],foc[1],foc[2])    
        vup = VTKCamera.GetViewUp()
        #printd("POS",pos)
        #printd("FOC",foc)
        #printd("VUP",vup)
        for i in range(0,3):
            self.PosSB[i].setValue(pos[i])
            self.FPSB[i].setValue(foc[i])
            self.VUSB[i].setValue(vup[i])
    
    def updateVTKCamera(self):   
        pos=[]
        fp=[]
        vu=[]
        for i in range(0,3):
            pos.append(self.PosSB[i].value())
            fp.append(self.FPSB[i].value())
            vu.append(self.VUSB[i].value())
            
        self.optionswindow.VTKWidget.VTKCamera.SetPosition(pos)
        self.optionswindow.VTKWidget.VTKCamera.SetFocalPoint(fp)
        self.optionswindow.VTKWidget.VTKCamera.SetViewUp(vu)
        self.optionswindow.VTKWidget.VTKRenderWindowInteractor.ReInitialize()  
        
        
class InfoOptionsWidget(GenericForm):
    def __init__(self, OptionsWindow): 
        self.optionswindow= OptionsWindow
        GenericForm.__init__(self,self.optionswindow,doNotShrink=False, isGroup=False)
        #self.setMaximumHeight(200)
        self.addSeparator()
        
        row=self.newRow()
        self.infoText = QtGui.QTextEdit()
#        self.infoText.setWordWrapMode(0)
#        self.infoText.setFontPointSize(10)
#        self.infoText.setReadOnly(True)
#        #self.infoText.setMaximumHeight(200)
#    
        row.addWidget(self.infoText)
        
        self.addSeparator()
        self.hide() 
        
        