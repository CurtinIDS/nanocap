import os,sys
files = [ 
#"nanocap/clib",
#"nanocap/ext",
#"nanocap/db",
"nanocap/main.py",
"nanocap/gui/gui.py",
#"nanocap/gui/threadmanager.py",
#"nanocap/gui/bottomdock.py",
"nanocap/gui/progresswidget.py",
"nanocap/gui/singlestructuregenwindow.py",
"nanocap/gui/structuretable.py",
"nanocap/gui/tablebuttondelegate.py",
#"nanocap/gui/forms.py",
"nanocap/gui/structuregenwindow.py",
"nanocap/gui/preferenceswindow.py",
"nanocap/gui/common.py",
"nanocap/gui/minimiserinputoptions.py",
"nanocap/gui/frozencoltablewidget.py",
"nanocap/gui/menubar.py",
"nanocap/gui/helpwindow.py",
"nanocap/gui/structurelist.py",
"nanocap/gui/loadfromfilewindow.py",
"nanocap/gui/aboutwindow.py",
"nanocap/gui/structureinputoptions.py",
"nanocap/gui/dbviewer.py",
"nanocap/gui/listitemdelegate.py",
"nanocap/gui/dock.py",
"nanocap/gui/exportstructurewindow.py",
"nanocap/gui/toolbar.py",
"nanocap/gui/gui.py",
"nanocap/gui/mainwindow.py",
"nanocap/gui/settings.py",
#"nanocap/gui/widgets.py",
"nanocap/gui/structureoptionswindow.py",
#"nanocap/core/calculateschlegel.py",
#"nanocap/core/config.py",
#"nanocap/core/constructdual.py",
#"nanocap/core/forcefield.py",
#"nanocap/core/globals.py",
#"nanocap/core/input.py",
#"nanocap/core/minimasearch.py",
#"nanocap/core/minimisation.py",
#"nanocap/core/output.py",
#"nanocap/core/points.py",
#"nanocap/core/ringcalculator.py",
#"nanocap/core/structuredata.py",
#"nanocap/core/structurelog.py",
#"nanocap/core/triangulation.py",
#"nanocap/core/util.py",
#"nanocap/structures/cap.py",
#"nanocap/structures/nanotube.py",
#"nanocap/structures/structure.py",
#"nanocap/structures/cappednanotube.py",
#"nanocap/structures/fullerene.py"
]






os.system("pyreverse -k "+" ".join(files)+" -p nanocap_gui")

os.system("python ~/Dropbox/Scripts/RemoveDuplicateLines.py classes_nanocap_gui.dot")
