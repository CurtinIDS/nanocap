'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: May 13, 2014
Copyright Marc Robinson  2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

NanoCap help window.

Current uses the reStructuredText
in the nanocap.help directory.

This needs to be link with online 
docs... 

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
'''


from nanocap.core.globals import *
import os,sys,math,copy,random,time,threading,Queue,types,glob,re
import docutils.core as core
import numpy
from nanocap.core.util import *
from nanocap.core import minimisation,triangulation,minimasearch,structurelog

from nanocap.gui.settings import *
from nanocap.gui.common import *
from nanocap.gui.widgets import SpinBox,DoubleSpinBox,HolderWidget,BaseWidget,Frame
import nanocap.gui.structuretable as structuretable
import nanocap.gui.progresswidget as progresswidget
import nanocap.gui.structureinputoptions as structureinputoptions
import nanocap.gui.minimiserinputoptions as minimiserinputoptions 

from nanocap.structures import fullerene
from nanocap.structures import cappednanotube



class HelpWindow(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)

        self.setWindowTitle("Help")
        
        self.setSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Preferred)
        
        self.contentlayout = QtGui.QGridLayout(self)
        self.contentlayout.setContentsMargins(5,5,5,5)
        self.contentlayout.setSpacing(5)
        #self.contentlayout.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        self.contentlayout.setAlignment(QtCore.Qt.AlignLeft)
        self.setLayout(self.contentlayout)
        
        
        '''
        only use the .tex derived html files. there's a problem with bundling
        docutils with py2app (outdated recipe?) so cannot use 
        core.publish_string
        '''

        self.options_holder = BaseWidget(self,group=False,show=True,align = QtCore.Qt.AlignTop)         
#         self.text_edit = QtGui.QTextBrowser()
#         self.text_edit.setReadOnly(True) 
#         self.text_edit.setOpenExternalLinks(True)
#         self.text_edit.setSearchPaths([get_root()+"/help/docs/",get_root()+"/help/docs/styles/"])
#         lines = open(get_root()+"/help/docs/index.html","r").read()
#         self.text_edit.insertHtml(lines)
        
        self.text_edit = QtWebKit.QWebView()
        self.text_edit.load(QtCore.QUrl(get_root()+"/help/docs/index.html"))
        
        
        
        self.options_holder.addWidget(self.text_edit,align = QtCore.Qt.AlignTop)
        self.contentlayout.addWidget(self.options_holder,0,1)

    def option_changed(self,index):
        option = self.options_list.currentItem().text()
        for form in self.options.values():form.hide()
        
        self.options[option].show()
        
    def sizeHint(self):
        return QtCore.QSize(750,400) 
            
    def bringToFront(self):
        self.raise_()
        self.show()    