'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: May 8, 2014
Copyright Marc Robinson  2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

common gui routines


-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
'''

import os,sys
from nanocap.core.util import *
from nanocap.core.globals import *
from nanocap.gui.settings import *


def make_url(lab,link):
    return '<qt> <a href = "'+link+'">'+lab+'</a></qt>'

def QL(*args,**kwargs):
    l = QtGui.QLabel(*args)
    if "link" in kwargs.keys():
        l = QtGui.QLabel('<qt> <a href = "'+kwargs["link"]+'">'+" ".join(*args)+'</a></qt>')
    
    #print kwargs,kwargs['font']
    if "font" in kwargs.keys():
        fs = kwargs['font']
        l.setStyleSheet("QLabel{font: "+str(fs)+";}")
        #print kwargs['font']
    if "align" in kwargs.keys():
        l.setAlignment(kwargs['align'])
    
        l.setAlignment(kwargs['align'])
    #l.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Sunken)
    #l.setWordWrap(True)
    return l

def browse_to_dir():
    fdiag = QtGui.QFileDialog()
    fdiag.setModal(1)
    fdiag.setAcceptMode(fdiag.AcceptOpen)
    fdiag.setFileMode(fdiag.Directory)
    
    ret = fdiag.exec_()
    if  ret == QtGui.QDialog.Accepted:
        f=fdiag.selectedFiles()[0]
        return f
    else:
        return None
    
def browse_to_file():
    fdiag = QtGui.QFileDialog()
    fdiag.setModal(1)
    fdiag.setAcceptMode(fdiag.AcceptOpen)
    fdiag.setFileMode(fdiag.ExistingFile)
    
    ret = fdiag.exec_()
    if  ret == QtGui.QDialog.Accepted:
        f=fdiag.selectedFiles()[0]
        return f
    else:
        return None    