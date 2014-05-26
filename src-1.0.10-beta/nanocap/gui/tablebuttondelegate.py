'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Apr 14, 2014
Copyright Marc Robinson  2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

item delegate for whole column
of table view. 

Can track the mode of each row to
set the icons.


-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
'''
import os,time,platform,random,math,copy
from nanocap.core.globals import *
from nanocap.gui.settings import *
from nanocap.gui.common import * 
from nanocap.core.util import *
     
class TableItemDelegate(QtGui.QItemDelegate):
    '''
    this is an item delegate for a column!!
    
    '''
    def __init__(self,icons=['save.png',],modes=1,noIcons=False,indent=0):
        QtGui.QItemDelegate.__init__(self)
        self.buttonWidthfrac = 9
        
        self.buttonWidth = 20
        self.pad = 0
        self.interpad = 1
        self.buttonPressed = False
        self.icons = icons
        self.nmodes = modes
        self.mode = {}
        
    def set_all_to_mode(self,mode):
        for key,val in self.mode.items():
            self.mode[key] = mode
             
    def editorEvent(self,event,model,option,index):
        printd(event.pos(),option.rect.center(),event.type(),QtCore.QEvent.MouseButtonPress,QtCore.QEvent.MouseButtonRelease)
                
        if( event.type() == QtCore.QEvent.MouseButtonPress or event.type() == QtCore.QEvent.MouseButtonRelease or event.type() == QtCore.QEvent.MouseMove):
            pass
        else:
            return True;
        
        item = model.data(index,QtCore.Qt.UserRole)
        buttonRect = copy.copy(option.rect)
        printd("clicked", index.row(),index.column())
        
        if(event.type() == QtCore.QEvent.MouseButtonRelease):
            if(buttonRect.contains(event.pos())):
                self.emit(QtCore.SIGNAL("buttonPressed(QModelIndex)"),index)
                self.mode[index.row()]+=1
                if(self.mode[index.row()]==self.nmodes):self.mode[index.row()]=0
                printl("editorEvent self.mode",index.row(),index.column(),self.mode[index.row()],"self.nmodes",self.nmodes)

        return True
        
    def paint(self, painter, option, index):
        
        painter.save()
        model = index.model()
        item = model.data(index,QtCore.Qt.UserRole)
       
        blueg = QtGui.QColor(150,150,200,100)
        redg = QtGui.QColor(200,150,150,100)
        greyg = QtGui.QColor(180,180,180,100)
        
        x,y,w,h=option.rect.getRect()
        buttonRect = copy.copy(option.rect)
        buttonRect.setWidth(self.buttonWidth)
        buttonRect.setHeight(self.buttonWidth)
        buttonRect.setRect(x+(w-self.buttonWidth)/2,y+(h-self.buttonWidth)/2,self.buttonWidth,self.buttonWidth)
        
        try:
            mode = self.mode[index.row()]
        except:
            self.mode[index.row()] = 0
            mode = self.mode[index.row()]
        
        Icon = QtGui.QPixmap(str(IconDir) + self.icons[mode])
        painter.drawPixmap(buttonRect,Icon)
        #printl("paint self.mode",index.row(),index.column(),self.mode,self.icons[mode])
        
        if (option.state & QtGui.QStyle.State_Selected):
            #printl("SELECTED",record)
            painter.setPen(QtGui.QPen(QtCore.Qt.NoPen))
            Brush = QtGui.QBrush()
            Brush.setStyle(QtGui.QApplication.palette().highlight().style())    
            Brush.setColor(QtGui.QColor(255,193,83,90))
            
            #painter.setBrush(QtGui.QApplication.palette().highlight())
            painter.setBrush(Brush)
            #(x,y,w,h)=option.rect.getRect()
            #option.rect.setRect(x+extrapad,y,w+extrapad,h)
            painter.drawRect(option.rect)
            #option.rect.setRect(x,y,w,h)
            #painter.fillRect(option.rect,QtGui.QColor.yellow())
            painter.restore()
            painter.save()
            font = painter.font
            pen = painter.pen()
            pen.setColor(QtGui.QApplication.palette().color(QtGui.QPalette.HighlightedText))
            pen.setColor(QtGui.QColor(30,30,30))
            painter.setPen(pen)
        
        painter.restore()
        
        return
    
    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable 
        
    def sizeHint(self,option,index):
        model = index.model()
        item = model.data(index,QtCore.Qt.UserRole)
        return QtCore.QSize(self.buttonWidth,self.buttonWidth)    
        
