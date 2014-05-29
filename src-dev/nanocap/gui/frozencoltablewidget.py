'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Apr 14, 2014
Copyright Marc Robinson  2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-




-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
'''
from nanocap.core.util import *
from nanocap.core.globals import *
import os,sys,math,copy,random,time,threading,Queue,types
from nanocap.gui.settings import *
from nanocap.gui.tablebuttondelegate import  TableItemDelegate

import numpy,datetime

from nanocap.resources.Resources import *
            
class FrozenTableWidget(QtGui.QWidget):
    def __init__(self,NFrozen=1,DelegateIcons=[]):
        '''
        DelegateIcons = (col,nmodes,files)
        
        '''
        QtGui.QWidget.__init__(self)
        self.NFrozen = NFrozen
        printl("NFrozen",self.NFrozen)
        self.scrollRowLimit = 5
        self.DelegateIcons  = DelegateIcons
        
        #self.MinimaTable.setBackgroundColour("red")
        

        self.contentlayout = QtGui.QStackedLayout(self)
        self.contentlayout.setStackingMode(QtGui.QStackedLayout.StackAll)
        #self.contentlayout.setContentsMargins(0,0,0,0)
        #self.contentlayout.setSpacing(0)
        self.setLayout(self.contentlayout)

        
        self.tableModel = QtGui.QStandardItemModel()
        self.frozenTableView = QtGui.QTableView()
        self.frozenTableView.setModel(self.tableModel)
        self.frozenTableView.setWordWrap(False)
        self.tableView = QtGui.QTableView()
        self.tableView.setModel(self.tableModel)
        self.tableView.setWordWrap(False)
        
        #self.tableView.setSizeGripEnabled(True)
        
        #self.frozenTableView.setStyleSheet("QTableView { border-style: outset; border-width: 1px; border-color: grey;}")
        #self.tableView.setStyleSheet("QTableView { border-style: outset; border-width: 1px; border-color: grey;}")
        
        self.frozenTableView.setObjectName("frozenTableView")
        self.tableView.setObjectName("tableView")


        self.setSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Expanding)

        self.contentlayout.insertWidget(0,self.frozenTableView)
        self.contentlayout.addWidget(self.tableView)
        
         
        self.frozenTableView.setFocusPolicy(QtCore.Qt.NoFocus)
        self.frozenTableView.verticalHeader().hide()
        self.tableView.verticalHeader().hide()
        
        #self.frozenTableView.horizontalHeader().setResizeMode(QtGui.QHeaderView.Fixed);
    
        self.frozenTableView.verticalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.tableView.verticalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        
        self.frozenTableView.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.tableView.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
                
        self.tableView.viewport().stackUnder(self.frozenTableView)
        
        #self.frozenTableView.setStyleSheet("QTableView { border: none;"
        #                                    "background-color: #E0E0E0;}")
                                           #"selection-background-color: #999}") 
        
                                       
        self.frozenTableView.setSelectionModel(self.tableView.selectionModel())
        
        self.connect(self.tableView.horizontalHeader(),QtCore.SIGNAL("sectionResized(int,int,int)"),self.updateSectionWidth)
        
        self.connect(self.tableView.verticalHeader(),QtCore.SIGNAL("sectionResized(int,int,int)"), self.updateSectionHeight)
        
        self.connect(self.frozenTableView.verticalScrollBar(), QtCore.SIGNAL("valueChanged(int)"),self.tableView.verticalScrollBar().setValue)
        
        self.connect(self.tableView.verticalScrollBar(), QtCore.SIGNAL("valueChanged(int)"),self.frozenTableView.verticalScrollBar().setValue)
        
        #self.frozenTableView.show()
        
        self.Nmodes = {}
        
        self.ButtonDelegates = {}
        for i,t in enumerate(self.DelegateIcons):
            
            col,modes = self.DelegateIcons[i][0],self.DelegateIcons[i][1]
            icons = self.DelegateIcons[i][2:]
            self.ButtonDelegate = TableItemDelegate(icons,modes)
            self.ButtonDelegates[col] = self.ButtonDelegate
            self.frozenTableView.setItemDelegateForColumn(col,self.ButtonDelegates[col])
            printl("setting delegate",col)
            self.connect(self.ButtonDelegates[col],QtCore.SIGNAL("buttonPressed(QModelIndex)"),self.buttonPressed)
            
        
        self.tableView.resize(self.sizeHint())    
        self.frozenTableView.resize(self.sizeHint())  
        
        #self.setColumnWidths(headers)
        
        self.init()
        self.repaint()
        self.tableView.repaint()
        self.frozenTableView.repaint()

        #self.frozenTableView.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        #self.tableView.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        
        self.setStretchLastSection(True)
        
        #self.frozenTableView.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.tableView.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
    
    
    def hide_all_columns(self):
        for i in range(0,self.tableModel.columnCount()):
            self.tableView.setColumnHidden(i,True)
            self.frozenTableView.setColumnHidden(i,True)
            
    def hide_column_from_header(self,header):
        hdata = [self.tableModel.headerData(i,QtCore.Qt.Horizontal) for i in range(0,self.tableModel.columnCount())]
        print hdata
        i = hdata.index(header)
        self.tableView.setColumnHidden(i,True)
        self.frozenTableView.setColumnHidden(i,True)
    
    def show_column_from_header(self,header):
        hdata = [self.tableModel.headerData(i,QtCore.Qt.Horizontal) for i in range(0,self.tableModel.columnCount())]
        i = hdata.index(header)
        self.tableView.setColumnHidden(i,False)
        self.frozenTableView.setColumnHidden(i,False)
        
    def setStretchLastSection(self,val):
        self.tableView.horizontalHeader().setStretchLastSection(val)
        self.frozenTableView.horizontalHeader().setStretchLastSection(val)
        
            
    def link_table(self,table):
        self.connect(self.frozenTableView.verticalScrollBar(), QtCore.SIGNAL("valueChanged(int)"),table.tableView.verticalScrollBar().setValue)
        self.connect(self.tableView.verticalScrollBar(), QtCore.SIGNAL("valueChanged(int)"),table.frozenTableView.verticalScrollBar().setValue)
        
        self.connect(table.frozenTableView.verticalScrollBar(), QtCore.SIGNAL("valueChanged(int)"),self.tableView.verticalScrollBar().setValue)
        self.connect(table.tableView.verticalScrollBar(), QtCore.SIGNAL("valueChanged(int)"),self.frozenTableView.verticalScrollBar().setValue)
        
        
        self.tableView.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff);
        
    def buttonPressed(self,index):
        printl("delegate presssed ",index.row(),index.column())
        self.emit(QtCore.SIGNAL("delegatePressed(QModelIndex)"),index)
    
    def setBackgroundColour(self,colourstring):
        #self.setStyleSheet("QWidget {background-color: "+colourstring+";}")
        pass
    
    def set_all_delegates_to_mode(self,mode):
        for key,delegate in self.ButtonDelegates.items():
            delegate.set_all_to_mode(mode)
        
    def init(self):
        for col in range(self.NFrozen,self.tableModel.columnCount()):
            self.frozenTableView.setColumnHidden(col, True)

#         for col in range(0,self.tableModel.columnCount()):
#             printl("is hiddden",self.frozenTableView.isColumnHidden(col))
        
        for col in range(0,self.NFrozen):
            self.frozenTableView.setColumnWidth(col, self.tableView.columnWidth(col) )
        
        self.frozenTableView.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff);
        self.frozenTableView.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff);
        self.frozenTableView.show()
        
        self.updateFrozenTableGeometry()
        
        self.tableView.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel);
        self.tableView.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel);
        self.tableView.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel);
        
        self.frozenTableView.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel);
        self.frozenTableView.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel);
        self.frozenTableView.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel);
                
        self.tableView.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.frozenTableView.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        

    def reset(self):
        for row in range(0,self.tableModel.rowCount()):self.tableModel.removeRow(0)
        #self.tableModel.clear()
        #self.setHeaders(self.headers)
        
    def setHeaders(self,headers):
        self.headers=headers
        self.tableModel.setHorizontalHeaderLabels(headers);
        self.setColumnWidths(headers)
        #self.init()
        self.update()
        self.updateFrozenTableGeometry()
    
    def setColumnWidths(self,headers):
        for col in range(0,self.tableModel.columnCount()):
            self.tableView.setColumnWidth(col,len(headers)*2)
            self.frozenTableView.setColumnWidth(col,len(headers)*2)
            
    def addRow(self,row):
        #self.tableModel.setHorizontalHeaderLabels(self.headers);
        
        currentRow = self.tableModel.rowCount()
        count=0
        
        for i in range(0,self.tableModel.columnCount()):
            if(i not in self.ButtonDelegates.keys()):
                data = row[count]
                if(isinstance(data, datetime.datetime)):data = data.strftime("%Y-%m-%d %H:%M:%S")
                else:data = str(data)
                printd("Adding item",currentRow,count,i,QtGui.QStandardItem(data),data)
                self.tableModel.setItem(currentRow,i,QtGui.QStandardItem(str(data)))
                count+=1
                
        if(len(self.headers)==self.NFrozen):
            self.tableModel.setItem(currentRow,len(self.headers),QtGui.QStandardItem(str("hidden")))
            self.tableView.setColumnHidden(len(self.headers), True)
            #else:    
                #self.modes["{}-{}".format(currentRow,i)] = 0
                
        
#        for i,item in enumerate(row):
#             printl("Adding item",currentRow,count,QtGui.QStandardItem(item),item)
#             if(i not in self.ButtonDelegates.keys()):
#                 self.tableModel.setItem(currentRow,count,QtGui.QStandardItem(str(item)))
#             else:
#                 printl("Adding item",currentRow,count,QtGui.QStandardItem(item),item)
#                 self.tableModel.setItem(currentRow,count,QtGui.QStandardItem(str("ARSE")))
#             count+=1
        

        self.init()
        self.tableView.repaint()
        self.frozenTableView.repaint()
        #self.update()
        #self.updateFrozenTableGeometry()
        
    def updateSectionWidth(self,logicalIndex, null, newSize):
       if(logicalIndex<self.NFrozen):
             self.frozenTableView.setColumnWidth(logicalIndex,newSize);
             self.updateFrozenTableGeometry();
   
    def updateSectionHeight(self,logicalIndex, null, newSize):
        self.frozenTableView.setRowHeight(logicalIndex, newSize);

    def resizeEvent(self,event):
        
        self.updateFrozenTableGeometry()
        
        #event.accept()
        
    def scrollTo(self,index, hint):
        if(index.column()>self.NFrozen):
            self.scrollTo(index, hint);
        
    def updateFrozenTableGeometry(self):
#         try:self.setColumnWidths(self.headers)
#         except:pass
        x=0
        for c in range(0,self.NFrozen):
            x += self.tableView.columnWidth(c)

        self.frozenTableView.setGeometry(self.tableView.verticalHeader().width()+self.tableView.frameWidth(),
                                        self.tableView.frameWidth(), x,
                                        self.tableView.viewport().height()+self.tableView.horizontalHeader().height())
        printd(self.NFrozen,"geometry",self.tableView.verticalHeader().width()+self.tableView.frameWidth(),
                                        self.tableView.frameWidth(), x,
                                        self.tableView.viewport().height()+self.tableView.horizontalHeader().height())
        self.tableView.repaint()
        self.frozenTableView.repaint()
        
    def sizeHint(self):
        geo = self.geometry()
        x=0
        for c in range(0,self.tableModel.columnCount()):
            x += self.tableView.columnWidth(c)
        
#         #x-=self.tableView.frameWidth()   
        #self.setMinimumWidth(x)
#         x=0
#         header = self.tableView.horizontalHeader() 
#         for c in range(0,header.count()):
#             printl(c,header.sectionSize(header.logicalIndex(c)))
#             x+=header.sectionSize(c)
#             self.tableView.setColumnWidth(c,header.sectionSize(c))
#          
#         printd("self.NFrozen",self.NFrozen,x)
        y=0
        for c in range(0,self.tableModel.columnCount()):
            y += self.tableView.rowHeight(c)
        
        self.updateFrozenTableGeometry()
         
        return QtCore.QSize(x*1.5,y+self.tableView.horizontalHeader().height()+2)#+self.tableView.viewport().height())
        
#      QModelIndex FreezeTableWidget::moveCursor(CursorAction cursorAction,
#                                            Qt::KeyboardModifiers modifiers)
#  {
#        QModelIndex current = QTableView::moveCursor(cursorAction, modifiers);
# 
#        if(cursorAction == MoveLeft && current.column()>0
#           && visualRect(current).topLeft().x() < frozenTableView->columnWidth(0) ){
# 
#              const int newValue = horizontalScrollBar()->value() + visualRect(current).topLeft().x()
#                                   - frozenTableView->columnWidth(0);
#              horizontalScrollBar()->setValue(newValue);
#        }
#        return current;
#  }   