'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: July 20 2012
Copyright Marc Robinson 2013
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

Basic Qt widgets

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
'''
from nanocap.core.globals import *
import os,time,platform,random,math
from nanocap.core.globals import QT
QtGui, QtCore = QT.QtGui, QT.QtCore
 
from numpy import *
from nanocap.core.util import *

class ShowButton(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self, None)
        self.containerLayout = QtGui.QHBoxLayout()
        self.setLayout(self.containerLayout)
        self.checkbox = QtGui.QCheckBox()
        self.checkbox.setFixedWidth(25)
        self.containerLayout.addWidget(self.checkbox)
        self.containerLayout.setContentsMargins(0, 0, 0, 0)
        self.containerLayout.setSpacing(4)
        self.containerLayout.setAlignment(QtCore.Qt.AlignCenter)

class SaveButton(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self, None)
        self.containerLayout = QtGui.QHBoxLayout()
        self.setLayout(self.containerLayout)
        self.button = QtGui.QPushButton()
        self.button.setIcon(QtGui.QIcon(str(IconDir) + 'save.png'))
        self.button.setFixedWidth(18)
        self.containerLayout.addWidget(self.button)
        self.containerLayout.setContentsMargins(0, 0, 0, 0)
        self.containerLayout.setSpacing(4)
        self.containerLayout.setAlignment(QtCore.Qt.AlignCenter)
        
        colourstring="red"
        self.setStyleSheet("QWidget { border: none}")
        
        self.button.setStyleSheet(
        "QPushButton { \
            border: none;\
        }\
            QPushButton:pressed {\
            background: rgb(105, 105, 105);\
        }\
        ")

class TableWidget(QtGui.QTableWidget):
    def __init__(self,w,h,scrollRowLimit=15,scaleCols=True):
        QtGui.QTableWidget.__init__(self)
        self.h = h
        self.w = w
        self.scrollRowLimit = scrollRowLimit
        self.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding,QtGui.QSizePolicy.Minimum)
        self.verticalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.scaleCols = scaleCols
        
    def sizeHinta(self):
        height = QtGui.QTableWidget.sizeHint(self).height()

        # length() includes the width of all its sections
        width = self.horizontalHeader().length() 

        # you add the actual size of the vertical header and scrollbar
        # (not the sizeHint which would only be the preferred size)                  
        width += self.verticalHeader().width()        
        width += self.verticalScrollBar().width()       

        # and the margins which include the frameWidth and the extra 
        # margins that would be set via a stylesheet or something else
        margins = self.contentsMargins()
        width += (margins.left() + margins.right())

        return QtCore.QSize(width, height)
    
    def setupHeaders(self,headers,widths):
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        for index,header in enumerate(headers):
            self.setColumnWidth(index,widths[index])
        
        printl("headers setup",headers,widths)
        
        self.col_widths=widths
        
        
    def resizeEvent (self,event):
        #printl("resizeEvent",self.width())
        
        if(self.scaleCols==True):
            oldwidth = self.horizontalHeader().length() 
            
            width = self.width()
            
            ratio = float(width)/float(numpy.sum(self.col_widths))
            if(ratio<1.0):
                for c in range(0,self.columnCount()):
                    self.setColumnWidth(c,self.col_widths[c])
                return
            width_per_c = math.ceil(float(width)/float(self.columnCount()))
            
            #printl("width_per_c")
            
            for c in range(0,self.columnCount()):
                self.setColumnWidth(c,self.col_widths[c]*ratio)
            
            margins = self.contentsMargins()
            extra = self.width() - self.horizontalHeader().length() - self.verticalHeader().width() - margins.left() - margins.right()
            
            #printl("additional",extra)
            req = extra
            c=0
            while req !=0:
                if(c>self.columnCount()):c=0
                if(req>0):
                    self.setColumnWidth(c,self.columnWidth(c)+1)
                    #printl("expanding col",c)
                    req-=1
                else:
                    self.setColumnWidth(c,self.columnWidth(c)-1)
                    #printl("reducing col",c)
                    req+=1
                c+=1    
            
        else:
            for c in range(0,self.columnCount()):
                self.setColumnWidth(c,self.col_widths[c])
        
    def sizeHint(self):
        self.h=self.horizontalHeader().height()
        rl=self.scrollRowLimit if self.rowCount() > self.scrollRowLimit else self.rowCount() 
        #if(self.rowCount()>self.scrollRowLimit):rl = self.scrollRowLimit
        
        for r in range(0,rl):self.h+=self.rowHeight(r)
        self.h+=5
        #self.h = self.rowHeight(int)
        
        self.w = self.verticalHeader().width()
        for c in range(0,self.columnCount()):
            self.w+=self.columnWidth(c)
        
        #self.w += self.verticalScrollBar().width()       

        #printl(self.h,self.rowCount(),self.rowHeight(0),self.horizontalHeader().height())
        return QtCore.QSize(self.w+20,self.h)

class SpinBox(QtGui.QSpinBox):
    def __init__(self):
        QtGui.QSpinBox.__init__(self)
        self.setMaximum(10000000)
        self.setMinimum(-10000000)
        self.setFixedWidth(80)
        
class DoubleSpinBox(QtGui.QDoubleSpinBox):
    def __init__(self):
        QtGui.QDoubleSpinBox.__init__(self)
        self.setMaximum(10000000.0)
        self.setMinimum(-10000000.0)
        self.setFixedWidth(80)


class HolderWidget(QtGui.QWidget):
    def __init__(self,widgets):
        QtGui.QWidget.__init__(self, None)
        self.containerLayout = QtGui.QHBoxLayout()
        self.setLayout(self.containerLayout)
        try:
            self.containerLayout.addWidget(widgets)
        except:
            for widget in widgets:self.containerLayout.addWidget(widget)
        self.containerLayout.setContentsMargins(0, 0, 0, 0)
        self.containerLayout.setSpacing(2)
        self.containerLayout.setAlignment(QtCore.Qt.AlignCenter)

class GenericForm(QtGui.QWidget):
    def __init__(self, parent=None,width=10.0,title=None,show=False,isGroup=True,
              doNotShrink=False,popup=False,isScrollView=False):
        if(popup):
            QtGui.QWidget.__init__(self)
            #self.setParent(parent)
        else:
            QtGui.QWidget.__init__(self,parent)

        #QtGui.QWidget.__init__(self,self.MainWindow,QtCore.Qt.Tool | QtCore.Qt.WindowStaysOnTopHint)
        self.setSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Preferred)
        
        self.width = width
        if(doNotShrink==True):self.setMinimumWidth(self.width)
        self.parent = parent
        self.title = title
        self.isGroup = isGroup
        self.isScrollView=isScrollView
        #self.setFixedWidth(self.width-10)
        
        self.FormLayout = QtGui.QVBoxLayout()
        self.FormLayout.setSpacing(0)
        self.FormLayout.setContentsMargins(0,0,0,0)
        self.FormLayout.setAlignment( QtCore.Qt.AlignCenter)
    
        if(self.isGroup):
            self.Group = QtGui.QGroupBox(self.title)
            self.Group.setAlignment(QtCore.Qt.AlignCenter)
            if(self.isScrollView==True):
                
                self.ScrollWidget = QtGui.QWidget()
                
                
                self.ScrollLayout = QtGui.QVBoxLayout()
                self.ScrollLayout.setSpacing(0)
                self.ScrollLayout.setContentsMargins(0,0,0,0)
                self.ScrollLayout.setAlignment( QtCore.Qt.AlignTop)
                self.ScrollWidget.setLayout(self.ScrollLayout)
                
                self.ScrollView = QtGui.QScrollArea(self)
                self.ScrollView.setMinimumWidth(self.width)
                #self.ScrollView.setMinimumHeight(200)
                self.ScrollView.setWidgetResizable(True)
                self.ScrollView.setEnabled(True)
                self.ScrollView.setWidget(self.ScrollWidget)
                #self.ScrollView.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Minimum)  
                

                self.ContentLayout = QtGui.QVBoxLayout()
                self.ContentLayout.setSpacing(0)
                self.ContentLayout.setContentsMargins(0,0,0,0)
                self.ContentLayout.setAlignment(QtCore.Qt.AlignTop)
                    
                self.Group.setLayout(self.ContentLayout)
                self.ScrollLayout.addWidget(self.Group)
                
                self.FormLayout.addWidget(self.ScrollView)
            else:    
                self.ContentLayout = QtGui.QVBoxLayout()
                self.ContentLayout.setSpacing(0)
                self.ContentLayout.setContentsMargins(0,0,0,0)
                self.ContentLayout.setAlignment( QtCore.Qt.AlignTop)
                    
                self.Group.setLayout(self.ContentLayout)
                self.FormLayout.addWidget(self.Group)
        else:
            if(self.isScrollView==True):
                
                self.ScrollWidget = QtGui.QWidget()
                
                
                self.ScrollLayout = QtGui.QVBoxLayout()
                self.ScrollLayout.setSpacing(0)
                self.ScrollLayout.setContentsMargins(0,0,0,0)
                self.ScrollLayout.setAlignment( QtCore.Qt.AlignTop)
                self.ScrollWidget.setLayout(self.ScrollLayout)
                
                self.ScrollView = QtGui.QScrollArea(self)
                self.ScrollView.setMinimumWidth(self.width)
                #self.ScrollView.setMinimumHeight(200)
                self.ScrollView.setWidgetResizable(True)
                self.ScrollView.setEnabled(True)
                self.ScrollView.setWidget(self.ScrollWidget)
                #self.ScrollView.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Minimum)  
                


                   
                self.ContentWidget = QtGui.QWidget()
                self.ContentLayout = QtGui.QVBoxLayout()
                self.ContentLayout.setSpacing(0)
                self.ContentLayout.setContentsMargins(0,0,0,0)
                self.ContentLayout.setAlignment(QtCore.Qt.AlignCenter)   
                    
                self.ContentWidget.setLayout(self.ContentLayout)
                self.ScrollLayout.addWidget(self.ContentWidget)
                
                self.FormLayout.addWidget(self.ScrollView)
            else:
                self.ContentWidget = QtGui.QWidget()
                self.ContentLayout = QtGui.QVBoxLayout()
                self.ContentLayout.setSpacing(0)
                self.ContentLayout.setContentsMargins(0,0,0,0)
                self.ContentLayout.setAlignment(QtCore.Qt.AlignCenter)
                if(self.title!=None):
                    self.TitleLabel = QtGui.QLabel(self.title) 
                    row = FormRow()
                    row.addWidget(self.TitleLabel)
                    self.ContentLayout.addWidget(row)
                    #self.ContentLayout.addWidget(self.TitleLabel)  
                self.ContentWidget.setLayout(self.ContentLayout)
                self.FormLayout.addWidget(self.ContentWidget)  
        self.setLayout(self.FormLayout)
        #self.parent.addWidget(self)
        #self.parent.addWidget(self)    
        
        #        self.show()
        self.hide()
        #       
        if(show):
            self.show() 
        
    def setTitle(self,string):
    
        self.Group.setTitle(string)
        
    def newRow(self,align=None):
        row = FormRow(align=align)
        self.ContentLayout.addWidget(row)
        return row
    
    def newGrid(self):
        widget = QtGui.QWidget()
        self.ContentLayout.addWidget(widget) 
        gridLayout = QtGui.QGridLayout()
        gridLayout.setSpacing(2)
        gridLayout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(gridLayout)
        
        return gridLayout
    
    
    def addHeaderOld(self,text):
        row = self.newRow()
        lb = QtGui.QLabel(text)
        f = lb.font()
        f.setBold(True)
        lb.setFont(f)
        lb.setStyleSheet("QWidget {font: bold 11pt }")
        row.addWidget(lb)
        #self.ContentLayout.addWidget(lb)
        return row
    
    def addHeader(self,text):
        row = self.newRow()
        
        layout= QtGui.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(QtCore.Qt.AlignHCenter)
        flayout1= QtGui.QVBoxLayout()
        flayout2= QtGui.QVBoxLayout()
        #flayout1.setContentsMargins(0, 0, 0, 0)
        #flayout2.setContentsMargins(0, 0, 0, 0)
        
        frame1 = QtGui.QFrame()
        frame1.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Preferred)
        frame1.setLineWidth(1)
        frame2 = QtGui.QFrame()
        frame2.setLineWidth(1)
        frame2.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Preferred)
        frame1.setFrameShape(QtGui.QFrame.HLine)
        frame2.setFrameShape(QtGui.QFrame.HLine)
        frame1.setLayout(flayout1)
        frame2.setLayout(flayout2)
        
        widget=QtGui.QWidget()
        widget.setLayout(layout)
        widget.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Preferred)
        layout.addWidget(frame1)
        
        lb = QtGui.QLabel(text)
        f = lb.font()
        f.setBold(True)
        lb.setFont(f)
        lb.setStyleSheet("QWidget {font: bold 11pt }")
        layout.addWidget(lb)
        layout.addWidget(frame2)
        
        row.addWidget(widget)
        #self.ContentLayout.addWidget(lb)
        return row
    
    def addSubHeader(self,text):
        row = self.newRow()
        lb = QtGui.QLabel(text)
        f = lb.font()
        f.setBold(True)
        lb.setFont(f)
        lb.setStyleSheet("QWidget {font: 11pt }")
        row.addWidget(lb)
        #self.ContentLayout.addWidget(lb)
        return row
    
    def addSeparator(self,dummy=False):
        
        
        frame = QtGui.QFrame()
        layout= QtGui.QVBoxLayout()
        frame.setLineWidth(1)
        if(dummy==False):
            frame.setFrameShape(QtGui.QFrame.HLine)
            layout.setContentsMargins(30, 10, 30, 10)
        else:
            frame.setFrameShape(QtGui.QFrame.NoFrame)
            layout.setContentsMargins(10, 7, 10, 7)
      
        frame.setLayout(layout)
        self.ContentLayout.addWidget(frame)
       
        return frame
        
    def removeRow(self,row):
        self.ContentLayout.removeWidget(row)    
    
    def removeAllRowsold(self):
        for i in range(0,self.ContentLayout.count()):
            printd("REMOVING ITEM",self.ContentLayout.itemAt(0))
            temp = self.ContentLayout.removeItem(self.ContentLayout.itemAt(0))
            del temp    
    def removeAllRows(self):
        while self.ContentLayout.count() > 0:
            item = self.ContentLayout.takeAt(0)
            if not item:
                continue
            w = item.widget()
            if w:
                w.deleteLater()
    
    
class FormRow(QtGui.QWidget):
    def __init__(self,align=None):        
        QtGui.QWidget.__init__(self)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Preferred)
        self.RowLayout = QtGui.QHBoxLayout(self)
        self.RowLayout.setAlignment(QtCore.Qt.AlignCenter)
        self.RowLayout.setSpacing(2)
        self.RowLayout.setContentsMargins(2,0,2,0)
        if(align=="Right"):
            self.RowLayout.setAlignment(QtCore.Qt.AlignRight)
        if(align=="Left"):
            self.RowLayout.setAlignment(QtCore.Qt.AlignLeft)
        if(align=="Center"):
            self.RowLayout.setAlignment(QtCore.Qt.AlignCenter)    
        if(align=="VCenter"):
            self.RowLayout.setAlignment(QtCore.Qt.AlignVCenter)         
        if(align=="HCenter"):
            self.RowLayout.setAlignment(QtCore.Qt.AlignHCenter)  
        if(align=="HTCenter"):
            self.RowLayout.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)    
        if(align=="Top"):
            self.RowLayout.setAlignment(QtCore.Qt.AlignTop)          
    def align(self,align):
        if(align=="Right"):
            self.RowLayout.setAlignment(QtCore.Qt.AlignRight)
        if(align=="Left"):
            self.RowLayout.setAlignment(QtCore.Qt.AlignLeft)
        if(align=="Center"):
            self.RowLayout.setAlignment(QtCore.Qt.AlignCenter)  
        if(align=="VCenter"):
            self.RowLayout.setAlignment(QtCore.Qt.AlignVCenter)         
        if(align=="HCenter"):
            self.RowLayout.setAlignment(QtCore.Qt.AlignHCenter)  
        if(align=="HTCenter"):
            self.RowLayout.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)    
        if(align=="Top"):
            self.RowLayout.setAlignment(QtCore.Qt.AlignTop)                 
    def addWidget(self,widget):
        self.RowLayout.addWidget(widget)
        #self.RowLayout.setSpacing(0)
        #self.RowLayout.setContentsMargins(0,0,0,0)
    def addWidgets(self,widgets):
        for widget in widgets:
            self.RowLayout.addWidget(widget)
            #self.RowLayout.setSpacing(0)
            #self.RowLayout.setContentsMargins(0,0,0,0)    
    def removeWidget(self,widget):    
        self.RowLayout.removeWidget(widget)
        
class OptionsWindow(QtGui.QWidget):
    def __init__(self, MainWindow,Name,vars=None,popup = True,parent=None):
        self.Name = Name
        self.MainWindow = MainWindow
        if(popup):
            QtGui.QWidget.__init__(self,self.MainWindow,QtCore.Qt.Tool)
            self.setParent(self.MainWindow)
        else:
            QtGui.QWidget.__init__(self)
            #self.setParent(parent)
        #QtGui.QWidget.__init__(self,self.MainWindow,QtCore.Qt.Tool | QtCore.Qt.WindowStaysOnTopHint)
        #self.setSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Preferred)
        
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)        
        #self.setMinimumWidth(200)
        self.center()
        self.setWindowTitle(self.Name)
        self.Layout = QtGui.QVBoxLayout(self)
        self.Layout.setContentsMargins(0,0,0,0)
        self.Layout.setSpacing(0)
        self.vars = vars
#        self.show()
        self.hide() 
        self.init=True
        self.widgetArray = []
        
        self.setLayout(self.Layout)
#        if(debug==1):
#            self.show()
        
        printd("INIT")
    
    def setBackgroundColour(self,colourstring):
        self.setStyleSheet("QWidget {background-color: "+colourstring+";}")
        
    def addWidget(self,widget):
        self.Layout.addWidget(widget)  
        #self.LastWidget = widget
        self.widgetArray.append(widget)
    
    def newRow(self,align=None):
        row = FormRow(align=align)
        self.Layout.addWidget(row)
        return row
        
    def removeWidgets(self):
        printd("Len Widget Array options window", len(self.widgetArray))
        for widget in self.widgetArray:
                widget.hide()
                widget.hideEvents()
                
        printd("RESIZING")     
        self.adjustSize()
    
    def adjustSize(self):
        pass
        
    def moveToMainWindow(self):
        if(self.init==True):self.move(self.MainWindow.x()-(self.width()*1.5),self.MainWindow.y())    
        printd(self.init,self.x()-self.width(),self.y()) 
        self.init=False
             
    def toggleshow(self):
        printd("OPTIONS WINDOW TOGGLE SHOW")
        if(self.isHidden()):
            self.show()
        else:
            self.hide() 
    def center(self):
        screen = QtGui.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)       
        
    def alignRightOfMain(self,xoffset,yoffset):  
        print self.MainWindow.x(),self.MainWindow.y()
        self.move(self.MainWindow.x() + self.MainWindow.width()+int(xoffset*self.MainWindow.x()) , self.MainWindow.y()+int(self.MainWindow.height()*yoffset))  
    
    def alignLeftOfMain(self,xoffset,yoffset):  
        print self.MainWindow.x(),self.MainWindow.y()
        self.move(self.MainWindow.x() - self.width() , self.MainWindow.y())     

    def alignUnderWindow(self,window):  
        print window.y(),window.height()
        self.move(window.x() , window.y()+(window.height()-window.y()))

class TitleBar(GenericForm):        
    def __init__(self,titlestring,widget,noicons=False,switchIcons=False):
        GenericForm.__init__(self,show=True,isGroup=False)
        mainrow = self.newRow()
        self.widget = widget
        self.noicons = noicons
        self.titleString = titlestring
        self.switchIcons = switchIcons
        menubarcol = "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(120,120,120,100), stop:1 rgba(240,240,240,100))"
        itembgcpol = "rgba(120,120,120,100)"
        toolbarcol = "rgb(180,180,180)"
        menufontcol = "rgb(20,20,20)"
        self.widgetHidden=False
        
        #self.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)
        #self.widget.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)
        #self.setBackgroundColour(menubarcol)
        
        if(self.noicons==True):
            row1 = FormRow(align="Center")
            self.lb = QtGui.QLabel(titlestring)
            self.lb.setStyleSheet("QLabel {background-color: rgba(20,20,20,0); font: bold;}")
            row1.addWidget(self.lb)
            
            row0 = FormRow(align="Left")
            if(self.switchIcons==True):
                self.MinimiseBT = QtGui.QPushButton(QtGui.QIcon(str(IconDir)+'ava-minimise-small.png'),'')
            else:
                self.MinimiseBT = QtGui.QPushButton(QtGui.QIcon(str(IconDir)+'ava-maximise-small.png'),'')
            #remove.setShortcut('Ctrl+S+V')
            #self.connect(self.ShowCheck, QtCore.SIGNAL('clicked()'), self.hideRenderedActors)
            self.MinimiseBT.setFixedWidth(20)
            self.MinimiseBT.setFixedHeight(20)
            self.MinimiseBT.setIconSize(QtCore.QSize(20,20))
            self.MinimiseBT.setCheckable(1)
            self.MinimiseBT.setStatusTip('Minimise')
            self.MinimiseBT.setStyleSheet("QPushButton { \
             background-color: rgba(120,120,120,0) ; \
             border: 0px ; \
             border-radius: 2px; padding: 20px} \
             QPushButton:checked { \
             background-color: rgba(120,120,120,0);}\
             QPushButton:pressed { \
             background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(120,120,120,100), stop:1 rgba(240,240,240,100));}" )
            row0.addWidget(self.MinimiseBT)
            self.connect(self.MinimiseBT, QtCore.SIGNAL('toggled(bool)'), self.minimisePressed)
            row2 = FormRow(align="Right")
            row2.addWidget(QtGui.QLabel(""))
            row2.setStyleSheet("QLabel {background-color: rgba(20,20,20,0); font: bold;}")
            mainrow.addWidgets((row0,row1,row2))
            return
        
        row0 = FormRow(align="Left")
        if(self.switchIcons==True):
            self.MinimiseBT = QtGui.QPushButton(QtGui.QIcon(str(IconDir)+'ava-maximise-small.png'),'')
        else:
            self.MinimiseBT = QtGui.QPushButton(QtGui.QIcon(str(IconDir)+'ava-minimise-small.png'),'')
        #remove.setShortcut('Ctrl+S+V')
        #self.connect(self.ShowCheck, QtCore.SIGNAL('clicked()'), self.hideRenderedActors)
        self.MinimiseBT.setFixedWidth(20)
        self.MinimiseBT.setFixedHeight(20)
        self.MinimiseBT.setIconSize(Qt.QSize(20,20))
        self.MinimiseBT.setCheckable(1)
        self.MinimiseBT.setStatusTip('Minimise')
        self.MinimiseBT.setStyleSheet("QPushButton { \
         background-color: rgba(120,120,120,0) ; \
         border: 0px ; \
         border-radius: 2px; padding: 20px} \
         QPushButton:checked { \
         background-color: rgba(120,120,120,0);}\
         QPushButton:pressed { \
         background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(120,120,120,100), stop:1 rgba(240,240,240,100));}" )
        row0.addWidget(self.MinimiseBT)
        self.connect(self.MinimiseBT, QtCore.SIGNAL('toggled(bool)'), self.minimisePressed)
        
        row1 = FormRow(align="Center")
        self.lb = QtGui.QLabel(titlestring)
        self.lb.setStyleSheet("QLabel {background-color: rgba(20,20,20,0); font: bold;}")
        row1.addWidget(self.lb)
        
        
        
        row2 = FormRow(align="Right")
        self.LoadPipelineBT = QtGui.QPushButton(QtGui.QIcon(str(IconDir)+'ava-loadpipeline-small.png'),'')
        #remove.setShortcut('Ctrl+S+V')
        #self.connect(self.ShowCheck, QtCore.SIGNAL('clicked()'), self.hideRenderedActors)
        self.LoadPipelineBT.setFixedWidth(20)
        self.LoadPipelineBT.setFixedHeight(20)
        self.LoadPipelineBT.setIconSize(Qt.QSize(17,20))
        self.LoadPipelineBT.setStatusTip('Load pipeline')
        self.LoadPipelineBT.setStyleSheet("QPushButton { \
         background-color: rgba(120,120,120,0) ; \
         border: 0px solid #8f8f91; \
         border-radius: 2px; } \
         QPushButton:pressed { \
         background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(150,150,150,100), stop:1 rgba(250,250,250,100));}" )
        self.connect(self.LoadPipelineBT, QtCore.SIGNAL('clicked()'), self.loadPressed)


        self.AddItemBT = QtGui.QPushButton(QtGui.QIcon(str(IconDir)+'ava-add-small.png'),'')
        #remove.setShortcut('Ctrl+S+V')
        #self.connect(self.ShowCheck, QtCore.SIGNAL('clicked()'), self.hideRenderedActors)
        self.AddItemBT.setIconSize(Qt.QSize(17,20))
        self.AddItemBT.setFixedWidth(20)
        self.AddItemBT.setFixedHeight(20)
        self.AddItemBT.setStatusTip('Add')
        
        self.AddItemBT.setStyleSheet("QPushButton { \
         background-color: rgba(120,120,120,0) ; \
         border: 0px solid #8f8f91; \
         border-radius: 2px; padding: 20px} \
         QPushButton:pressed { \
         background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(150,150,150,100), stop:1 rgba(250,250,250,100));}" )
        self.connect(self.AddItemBT, QtCore.SIGNAL('clicked()'), self.addPressed)
        
        

        self.emit(QtCore.SIGNAL("loadTitlePressed()"))
        
        row2.addWidget(self.LoadPipelineBT)
        row2.addWidget(self.AddItemBT)
        mainrow.addWidgets((row0,row1,row2))
    
    def addPressed(self):
        self.emit(QtCore.SIGNAL("addTitlePressed()"))
    
    def loadPressed(self):
        self.emit(QtCore.SIGNAL("loadTitlePressed()"))
    
    def hideWidget(self):
        if(self.switchIcons==True):
            self.MinimiseBT.setIcon(QtGui.QIcon(str(IconDir)+'ava-minimise-small.png'))
        else:
            self.MinimiseBT.setIcon(QtGui.QIcon(str(IconDir)+'ava-maximise-small.png'))
        self.widget.hide()
        self.widgetHidden=True
        #self.widget.adjustSize() 
        
    def showWidget(self):
        if(self.switchIcons==True):
            self.MinimiseBT.setIcon(QtGui.QIcon(str(IconDir)+'ava-maximise-small.png'))
        else:
            self.MinimiseBT.setIcon(QtGui.QIcon(str(IconDir)+'ava-minimise-small.png'))
        self.widget.show()
        self.widgetHidden=False
        #self.widget.adjustSize() 
        
    def minimisePressed(self,state):
        printd("minimise pressed",self.titleString,self.MinimiseBT.isChecked(),state)
        self.emit(QtCore.SIGNAL("minimiseTitlePressed(QString)"),self.titleString)    
        
        
        if(self.MinimiseBT.isChecked()==True):
            if(self.switchIcons==True):
                self.MinimiseBT.setIcon(QtGui.QIcon(str(IconDir)+'ava-minimise-small.png'))
            else:
                self.MinimiseBT.setIcon(QtGui.QIcon(str(IconDir)+'ava-maximise-small.png'))
                  
            self.emit(QtCore.SIGNAL("hideTitlePressed(QString)"),self.titleString) 
            self.widget.hide()
            self.widgetHidden=True
        else:
            if(self.switchIcons==True):
                self.MinimiseBT.setIcon(QtGui.QIcon(str(IconDir)+'ava-maximise-small.png'))
            else:
                self.MinimiseBT.setIcon(QtGui.QIcon(str(IconDir)+'ava-minimise-small.png'))
    
            self.emit(QtCore.SIGNAL("showTitlePressed(QString)"),self.titleString)  
            self.widget.show()  
            self.widgetHidden=False
        