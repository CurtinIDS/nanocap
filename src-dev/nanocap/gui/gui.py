'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Apr 10, 2014
Copyright Marc Robinson  2014
'''

from nanocap.gui.settings import *
from nanocap.core.globals import *
from nanocap.core.util import *
from nanocap.core import util
from nanocap.gui import threadmanager
from nanocap.gui import dock
from nanocap.gui import structuregenwindow
from nanocap.gui import singlestructuregenwindow 
from nanocap.gui import exportstructurewindow
from nanocap.gui import loadfromfilewindow 
from nanocap.gui import preferenceswindow
from nanocap.gui import helpwindow 
from nanocap.gui import aboutwindow
from nanocap.gui import dbviewer 
from nanocap.gui import widgets 
from nanocap.gui import common 
from nanocap.rendering import vtkqtrenderwidgets
from nanocap.gui import bottomdock

from vtk import vtkRenderWindow,vtkGenericRenderWindowInteractor,\
                vtkRenderer,vtkConeSource,vtkPolyDataMapper,vtkActor

# class MDIArea(QtGui.QMdiArea):
#     def __init__(self):
#         QtGui.QMdiArea.__init__(self)
#         
#     def sizeHint(self):
#         return QtCore.QSize(800,700)

class GUI():    
    def __init__(self,mainwindow):       
        self.mainWindow = mainwindow
        
        self.dockWidth = n_DOCKWIDTH
        self.dockHeight = n_DOCKHEIGHT
        
        self.mainwidget = QtGui.QWidget(self.mainWindow)
        self.mdilayout = QtGui.QHBoxLayout(self.mainwidget)

        self.threadManager = threadmanager.QThreadManager()
        
        self.structureGenWindow = structuregenwindow.StructureGenWindow(self,self.mainWindow,self.threadManager)
        self.structureGenWindow.hide()
        
        self.singleStructureGenWindow = singlestructuregenwindow.SingleStructureGenWindow(self,self.mainWindow)
        self.singleStructureGenWindow.hide()
        
        self.dataBaseViewerWindow = dbviewer.DataBaseViewerWindow(self,self.mainWindow,self.threadManager)
        self.dataBaseViewerWindow.hide()
        
        self.exportStructureWindow = exportstructurewindow.ExportStructureWindow()#self,self.mainWindow)
        self.exportStructureWindow.hide()
        
        self.preferencesWindow = preferenceswindow.PreferencesWindow()#self,self.mainWindow)
        self.preferencesWindow.hide()
        
        self.loadFromFileWindow =loadfromfilewindow.LoadFromFileWindow()#self,self.mainWindow)
        self.loadFromFileWindow.hide()
        
        self.aboutWindow =aboutwindow.AboutWindow(self.mainWindow)#self,self.mainWindow)
        self.aboutWindow.hide()
        
        self.helpWindow =helpwindow.HelpWindow()#self,self.mainWindow)
        self.helpWindow.hide()
        
#         self.t = widgets.BaseWidget(group=True,title="Points && Atoms",show=True,align=QtCore.Qt.AlignTop,
#                                                 name="NoBorder",w=100,h=200)
#         
#         self.t.addWidget(common.QL("TEST "))
#         self.t.show()
        
        self.dock = dock.Dock(self,self.mainWindow,self.dockWidth, self.dockHeight,"Toolbar") 
        
        self.bottomDock = bottomdock.BottomDock()
        self.mainWindow.addDockWidget(QtCore.Qt.BottomDockWidgetArea,self.bottomDock)
        self.mainWindow.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.dock)
        
        self.mainWindow.setCorner(QtCore.Qt.BottomLeftCorner,QtCore.Qt.LeftDockWidgetArea)
        printl("Welcome to the Python Carbon Nano-structures generator")

        self.mdilayout.setContentsMargins(0, 0, 0, 0)
        self.mainWindow.setCentralWidget(self.mainwidget)
        
        self.status_bar = QtGui.QStatusBar()
        self.mainWindow.setStatusBar(self.status_bar)
        
        self.dock.draw()    
    
    def setOutputWidget(self,widget):
        util.outputWidget = widget
        
    def callback(self):
        #printl("callback")
        sys.exit()