import os,sys
files = [ 
"nanocap/clib",
"nanocap/ext",
#"nanocap/db",
#"nanocap/gui",
"nanocap/core/calculateschlegel.py",
#"nanocap/core/config.py",
"nanocap/core/constructdual.py",
"nanocap/core/forcefield.py",
"nanocap/core/globals.py",
"nanocap/core/input.py",
"nanocap/core/minimasearch.py",
"nanocap/core/minimisation.py",
"nanocap/core/output.py",
"nanocap/core/points.py",
"nanocap/core/ringcalculator.py",
#"nanocap/core/structuredata.py",
"nanocap/core/structurelog.py",
"nanocap/core/triangulation.py",
"nanocap/core/util.py",
"nanocap/structures/cap.py",
"nanocap/structures/nanotube.py",
"nanocap/structures/structure.py",
"nanocap/structures/cappednanotube.py",
"nanocap/structures/fullerene.py"
]






os.system("pyreverse -k "+" ".join(files)+" -p nanocap")

os.system("python ~/Dropbox/Scripts/RemoveDuplicateLines.py classes_nanocap.dot")
