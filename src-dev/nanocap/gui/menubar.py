'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Apr 11, 2014
Copyright Marc Robinson  2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

MenuBar on the main toolbar

Will hold add/load structures options


-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
'''

from nanocap.core.globals import *
from nanocap.gui.settings import *


class MenuBar(QtGui.QToolBar):
    def __init__(self,parent):
        QtGui.QToolBar.__init__(self, parent)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Preferred)
        self.set_file_menu()
        self.set_edit_menu()
        self.set_view_menu()
        self.set_help_menu()
        self.set_about_menu()
        self.setObjectName("Main")
    
    def set_about_menu(self):
        self.about_menu = QtGui.QMenu(self)
        self.about_menu.setObjectName('about_menu')
        
        about_action = QtGui.QAction('About NanoCap', self)
        about_action.setStatusTip('About NanoCap')
        call = lambda : self.emit(QtCore.SIGNAL("show_about()"))
        self.connect(about_action, QtCore.SIGNAL('triggered()'), call)
        
        self.about_menu.addAction(about_action)
        about_button = QtGui.QToolButton()
        about_button.setText('About')
        about_button.setPopupMode(QtGui.QToolButton.InstantPopup)
        about_button.setMenu(self.about_menu)
        self.addWidget(about_button)
        
    def set_help_menu(self):
        self.help_menu = QtGui.QMenu(self)
        self.help_menu.setObjectName('help_menu')
        
        help_action = QtGui.QAction('Help', self)
        help_action.setStatusTip('Help')
        help_action.setShortcut('Ctrl+Shift+H')
        call = lambda : self.emit(QtCore.SIGNAL("show_help()"))
        self.connect(help_action, QtCore.SIGNAL('triggered()'), call)
        
        self.help_menu.addAction(help_action)
        help_button = QtGui.QToolButton()
        help_button.setText('Help')
        help_button.setPopupMode(QtGui.QToolButton.InstantPopup)
        help_button.setMenu(self.help_menu)
        self.addWidget(help_button)
        
        
    def set_view_menu(self):
        self.view_menu = QtGui.QMenu(self)
        self.view_menu.setObjectName('view_menu')
        
        view_local_db = QtGui.QAction('View Local Database', self)
        view_local_db.setStatusTip('View Local Database')
        view_local_db.setShortcut('Ctrl+D')
        call = lambda : self.emit(QtCore.SIGNAL("show_local_database()"))
        self.connect(view_local_db, QtCore.SIGNAL('triggered()'), call)
        
        self.view_menu.addAction(view_local_db)
        view_button = QtGui.QToolButton()
        view_button.setText('View')
        view_button.setPopupMode(QtGui.QToolButton.InstantPopup)
        view_button.setMenu(self.view_menu)
        self.addWidget(view_button)
        
    def set_edit_menu(self):
        self.edit_menu = QtGui.QMenu(self)
        self.edit_menu.setObjectName('edit_menu')
        
        copy_structure = QtGui.QAction( 'Copy  ', self)
        copy_structure.setStatusTip('Copy Structure')
        copy_structure.setShortcut('Ctrl+c')
        
        paste_structure = QtGui.QAction( 'Paste  ', self)
        paste_structure.setStatusTip('Paste Structure')
        paste_structure.setShortcut('Ctrl+v')
        
        preferences = QtGui.QAction( 'Preferences  ', self)
        preferences.setStatusTip('Preferences')
        call = lambda : self.emit(QtCore.SIGNAL("show_preferences()"))
        self.connect(preferences, QtCore.SIGNAL('triggered()'), call)
        
        self.edit_menu.addAction(copy_structure)
        self.edit_menu.addAction(paste_structure)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(preferences)
                         
        edit_button = QtGui.QToolButton()
        edit_button.setText('Edit')
        edit_button.setPopupMode(QtGui.QToolButton.InstantPopup)
        edit_button.setMenu(self.edit_menu)
                
        self.addWidget(edit_button)
        
    def set_file_menu(self):
        #self.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.file_menu = QtGui.QMenu(self)
        self.file_menu.setObjectName('file_menu')
        
        self.new_structure_menu = QtGui.QMenu("New Structure")
        self.new_structure_menu.setObjectName('file_menu')
        self.load_structure_menu = QtGui.QMenu("Load Structure")
        self.load_structure_menu.setObjectName('file_menu')
        
        new_single_structure = QtGui.QAction( 'Single Structure', self)
        new_single_structure.setStatusTip('Create Single Structure')
        new_single_structure.setShortcut('Ctrl+n')
        call = lambda : self.emit(QtCore.SIGNAL("new_single_structure()"))
        self.connect(new_single_structure, QtCore.SIGNAL('triggered()'), call)
        
        self.new_structure_menu.addAction(new_single_structure)
        self.file_menu.addMenu(self.new_structure_menu)
        
        new_structure_search = QtGui.QAction( 'Structure Search', self)
        new_structure_search.setStatusTip('Structure Search')
        new_structure_search.setShortcut('Ctrl+Shift+n')
        call = lambda : self.emit(QtCore.SIGNAL("new_structure_search()"))
        self.connect(new_structure_search, QtCore.SIGNAL('triggered()'), call)
        
        self.new_structure_menu.addAction(new_structure_search)

        self.file_menu.addSeparator()
        
        export_structure = QtGui.QAction( 'Export Structure', self)
        export_structure.setShortcut('Ctrl+E')
        export_structure.setStatusTip('Export Current Structure')
        #exportStructure.triggered.connect(self.close)
        call = lambda : self.emit(QtCore.SIGNAL("export_structure()"))
        self.connect(export_structure, QtCore.SIGNAL('triggered()'), call)
        
        self.file_menu.addMenu(self.load_structure_menu)
        
        load_from_file = QtGui.QAction( 'From File', self)
        load_from_file.setStatusTip('Load Structure From File')
        load_from_file.setShortcut('Ctrl+Shift+f')
        call = lambda : self.emit(QtCore.SIGNAL("load_from_file()"))
        self.connect(load_from_file, QtCore.SIGNAL('triggered()'), call)
        
        load_from_local = QtGui.QAction( 'From Local Database', self)
        load_from_local.setStatusTip('Load Structure From Local Database')
        load_from_local.setShortcut('Ctrl+l')
        call = lambda : self.emit(QtCore.SIGNAL("load_from_local()"))
        self.connect(load_from_local, QtCore.SIGNAL('triggered()'), call)
        
        load_from_web = QtGui.QAction( 'From NanoCap Database', self)
        load_from_web.setStatusTip('Load Structure From NanoCap Online Database')
        load_from_web.setShortcut('Ctrl+Shift+l')
        call = lambda : self.emit(QtCore.SIGNAL("load_from_web()"))
        self.connect(load_from_web, QtCore.SIGNAL('triggered()'), call)
        
        self.load_structure_menu.addAction(load_from_file)
        self.load_structure_menu.addAction(load_from_local)
        self.load_structure_menu.addAction(load_from_web)
        
        self.file_menu.addSeparator()
        
        self.file_menu.addAction(export_structure)
        
        quit = QtGui.QAction( 'Quit', self)
        quit.setShortcut('Ctrl+Q')
        quit.setStatusTip('Exit NanoCap')
        call = lambda : self.emit(QtCore.SIGNAL("quit()"))
        self.connect(quit, QtCore.SIGNAL('triggered()'), call)
        
        self.file_menu.addSeparator()
        self.file_menu.addAction(quit)
        
        file_button = QtGui.QToolButton()
        file_button.setText('File')
        #file_button.setPopupMode(QtGui.QToolButton.MenuButtonPopup)
        file_button.setPopupMode(QtGui.QToolButton.InstantPopup)
        file_button.setMenu(self.file_menu)
        
        #self.connect(file_button,QtCore.SIGNAL('clicked()'),self.file_menu.show)
        
        self.addWidget(file_button)
        
        
        
        #self.show()