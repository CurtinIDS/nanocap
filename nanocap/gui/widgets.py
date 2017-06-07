'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: May 9, 2014
Copyright Marc Robinson  2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-


moved form widgets to new module

Simple widgets with layouts,
primarily use BaseWidget


-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
'''


import os,sys
from nanocap.core.util import *
from nanocap.core.globals import *
from nanocap.gui.settings import *

class HolderWidget(QtGui.QWidget):
    '''
    Simple a holder, no alignment etc. Will expand width to fill where added.
    '''
    def __init__(self,widgets=[],stack="H",align=QtCore.Qt.AlignHCenter,spacing=0,margins=[0,0,0,0]):
        QtGui.QWidget.__init__(self, None)
        #self.setObjectName("HolderWidget")
        self.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Preferred)
        self.setStyleSheet(STYLESHEET)
        
        if(stack=="H"):self.containerLayout = QtGui.QHBoxLayout()
        else:self.containerLayout = QtGui.QVBoxLayout()
        self.setLayout(self.containerLayout)
        try:
            self.containerLayout.addWidget(widgets)
            #self.containerLayout.setAlignment(widgets, align)
        except:
            for widget in widgets:
                self.containerLayout.addWidget(widget)
                #self.containerLayout.setAlignment(widget, align)
                
        self.containerLayout.setContentsMargins(*margins)
        self.containerLayout.setSpacing(spacing)
        if(align!=None):self.containerLayout.setAlignment(align)
        

    
    def setBackgroundColour(self,colourstring):
        #self.setStyleSheet("QWidget {background-color: "+colourstring+";}")
        pass
        
    def addWidget(self,widget,align=QtCore.Qt.AlignHCenter):
        self.containerLayout.addWidget(widget)
        #self.containerLayout.setAlignment(widget, align)

class BaseWidget(QtGui.QWidget):
    '''
    Note IF group then the widget will not expand to fill space
    best practice
    
    widget1=BaseWidget(group=True)
    widget2=BaseWidget(group=False)
    widget1.addWidget(widget2)
    
    then add widgets to widget2
    
    if align=None, widgets will stretch... 
    
    '''
    def __init__(self,parent=None,popup=False,w=None,h=None,spacing=0,margins=[0,0,0,0],
                 align=QtCore.Qt.AlignHCenter,show=True,group=False,scroll=False,
                 title="",stack="V",name=None):
            
        if(popup):
            QtGui.QWidget.__init__(self,parent,QtCore.Qt.Tool)
            self.setWindowTitle(title)
            self.setParent(parent)
        else:
            QtGui.QWidget.__init__(self, None)
        
        if(name!=None):self.setObjectName(name)
        
        #self.setObjectName("NoBorder")
        #self.setStyleSheet(STYLESHEET)
        
        self.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Preferred)

        if(stack=="H"):self.form_layout = QtGui.QHBoxLayout()
        else:self.form_layout = QtGui.QVBoxLayout()
        self.form_layout.setContentsMargins(0,0,0,0)
        self.form_layout.setSpacing(0)
        if(align!=None):self.form_layout.setAlignment(align)
        if(group):
             
            self.central_widget = QtGui.QGroupBox(title)
            if(align!=None):self.central_widget.setAlignment(align)
            self.central_widget.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                              QtGui.QSizePolicy.Preferred)
            if(stack=="H"):self.layout = QtGui.QHBoxLayout()
            else:self.layout = QtGui.QVBoxLayout()
            self.layout.setContentsMargins(*margins)
            self.layout.setSpacing(spacing)
            if(align!=None):self.layout.setAlignment(align)
                
            self.central_widget.setLayout(self.layout)
            if(scroll): 
                self.scroll_view = QtGui.QScrollArea(self)
                self.scroll_view.setMinimumWidth(w)
                self.scroll_view.setWidgetResizable(True)
                self.scroll_view.setEnabled(True)
                self.scroll_view.setWidget(self.central_widget)
                if(name!=None):self.scroll_view.setObjectName(name)
                self.form_layout.addWidget(self.scroll_view)
            else:
                self.form_layout.addWidget(self.central_widget)
        
        else:
            if(scroll): 
                self.central_widget = QtGui.QWidget()
                if(stack=="H"):self.layout = QtGui.QHBoxLayout()
                else:self.layout = QtGui.QVBoxLayout()
                self.layout.setContentsMargins(*margins)
                self.layout.setSpacing(spacing)
                if(align!=None):self.layout.setAlignment(align)
                self.central_widget.setLayout(self.layout)
                
                self.scroll_view = QtGui.QScrollArea(self)
                if(name!=None):self.scroll_view.setObjectName(name)
                #self.scroll_view.setMinimumWidth(w)
                self.scroll_view.setWidgetResizable(True)
                self.scroll_view.setEnabled(True)
                self.scroll_view.setWidget(self.central_widget)
                self.form_layout.addWidget(self.scroll_view)
            else:
                self.central_widget = self
                self.layout = self.form_layout
        
        self.setLayout(self.form_layout)
        if(name!=None):self.central_widget.setObjectName(name)
        
        #self.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Preferred)
        #self.setWidgetResizable(True)
        
        self.my_widgets = []
        
        self.w=w
        self.h=h 
  
#         if(show):self.show()
#         else:self.hide()
    
    def bringToFront(self):
        self.setWindowState( (self.windowState() & ~QtCore.Qt.WindowMinimized) | QtCore.Qt.WindowActive)
        self.raise_()
        self.activateWindow()
        self.show()
        
    def show(self):
        
        super(BaseWidget, self).show()
        #for widget in self.my_widgets:widget.show()
    
    def hide(self):
        super(BaseWidget, self).hide()
        #for widget in self.my_widgets:widget.hide()
    
    def newStack(self,spacing=0,margins=[0,0,0,0],align=QtCore.Qt.AlignCenter):
        
        self.holder = QtGui.QWidget()
        self.stackedLayout = QtGui.QStackedLayout()
        self.stackedLayout.setSpacing(spacing)
        self.stackedLayout.setContentsMargins(*margins)
        #self.gridLayout.setAlignment(QtCore.Qt.AlignLeft)
        self.holder.setLayout(self.stackedLayout)
        self.layout.addWidget(self.holder)
        self.layout.setAlignment(self.holder, align)
        return self.stackedLayout
    
    def newGrid(self,spacing=0,margins=[0,0,0,0],align=QtCore.Qt.AlignCenter):
        self.holder = QtGui.QWidget()
        #self.holder.setObjectName("BaseWidget")
        #self.holder.setStyleSheet("QWidget {font-size: 7 pt;}")
        #colourstring="green"
        #self.holder.setStyleSheet("QWidget {background-color: "+colourstring+";}")
        self.holder.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Preferred)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setSpacing(spacing)
        self.gridLayout.setContentsMargins(*margins)
        #self.gridLayout.setAlignment(QtCore.Qt.AlignLeft)
        self.holder.setLayout(self.gridLayout)
        self.layout.addWidget(self.holder)
        self.layout.setAlignment(self.holder, align)
        #self.holder.show()
        return self.gridLayout
    
    def addWidgets_dep(self,widgets,align=QtCore.Qt.AlignHCenter):
        for widget in widgets:
            self.my_widgets.append(widget)
            self.layout.addWidget(widget)
            self.layout.setAlignment(widget, align)
            
    def addWidget_dep(self,widget,align=QtCore.Qt.AlignHCenter,add=True):
        self.my_widgets.append(widget)
        self.layout.addWidget(widget)
        self.layout.setAlignment(widget, align)
        
    def addWidgets(self,widgets,stack="H",spacing=0,margins=[0,0,0,0],align=QtCore.Qt.AlignHCenter,add=True):
        widget = HolderWidget(widgets=widgets,stack=stack,align=align,margins=margins,
                                           spacing=spacing)
        self.my_widgets.append(widget)
        try:self.my_widgets.extend(widgets)
        except:self.my_widgets.append(widgets)
        
        if(add):self.layout.addWidget(widget,align=align)
        return widget
    
    def addWidget(self,widgets,stack="H",spacing=0,margins=[0,0,0,0],align=QtCore.Qt.AlignHCenter,add=True):
        widget =self.addWidgets(widgets, stack, spacing, margins, align,add=add)
        return widget
    
    def center(self):
        screen = QtGui.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)    
    
    def addHeader(self,text,frame=True,align=QtCore.Qt.AlignHCenter,bold=True):       
        layout= QtGui.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(align)
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
        if(frame):layout.addWidget(frame1)
        
        lb = QtGui.QLabel(text)
        f = lb.font()
        f.setBold(True)
        lb.setFont(f)
        #lb.setStyleSheet("QWidget {font: "+str(font_size)+"pt }")
        #if(bold):lb.setStyleSheet("QWidget {font: bold "+str(font_size)+"pt }")
        lb.setObjectName("Header")
        
        layout.addWidget(lb)
        if(frame):layout.addWidget(frame2)
        
        self.addWidget(widget)
        #self.ContentLayout.addWidget(lb)
        #return row
    
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
        self.layout.addWidget(frame)
       
        return frame
    
    def setBackgroundColour(self,colourstring):
        self.setStyleSheet("QWidget {background-color: "+colourstring+";}")
        self.central_widget.setStyleSheet("QWidget {background-color: "+colourstring+";}") 
        pass   
                
    def sizeHint(self):
        if self.w==None and self.h==None:
            return QtCore.QSize()  
        return QtCore.QSize(self.w,self.h)  


class TabWidget(QtGui.QTabWidget):
    def __init__(self):
        QtGui.QTabWidget.__init__(self)
        
    
class Frame(QtGui.QFrame):
    def __init__(self,dummy=False): 
        QtGui.QFrame.__init__(self)   
        layout= QtGui.QVBoxLayout()
        self.setLineWidth(1)
        if(dummy==False):
            self.setFrameShape(QtGui.QFrame.HLine)
            layout.setContentsMargins(30, 10, 30, 10)
        else:
            self.setFrameShape(QtGui.QFrame.NoFrame)
            layout.setContentsMargins(10, 7, 10, 7)
        self.setLayout(layout)
        
class SpinBox(QtGui.QSpinBox):
    def __init__(self,val=0):
        QtGui.QSpinBox.__init__(self)
        self.setMaximum(10000000)
        self.setMinimum(-10000000)
        self.setFixedWidth(80)
        self.setValue(val)
        
class DoubleSpinBox(QtGui.QDoubleSpinBox):
    def __init__(self,val=0):
        QtGui.QDoubleSpinBox.__init__(self)
        self.setMaximum(10000000.0)
        self.setMinimum(-10000000.0)
        self.setFixedWidth(80)
        self.setValue(val)

class ColorButton(QtGui.QPushButton):
    def __init__(self,irgb=(1,0,0),width=25):
        QtGui.QPushButton.__init__(self)
        self.rgb = numpy.array(irgb)*255
        self.irgb = numpy.array(irgb)*255
        self.width = width
        self.setFixedWidth(self.width)
        self.Qcolor = QtGui.QColor(self.rgb[0],self.rgb[1],self.rgb[2])         
        self.setStyleSheet("QPushButton { background-color: %s ; border-radius: 5px }" % self.Qcolor.name())
        #call = lambda button=self: self.changeColor
        self.connect(self, QtCore.SIGNAL('clicked()'), self.changeColor)
    
    def changeColor(self):
        col = self.getQtColour(self.rgb)
        self.setStyleSheet("QPushButton { background-color: %s ; border-radius: 5px }" % col.name())
        self.emit(QtCore.SIGNAL("colorChanged(int,int,int)"),col.red(),col.green(),col.blue())
        printd("emitting",col.red(),col.green(),col.blue())
        
    def getQtColour(self,icol):
        qCol = QtGui.QColor(self.rgb[0],self.rgb[1],self.rgb[2])    
        col = QtGui.QColorDialog().getColor(qCol)
        if col.isValid():return col
        else:return qCol 

class GenericButton(QtGui.QWidget):
    def __init__(self,icon='save.png'):
        QtGui.QWidget.__init__(self, None)
        self.containerLayout = QtGui.QHBoxLayout()
        self.setLayout(self.containerLayout)
        self.button = QtGui.QPushButton()
        self.button.setIcon(QtGui.QIcon(str(IconDir) + icon))
        self.button.setFixedWidth(18)
        self.containerLayout.addWidget(self.button)
        self.containerLayout.setContentsMargins(0, 0, 0, 0)
        self.containerLayout.setSpacing(4)
        self.containerLayout.setAlignment(QtCore.Qt.AlignCenter)
        
#         self.setStyleSheet("QWidget { border: none}")
#         
#         self.button.setStyleSheet(
#         "QPushButton { \
#             border: none;\
#         }\
#             QPushButton:pressed {\
#             background: rgb(105, 105, 105);\
#         }\
#         ")
        
        self.connect(self.button,QtCore.SIGNAL("clicked()"),self.clicked)

    def clicked(self):
        self.emit(QtCore.SIGNAL("clicked()"))
        

class TableWidget(QtGui.QTableWidget):
    def __init__(self,w,h,scrollRowLimit=15,scaleCols=True):
        QtGui.QTableWidget.__init__(self)
        self.h = h
        self.w = w
        self.scrollRowLimit = scrollRowLimit
        self.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding,QtGui.QSizePolicy.Minimum)
        self.verticalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        
        
        self.scaleCols = scaleCols
    
    def setupHeaders(self,headers,widths):
        
       # self.horizontalHeader().setResizeMode(0,QtGui.QHeaderView.Stretch)
        
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        for index,header in enumerate(headers):
            self.setColumnWidth(index,widths[index])
        
        printl("headers setup",headers,widths)
        
        self.col_widths=widths
        
        
        self.resize(QtCore.QSize(self.w,self.h+4))  
        
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
#    
#     def sizeHint(self):    
#          return QtCore.QSize(self.w,self.h) 
    def sizeHint(self):
        self.h=self.horizontalHeader().height()
        
        rl=self.scrollRowLimit if self.rowCount() > self.scrollRowLimit else self.rowCount() 
        #if(self.rowCount()>self.scrollRowLimit):rl = self.scrollRowLimit
          
        for r in range(0,self.rowCount()):
            self.h+=self.rowHeight(r)
        #self.h+=5
        #self.h = self.rowHeight(int)
          
#         self.w = self.verticalHeader().width()
#         for c in range(0,self.columnCount()):
#             self.w+=self.columnWidth(c)
          
        #self.w += self.verticalScrollBar().width()       
  
        #printl(self.h,self.rowCount(),self.rowHeight(0),self.horizontalHeader().height())
        return QtCore.QSize(self.w,self.h+2)