'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: May 21, 2014
Copyright Marc Robinson  2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

delegate to add buttons to list items

TODO:
icons and modes for multitple stats

icon1: 1 state, state1.png
icon2: 2 states, state1.png state2.png
etc...

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
'''


import os,time,platform,random,math,copy
from nanocap.core.globals import *
from nanocap.gui.settings import *
from nanocap.gui.common import * 
from nanocap.core.util import *
     
class ListItemDelegate(QtGui.QItemDelegate):
    def __init__(self,icons=['save.png',],noIcons=False,indent=0):
        QtGui.QItemDelegate.__init__(self)
        self.buttonWidthfrac = 9
        self.buttonWidth = 20
        self.pad = 0
        self.interpad = 1
        self.buttonPressed = False
        self.fontpad = 2
        self.icons = icons
        self.mode = 0
                     
    def editorEvent(self,event,model,option,index):
        printd(event.pos(),option.rect.center(),event.type(),QtCore.QEvent.MouseButtonPress,QtCore.QEvent.MouseButtonRelease)
                
        if( event.type() == QtCore.QEvent.MouseButtonPress or event.type() == QtCore.QEvent.MouseButtonRelease or event.type() == QtCore.QEvent.MouseMove):
            pass
        else:
            return True;
        
        item = model.data(index,QtCore.Qt.UserRole)
        buttonRect = copy.copy(option.rect)
        printd("clicked", index.row(),index.column())
        
        x,y,w,h=option.rect.getRect()
        button_clicked=False
        if(event.type() == QtCore.QEvent.MouseButtonRelease):
            for i,icon in enumerate(self.icons):
                buttonRect = copy.copy(option.rect)
                buttonRect.setWidth(self.buttonWidth)
                buttonRect.setHeight(self.buttonWidth)
                newx = x+w-((i+1)*(self.buttonWidth+self.interpad))
                buttonRect.setRect(newx,y+(h-self.buttonWidth)/2,self.buttonWidth,self.buttonWidth)
                if(buttonRect.contains(event.pos())):
                    self.emit(QtCore.SIGNAL("buttonPressed(QModelIndex,int)"),index,i)
                    printl("pressed button",i)
                    button_clicked=True
                    break
            if not button_clicked:self.emit(QtCore.SIGNAL("noButtonPressed(QModelIndex)"),index)
        
    
        return False
        
    def paint(self, painter, option, index):
        
        painter.save()
        model = index.model()
        item = model.data(index)
       
        blueg = QtGui.QColor(150,150,200,100)
        redg = QtGui.QColor(200,150,150,100)
        greyg = QtGui.QColor(180,180,180,100)
        
        #draw the icons:
        
        #printl("paint self.mode",index.row(),index.column(),self.mode,self.icons[mode])
        x,y,w,h=option.rect.getRect()
        if (option.state & QtGui.QStyle.State_Selected):
            painter.setPen(QtGui.QPen(QtCore.Qt.NoPen))
            Brush = QtGui.QBrush()
            Brush.setStyle(QtGui.QApplication.palette().highlight().style())    
            Brush.setColor(QtGui.QColor(255,193,83,90))
            
            Brush.setColor(greyg)
            Brush.setColor(QtGui.QColor(0,91,255,255))
            
            
            #painter.setBrush(QtGui.QApplication.palette().highlight())
            painter.setBrush(Brush)
            #(x,y,w,h)=option.rect.getRect()
            #option.rect.setRect(x+extrapad,y,w+extrapad,h)
            
            highlightRect = copy.copy(option.rect)
            highlightRect.setRect(x,y,w-(len(self.icons)*(self.buttonWidth+self.interpad)),self.buttonWidth)
            
            painter.drawRect(option.rect)
            #option.rect.setRect(x,y,w,h)
            #painter.fillRect(option.rect,QtGui.QColor.yellow())
            painter.restore()
            painter.save()
            
            pen = painter.pen()
            pen.setColor(QtGui.QApplication.palette().color(QtGui.QPalette.HighlightedText))
            pen.setColor(QtGui.QColor(30,30,30))
            pen.setColor(QtGui.QColor(240,240,240))
            painter.setPen(pen)
            font = painter.font()
            font.setWeight(QtGui.QFont.Bold)
            painter.setFont(font)
        
        
        for i,icon in enumerate(self.icons):
            #print "option:",x,y,w,h
            #print "button:",x-self.buttonWidth,y+(h-self.buttonWidth)/2,self.buttonWidth,self.buttonWidth
            buttonRect = copy.copy(option.rect)
            buttonRect.setWidth(self.buttonWidth)
            buttonRect.setHeight(self.buttonWidth)
            newx = x+w-((i+1)*(self.buttonWidth+self.interpad))
            buttonRect.setRect(newx,y+(h-self.buttonWidth)/2,self.buttonWidth,self.buttonWidth)

            Icon = QtGui.QPixmap(str(IconDir) + icon)
            painter.drawPixmap(buttonRect,Icon)
        
        frect = copy.copy(option.rect)
        frect.setX(option.rect.x()+self.fontpad)
        frect.setWidth(option.rect.width()-self.fontpad-len(self.icons)*(self.buttonWidth+self.interpad))
        painter.drawText(frect, QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter , item)
        painter.restore()
        
        return
    
    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable 
        
    def sizeHint(self,option,index):
        model = index.model()
        item = model.data(index,QtCore.Qt.UserRole)
        return QtCore.QSize(self.buttonWidth,self.buttonWidth)    