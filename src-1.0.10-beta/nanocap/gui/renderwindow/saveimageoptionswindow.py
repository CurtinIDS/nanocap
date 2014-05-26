'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: May 9, 2014
Copyright Marc Robinson  2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

Qt popup window to hold the renderwindow
save options

used to be in nanocap.rendering.vtkqtrenderwidgets

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
'''

from nanocap.core.globals import *
import sys, os, pickle,copy,math,cPickle,threading
from nanocap.gui.settings import *
from nanocap.core.util import *
import nanocap.resources.Resources as Resources
from nanocap.gui.widgets import BaseWidget

class SaveImageOptionsWindow(BaseWidget):
    def __init__(self,vtk_qt_frame):
        self.vtk_qt_frame = vtk_qt_frame
        BaseWidget.__init__(self,parent=self.vtk_qt_frame,title="Save Image",
                            popup=True,show=False,w=300,h=150) 
        
        self.layout.setContentsMargins(5,5,5,5)
        self.layout.setSpacing(2)
        self.Resolution = [0]*2
        
        
        self.renderer_group = BaseWidget(title="Renderer",show=True,group=True,align=QtCore.Qt.AlignLeft)
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
        self.res_group.addWidget(self.UseCurrentResolutionCB,align=QtCore.Qt.AlignLeft)
       
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
        self.res_group.addWidgets((self.reslab,self.ImageWidthSB,self.reslab2,self.ImageHeightSB),align=QtCore.Qt.AlignLeft)
        
        self.output_group = BaseWidget(show=True,group=True,title="Output")
        self.addWidget(self.output_group) 
        
        lab= QtGui.QLabel("Filename:")
        self.FilenameEntry = QtGui.QLineEdit()
        self.FilenameEntry.setMinimumWidth(80)
        self.output_group.addWidgets((lab,self.FilenameEntry))
        
        self.SaveButton = QtGui.QPushButton("Save")
        self.connect(self.SaveButton, QtCore.SIGNAL('clicked()'), self.save)
        self.SaveAsButton = QtGui.QPushButton("Save As")
        self.connect(self.SaveAsButton, QtCore.SIGNAL('clicked()'), self.saveAs)
        self.addWidgets((self.SaveButton,self.SaveAsButton))
        
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
            self.vtk_qt_frame.saveImage(str(f),overwrite=True,resolution=None)
        else:
            self.vtk_qt_frame.saveImage(str(f),overwrite=False,resolution=self.Resolution) 
        self.FilenameEntry.setText(f)
        fdiag.close()
       
    def save(self):     
        f = self.FilenameEntry.text()
        if(self.UseCurrentResolutionCB.isChecked()):
            self.vtk_qt_frame.saveImage(str(f),overwrite=False,resolution=None)
        else:
            self.vtk_qt_frame.saveImage(str(f),overwrite=False,resolution=self.Resolution) 
    
