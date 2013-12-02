'''
Created on Sep 23, 2013

@author: Marc Robinson
'''
from nanocap.core.globals import *
import os,sys,math,copy,random,time,threading,Queue,types
from nanocap.core.globals import QT
QtGui, QtCore = QT.QtGui, QT.QtCore

import numpy

from nanocap.core import globals
from nanocap.gui.forms import TableWidget,ShowButton,SaveButton,HolderWidget
import nanocap.core.processes as processes
from nanocap.core.util import *
import copy


class StructureWindow(QtGui.QWidget):
    def __init__(self,Gui,MainWindow,Processor,ThreadManager,SignalManager,GenType):
        self.Gui = Gui
        self.MainWindow = MainWindow
        self.Processor = Processor
        self.ThreadManager = ThreadManager
        self.SignalManager = SignalManager
        self.GenType = GenType
        self.config = self.Processor.config
        
        QtGui.QWidget.__init__(self,self.MainWindow,QtCore.Qt.Tool)
        self.setParent(self.MainWindow)
        self.setWindowTitle("Generated Structures "+str(GenType))
        self.setSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Preferred)
        
        #row = self.newRow(self)
        self.MinimaTable = TableWidget(260,300)
        self.MinimaTable.setSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Preferred)
        #self.MinimaTable.verticalScrollBar().setDisabled(True)
        #self.MinimaTable.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        
        self.MinimaTable.verticalScrollBar().setStyleSheet("QScrollBar {width:0px;}")        
        
        self.ButtonTable = TableWidget(160,300)
        self.ButtonTable.setSizePolicy(QtGui.QSizePolicy.Fixed,QtGui.QSizePolicy.Preferred)
        self.ButtonTable.verticalHeader().hide()
        #self.ButtonTable.verticalScrollBar().setStyleSheet("QScrollBar {width:0px;}")        
        #self.ButtonTable.verticalScrollBar().setDisabled(True)
        #self.ButtonTable.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        
        self.ButtonTable.horizontalScrollBar().setDisabled(True)
        self.ButtonTable.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        
        
        
        self.VScollBar = QtGui.QScrollBar()
        self.connect(self.ButtonTable.verticalScrollBar(), QtCore.SIGNAL("valueChanged(int)"), self.slideMoved)
        self.connect(self.MinimaTable.verticalScrollBar(), QtCore.SIGNAL("valueChanged(int)"), self.slideMoved)
        
        self.DummyScollBar = QtGui.QScrollBar()
        
        self.contentlayout = QtGui.QHBoxLayout(self)
        self.contentlayout.setContentsMargins(5,5,5,5)
        self.contentlayout.setSpacing(0)
        self.setLayout(self.contentlayout)
        
        self.contentlayout.addWidget(self.MinimaTable)
        self.contentlayout.addWidget(self.ButtonTable)
        
        
        #self.MinimaTable.setVerticalScrollBar(self.DummyScollBar)
        #self.ButtonTable.setVerticalScrollBar(self.VScollBar)
        #self.contentlayout.addWidget(self.VScollBar) 
        #self.ButtonTable.verticalScrollBar().setStyleSheet("QScrollBar {width:0px;}")          
        
        #self.VScollBar.show()    
        
        self.StructureLog = self.Processor.structureLog[self.GenType]
        
        self.setupHeaders(self.StructureLog.headers)
        
        #self.connect(self.ThreadManager, QtCore.SIGNAL("update_structure_table"), self.updateStructureTable)
        
        if(self.GenType=="Fullerene"):
            self.connect(self.SignalManager, QtCore.SIGNAL("update_fullerene_structure_table()"), self.updateStructureTable)
        if(self.GenType=="Nanotube"):
            self.connect(self.SignalManager, QtCore.SIGNAL("update_nanotube_structure_table()"), self.updateStructureTable)
        #self.Processor.updateStructureWindow = types.MethodType( self.updateStructureTable, self.Processor )
        
        size=self.sizeHint()
        printl("initial size",size)
        #self.resize(QtCore.QSize(size.width()+10,size.height()))
        
        #row.addWidget(self.MinimaTable)
    def slideMoved(self,val):
        self.ButtonTable.verticalScrollBar().setValue(val)
        self.MinimaTable.verticalScrollBar().setValue(val)  
        
        
    def slideMoved222(self,val):
        self.ButtonTable.verticalScrollBar().setValue(self.VScollBar.value())
        self.MinimaTable.verticalScrollBar().setValue(self.VScollBar.value())        
        self.ButtonTable.verticalScrollBar().setSliderPosition(val)
        self.MinimaTable.verticalScrollBar().setSliderPosition(val)
        ##self.ButtonTable.scrollContentsBy(0,val)
        #self.MinimaTable.scrollContentsBy(0,val)
        pass
        
    def updateStructureTable(self): 
        printl("updateStructureTable",self.config.opts["GenType"],threading.currentThread())
        
        
        self.config.opts["GUIlock"] = True
        
        if(self.config.opts["GenType"]==self.GenType):
            self.reset()
            
            #self.setupTableWidgets(len(self.Processor.structureLog[self.GenType].structures))
            indexes = self.Processor.structureLog[self.GenType].get_sorted_indexes()
            
            printl("self.Processor.structureLog.lastAdded",self.Processor.structureLog[self.GenType].lastAdded)
            
            #checkRow = numpy.where(indexes==self.Processor.structureLog["Fullerene"].lastAdded)[0][0]
            for count,i in enumerate(indexes):
                row_data = self.Processor.structureLog[self.GenType].get_data(i)
                printl("received",row_data)
                self.addRow(row_data)
            #time.sleep(2)
            
        printl("end updateStructureTable")   
        
        self.VScollBar.setMaximum(self.MinimaTable.verticalScrollBar().maximum())
        self.VScollBar.setMinimum(self.MinimaTable.verticalScrollBar().minimum())     
        self.VScollBar.setSingleStep(self.MinimaTable.verticalScrollBar().singleStep())
        self.VScollBar.setSliderPosition(self.MinimaTable.verticalScrollBar().sliderPosition())
        
        #self.VScollBar  = self.MinimaTable.verticalScrollBar()
        
        self.config.opts["GUIlock"] = False
    
    def setupHeaders(self,headers):

        labels = copy.deepcopy(headers)
        #labels.extend(["D","F","C","Save"])
        
        widths = []

        for index,header in enumerate(labels):
            w = len(header)*8
            if(w<30):w=30
            widths.append(w)
        #widths[-1] = 40    

        self.MinimaTable.setupHeaders(labels,widths)
        self.scaleWindow()
        
        labels = ["Top.","Uncon.","Con.","Save"]
        widths = [40,50,40,40]
        self.ButtonTable.setupHeaders(labels,widths)
    
    def scaleWindow(self):
        height = self.MinimaTable.sizeHint().height()
        width = self.MinimaTable.horizontalHeader().length() 
        width += self.MinimaTable.verticalHeader().width()        
        #width += self.MinimaTable.verticalScrollBar().width()       

        margins = self.contentlayout.contentsMargins()
        width += margins.left() + margins.right()
        self.resize(QtCore.QSize(width+10,height))
    
        
#    def setupTableWidgets(self,N):
#        self.ShowFButtons = []
#        self.ShowCButtons = []        
#        self.ShowDButtons = []
#        self.SaveButtons = []
#        for i in range(0,N):
#            Fcheck = ShowButton()
#            Ccheck = ShowButton()
#            Dcheck = ShowButton()
#            button = SaveButton()
#            #button.setFixedWidth(25)
#            #button.setCheckable(True)
#            #button.setStyleSheet("QPushButton { background-color: grey; border-radius: 5px }")
#            self.SaveButtons.append(button)
#            self.ShowFButtons.append(Fcheck)
#            self.ShowCButtons.append(Ccheck)
#            self.ShowDButtons.append(Dcheck)
#        
#        printl("setup Table Widgets",self.GenType)
        
    def addRow(self,data,checkedRow=None):
        
        printl("adding row checkedRow",checkedRow,self.MinimaTable.rowCount(),self.ButtonTable.rowCount())
        
        row = self.MinimaTable.rowCount()
        self.MinimaTable.insertRow(row)
        self.ButtonTable.insertRow(row)
                
        for i,d in enumerate(data):
            lab1 = QtGui.QTableWidgetItem(str(d))
            self.MinimaTable.setItem(row,i,lab1)    
        
        
        
        
        col = len(data)
        col= 0 
        widget = ShowButton() 
        self.ButtonTable.setCellWidget(row,col,HolderWidget(widget))
        call = lambda checked,row=row,col=col,button=widget: self.showDStructure(row,col,button,checked)
        self.connect(widget.checkbox, QtCore.SIGNAL('stateChanged(int)'), call)
        
        col +=1
        widget = ShowButton() 
        self.ButtonTable.setCellWidget(row,col,HolderWidget(widget))
        call = lambda checked,row=row,col=col,button=widget: self.showFStructure(row,col,button,checked)
        self.connect(widget.checkbox, QtCore.SIGNAL('stateChanged(int)'), call)
        
        col +=1
        widget = ShowButton() 
        self.ButtonTable.setCellWidget(row,col,HolderWidget(widget))
        call = lambda checked,row=row,col=col,button=widget: self.showCStructure(row,col,button,checked)
        self.connect(widget.checkbox, QtCore.SIGNAL('stateChanged(int)'), call)
        
        col +=1
        widget = SaveButton() 
        self.ButtonTable.setCellWidget(row,col,HolderWidget(widget))
        call = lambda row=row,col=col,button=widget: self.saveStructure(row,col,widget)
        self.connect(widget.button, QtCore.SIGNAL('clicked()'), call)
        
        self.MinimaTable.setRowHeight(row,20)
        self.MinimaTable.updateGeometry()
        
        self.ButtonTable.setRowHeight(row,20)
        self.ButtonTable.updateGeometry()
        
#        showDButtonWidget = self.ShowDButtons[row]
#        showFButtonWidget = self.ShowFButtons[row]
#        showCButtonWidget = self.ShowCButtons[row]
#        saveButtonWidget = self.SaveButtons[row]
#        
#        for index,button in enumerate(self.ShowFButtons):
#            #if(index!=row):
#            button.checkbox.setChecked(False)
#            
#        for index,button in enumerate(self.ShowCButtons):
#            button.checkbox.setChecked(False)
#            
##        if(checkedRow==None):
##            showFButtonWidget.checkbox.setChecked(True) 
##        else:
##            self.ShowFButtons[checkedRow].checkbox.setChecked(True) 
#        
#        self.MinimaTable.setCellWidget(row,len(data),showDButtonWidget)
#        self.MinimaTable.setCellWidget(row,len(data)+1,showFButtonWidget)
#        self.MinimaTable.setCellWidget(row,len(data)+2,showCButtonWidget)
#        self.MinimaTable.setCellWidget(row,len(data)+3,saveButtonWidget)
#        
#        call = lambda checked,row=row: self.showDStructure(row,checked)
#        self.connect(showDButtonWidget.checkbox, QtCore.SIGNAL('stateChanged(int)'), call)
#        
#        call = lambda checked,row=row: self.showFStructure(row,checked)
#        self.connect(showFButtonWidget.checkbox, QtCore.SIGNAL('stateChanged(int)'), call)
#        
#        
#        call2 = lambda checked,row=row: self.showCStructure(row,checked)
#        self.connect(showCButtonWidget.checkbox, QtCore.SIGNAL('stateChanged(int)'), call2)     
#        
#        call3 = lambda row=row: self.saveStructure(row)
#        self.connect(saveButtonWidget.button, QtCore.SIGNAL('clicked()'), call3)
        
            
    
    def saveStructure(self,row,col,button):
        printl("will save",row)
        folder = QtGui.QFileDialog().getExistingDirectory()
        printl("folder",folder)
        if(folder==""):return
        
        prev = -1
#        for index,button in enumerate(self.ShowFButtons):
#            buttons = [self.ShowCButtons[index].checkbox,
#                       self.ShowDButtons[index].checkbox,
#                       self.ShowFButtons[index].checkbox]
#            if(buttons[0].isChecked() or buttons[1].isChecked() or buttons[2].isChecked()):
#                prev=index
#                break
            
        ID = int(self.MinimaTable.item(row,0).text())
        self.Processor.selectStructure(ID,carbonMinimised=True)
        
        self.Gui.saveCurrentStructure(folder)
        #self.Processor.saveCurrentStructure(folder)
        self.MinimaTable.selectRow(row)
        self.emit(QtCore.SIGNAL("save_structure(int,int)"),row,prev)
        printl("emitting save structure",row)
        printl("will save structure at row",row)
    


    
    def showDStructure(self,row,col,button,checked):
        if(checked==0):return
        try:
            if(button is not self.lastButton):
                self.lastButton.checkbox.setChecked(False)
        except:pass
        self.lastButton = button
        self.MinimaTable.selectRow(row)
        ID = int(self.MinimaTable.item(row,0).text())
        self.Processor.selectStructure(ID)
    
    def showCStructure(self,row,col,button,checked):
        if(checked==0):return
        try:
            if(button is not self.lastButton):
                self.lastButton.checkbox.setChecked(False)
        except:pass
        self.lastButton = button
        self.MinimaTable.selectRow(row)
        ID = int(self.MinimaTable.item(row,0).text())
        self.Processor.selectStructure(ID,carbonMinimised=True,carbonConstrained=True)
    
    def showFStructure(self,row,col,button,checked):
        if(checked==0):return
        try:
            if(button is not self.lastButton):
                self.lastButton.checkbox.setChecked(False)
        except:pass
        self.lastButton = button
        self.MinimaTable.selectRow(row)
        ID = int(self.MinimaTable.item(row,0).text())
        self.Processor.selectStructure(ID,carbonMinimised=True)
    
    def showDStructureOLD(self,row,checked):
        if(checked==0):return
            
        if(self.ShowDButtons[row].checkbox.isChecked() and checked!=0):
            self.emit(QtCore.SIGNAL("show_d_structure(int)"),row)
                
        for index,button in enumerate(self.ShowDButtons):
            if(index!=row):button.checkbox.setChecked(False)
        
        for index,button in enumerate(self.ShowFButtons):
            button.checkbox.setChecked(False)
        for index,button in enumerate(self.ShowCButtons):
            button.checkbox.setChecked(False)
            
        printl("emitting show_c_structure",row,checked)  
        
        ID = int(self.MinimaTable.item(row,0).text())
        self.Processor.selectStructure(ID,)
        
    def showFStructureOLD(self,row,checked):
        if(checked==0):return
            
        if(self.ShowFButtons[row].checkbox.isChecked() and checked!=0):
            self.emit(QtCore.SIGNAL("show_f_structure(int)"),row)
                
        for index,button in enumerate(self.ShowFButtons):
            if(index!=row):button.checkbox.setChecked(False)
        
        for index,button in enumerate(self.ShowCButtons):
            button.checkbox.setChecked(False)
        for index,button in enumerate(self.ShowDButtons):
            button.checkbox.setChecked(False)
            
        printl("emitting show_f_structure",row,checked)    
        ID = int(self.MinimaTable.item(row,0).text())
        self.Processor.selectStructure(ID,carbonMinimised=True)
        
    def showCStructureOLD(self,row,checked):
        if(checked==0):return
            
        if(self.ShowCButtons[row].checkbox.isChecked() and checked!=0):
            self.emit(QtCore.SIGNAL("show_c_structure(int)"),row)
                
        for index,button in enumerate(self.ShowCButtons):
            if(index!=row):button.checkbox.setChecked(False)
        
        for index,button in enumerate(self.ShowFButtons):
            button.checkbox.setChecked(False)
        for index,button in enumerate(self.ShowDButtons):
            button.checkbox.setChecked(False)
            
        printl("emitting show_c_structure",row,checked)  
        
        ID = int(self.MinimaTable.item(row,0).text())
        self.Processor.selectStructure(ID,carbonMinimised=True,carbonConstrained=True)
    
    def saveStructureOLD(self,row):
        printl("will save",row)
        folder = QtGui.QFileDialog().getExistingDirectory()
        if(folder==None):return
        
        prev = -1
        for index,button in enumerate(self.ShowFButtons):
            buttons = [self.ShowCButtons[index].checkbox,
                       self.ShowDButtons[index].checkbox,
                       self.ShowFButtons[index].checkbox]
            if(buttons[0].isChecked() or buttons[1].isChecked() or buttons[2].isChecked()):
                prev=index
                break
            
        ID = int(self.MinimaTable.item(row,0).text())
        self.Processor.selectStructure(ID,carbonMinimised=True)
        
        self.Gui.saveCurrentStructure(folder)
        #self.Processor.saveCurrentStructure(folder)
        
        self.emit(QtCore.SIGNAL("save_structure(int,int)"),row,prev)
        printl("emitting save structure",row)
        printl("will save structure at row",row)
            
        
    def reset(self):
        self.MinimaTable.clearContents()
        self.MinimaTable.setRowCount(0)
        self.ButtonTable.clearContents()
        self.ButtonTable.setRowCount(0)
    
#    def minimumSizeHint(self):
#        printl(self.MinimaTable.width(),self.MinimaTable.height())
#        tsize = self.MinimaTable.sizeHint()
#        
#        if(self.MinimaTable.rowCount()>0):
#            hw = int(math.log10(self.MinimaTable.rowCount())+1)
#        else:hw=0
#        w = tsize.width()+20+hw*10
#        
#        printl(hw)
#        printl("size",w,tsize.height()+5)
#        #self.setMinimumWidth(w)
#        return QtCore.QSize(w,tsize.height()+5)    
    
    def sizeHint(self):
        #printl(self.MinimaTable.width(),self.MinimaTable.height())
        tsize = self.MinimaTable.sizeHint()
        height = tsize.height()
        width = self.MinimaTable.horizontalHeader().length() 
        width += self.MinimaTable.verticalHeader().width()        
        #width += self.MinimaTable.verticalScrollBar().width()       

        margins = self.contentlayout.contentsMargins()
        width += margins.left() + margins.right()

#        if(self.MinimaTable.rowCount()>0):
#            hw = int(math.log10(self.MinimaTable.rowCount())+1)
#        else:hw=0
#        w = tsize.width()+20+hw*10
#        
#        printl(hw)
#        printl("size",w,tsize.height()+5)
        #self.setMinimumWidth(w)
        #printl(width+10,height)
        
        
        self.MinimaTable.resize(QtCore.QSize(width+10,height+20))
        
#        self.VScollBar.setMaximum(self.MinimaTable.verticalScrollBar().maximum())
#        self.VScollBar.setMinimum(self.MinimaTable.verticalScrollBar().minimum())     
#        self.VScollBar.setSingleStep(self.MinimaTable.verticalScrollBar().singleStep())
#        self.VScollBar.setSliderPosition(self.MinimaTable.verticalScrollBar().sliderPosition())
        
        #printl("resizing minima table")
        return QtCore.QSize(width+10,height+20)
    
    def sizeHintaa(self):
        printl(self.MinimaTable.width(),self.MinimaTable.height())
        tsize = self.MinimaTable.sizeHint()
        
        if(self.MinimaTable.rowCount()>0):
            hw = int(math.log10(self.MinimaTable.rowCount())+1)
        else:hw=0
        w = tsize.width()+20+hw*10
        
        printl(hw)
        printl("size",w,tsize.height()+5)
        #self.setMinimumWidth(w)
        return QtCore.QSize(w,tsize.height()+5)