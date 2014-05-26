'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: May 9, 2014
Copyright Marc Robinson  2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

Qt popup window to hold the renderwindow
save options for window rotation

used to be in nanocap.rendering.vtkqtrenderwidgets


-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
'''

from nanocap.core.globals import *
import sys, os, pickle,copy,math,cPickle,threading
from nanocap.gui.settings import *
from nanocap.gui.common import *
from nanocap.core.util import *
import nanocap.resources.Resources as Resources
from nanocap.gui.widgets import BaseWidget,HolderWidget

class SaveImageRotationOptionsWindow(BaseWidget):
    def __init__(self,vtk_qt_frame):#,MainWindow):
        self.vtk_qt_frame = vtk_qt_frame
        BaseWidget.__init__(self,parent=self.vtk_qt_frame,w=200,h=350,title="Save Rotating Image & Encode",
                            popup=True,show=False) 
        
        self.layout.setContentsMargins(5,5,5,5)
        self.layout.setSpacing(2)
        self.Resolution = [0]*2
        
        self.renderer_group = BaseWidget(title="Renderer",group=True,show=True,align=QtCore.Qt.AlignLeft)
        self.renderer_group.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Preferred)
        self.addWidget(self.renderer_group) 

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
        self.renderer_group.addWidgets((self.POVButton,self.VTKButton))
        
        self.res_group = BaseWidget(title="Resolution",show=True,group=True,align=QtCore.Qt.AlignLeft)
        self.res_group.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Preferred)
        self.addWidget(self.res_group) 

        self.UseCurrentResolutionCB = QtGui.QCheckBox("Use window resoluton")
        self.UseCurrentResolutionCB.setEnabled(1)
        self.UseCurrentResolutionCB.setChecked(1)
        self.connect(self.UseCurrentResolutionCB, QtCore.SIGNAL('stateChanged(int)'), self.setUseResolution)
        self.res_group.addWidget(self.UseCurrentResolutionCB)
       
        
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
        self.res_group.addWidgets((self.reslab,self.ImageWidthSB,self.reslab2,self.ImageHeightSB))
        
        
        self.image_output_group = BaseWidget(show=True,group=True,title="Image options",align=QtCore.Qt.AlignLeft)
        self.image_output_group.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Preferred)
        self.addWidget(self.image_output_group) 
        

        self.image_holder = BaseWidget(group=False,title="",show=True)
        self.image_output_group.addWidgets((self.image_holder,))
        row=self.image_holder.newGrid()
        self.FolderEntry = QtGui.QLineEdit()
        self.FolderEntry.setMinimumWidth(80)
        self.GetFolderButton = QtGui.QPushButton("Browse")
        self.connect(self.GetFolderButton, QtCore.SIGNAL('clicked()'), self.getFolder)
        row.addWidget(QL("Folder: "),0,0)
        row.addWidget(self.FolderEntry,0,1)
        row.addWidget(self.GetFolderButton,0,2)
        
        #row=self.image_output_group.newRow(align="HTCenter")
        self.FilenameEntry = QtGui.QLineEdit()
        self.FilenameEntry.setMinimumWidth(80)
        #row.addWidgets((lab,self.FilenameEntry,lab2))
        row.addWidget(QL("Filename: "),1,0)
        row.addWidget(self.FilenameEntry,1,1)
        row.addWidget(QL("<image_number>"),1,2)
        
        #row=self.image_output_group.newRow(align="HTCenter")
        self.ImageWidthSB.setEnabled(0)
        #self.DegLab= QtGui.QLabel("Degree Increment")
        
        self.DegreeStepSB = QtGui.QSpinBox()
        self.DegreeStepSB.setMaximum(360)
        self.DegreeStepSB.setValue(5)
        self.DegreeStepSB.setEnabled(1)
        #row.addWidgets((self.DegLab,self.DegreeStepSB))
        row.addWidget(QL("Degree Increment: "),2,0)
        row.addWidget(self.DegreeStepSB,2,1)

        self.GoButton = QtGui.QPushButton("Go!")
        self.connect(self.GoButton, QtCore.SIGNAL('clicked()'), self.go_rotation)        
        self.layout.addWidget(HolderWidget(self.GoButton))
        
        
        self.video_output_group = BaseWidget(show=True,group=True,title="Video options",align=QtCore.Qt.AlignLeft)
        self.video_output_group.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Preferred)
        self.addWidget(self.video_output_group) 
        self.video_holder = BaseWidget(group=False,title="",show=True)
        self.video_output_group.addWidgets((self.video_holder,))
        
        
        #row=self.video_output_group.newRow(align="HTCenter")
        
        row= self.video_holder.newGrid()
        self.FrameRateSB = QtGui.QSpinBox()
        self.FrameRateSB.setMaximum(360)
        self.FrameRateSB.setValue(5)
        self.FrameRateSB.setEnabled(1)
        self.VideoExtEntry = QtGui.QLineEdit()
        #self.VideoExtEntry.setMinimumWidth(80)
        self.VideoExtEntry.setText(".avi") 
        row.addWidget(QL("Frame Rate: "),0,0)
        row.addWidget(self.FrameRateSB,0,1)
        row.addWidget(QL("Ext: "),0,2)
        row.addWidget(self.VideoExtEntry,0,3)
        
        self.VideoFlags = QtGui.QLineEdit()
        self.VideoFlags.setMinimumWidth(160)
        self.VideoFlags.setText("-qscale 0 -vcodec msmpeg4v2") 
        self.FFmpegBin = QtGui.QLineEdit()
        #self.FFmpegBin.setMinimumWidth(80)
        self.FFmpegBin.setText("ffmpeg") 
        row.addWidget(QL("ffmpeg binary: "),1,0)
        row.addWidget(self.FFmpegBin,1,1,1,3)
        row.addWidget(QL("Flags: "),2,0)
        row.addWidget(self.VideoFlags,2,1,1,3)
        
        self.EncodeVideoButton = QtGui.QPushButton("Encode Video")
        self.connect(self.EncodeVideoButton, QtCore.SIGNAL('clicked()'), self.encode_roationVideo)
        self.layout.addWidget(HolderWidget(self.EncodeVideoButton))
        
        
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
                self.vtk_qt_frame.saveImage(Filename,overwrite=False,resolution=None)
            else:
                self.vtk_qt_frame.saveImage(Filename,overwrite=False,resolution=self.Resolution)
            
            self.vtk_qt_frame.rotate(degPerRotation)
            #self.vtk_qt_frame.VTKCamera.Azimuth(degPerRotation)
            
    def encode_roationVideo(self):  
        olddir = os.getcwd()
        wd = str(self.FolderEntry.text())
                 
        os.chdir(wd+"/Rotation_Images")
        framerate = self.FrameRateSB.value()
        fprefix = self.FilenameEntry.text()
        ffmpeg = self.FFmpegBin.text()
        vidext = self.VideoExtEntry.text()
        ext = '.jpg'
        format = '%04d'
        
        output = fprefix+"_movie"+vidext
        
        systemcall = str(ffmpeg)+" -r " + str(framerate) + " -y "
        systemcall += " -i " + str(fprefix)+str(format)+str(ext)
        systemcall += " "+str(self.VideoFlags.text())
        systemcall += " "+str(output)
        
        print systemcall
        os.system(systemcall)  
        os.chdir(olddir) 