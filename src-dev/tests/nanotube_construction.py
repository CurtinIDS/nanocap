'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Apr 22, 2014
Copyright Marc Robinson  2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

test construction of a nanotube from
chirality and length.

Show in VTK window


-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
'''

import unittest,sys,os
if __name__ == "__main__":sys.path.append(os.path.abspath(__file__+"/../"))
print sys.path
from nanocap.core.util import *
from nanocap.core.globals import *
import nanocap.core.globals as globals
import nanocap.structures.nanotube as nanotube
import nanocap.core.points as points
from nanocap.gui.settings import *
from nanocap.rendering import pointset,renderwidgets
from nanocap.gui.renderwindow import vtkqtframe

from nanocap.clib import clib_interface
clib = clib_interface.clib

class CheckNanotube(unittest.TestCase): 
    def test_construct_nanotube(self):
        
        n=6
        m=4
        l=5.0
        u=1
        p=True
        
        myNanotube = nanotube.Nanotube()
       # myNanotube.construct_2D_lattices(n,m,l)
        myNanotube.construct_nanotube(n,m,length=l,units=u,periodic=p)

        
        print myNanotube
        
        app = QtGui.QApplication(sys.argv)
        mw = QtGui.QMainWindow()
        vtk = vtkqtframe.VtkQtFrame(0) 
        
        pointActors = pointset.PointSet(0.1,
                                        (1,0,0))
        pointActors.initArrays(myNanotube.points2D)
        pointActors.addToRenderer(vtk.VTKRenderer)
        
        printl("myNanotube.points2D",myNanotube.points2D.npoints)
        
#         carbon_latticeActors = pointset.PointSet(0.1,
#                                         (1,0,0))
#         carbon_latticeActors.initArrays(myNanotube.carbon_lattice2D)
#         carbon_latticeActors.addToRenderer(vtk.VTKRenderer)
#         
#         dual_latticeActors2D = pointset.PointSet(0.2,
#                                         (1,0,0))
#         dual_latticeActors2D.initArrays(myNanotube.dual_lattice2D)
#         dual_latticeActors2D.addToRenderer(vtk.VTKRenderer)
#         
#         i_latticeActors2D = pointset.PointSet(0.1,
#                                         (1,1,0))
#         i_latticeActors2D.initArrays(myNanotube.i_lattice2D)
#         
#         i_latticeActors2D.addToRenderer(vtk.VTKRenderer)
#         
#         
#         pointActors_r = pointset.PointSet(0.1,
#                                         (0,0,1))
#         pointActors_r.initArrays(myNanotube.points2D_r)
#         #pointActors_r.addToRenderer(vtk.VTKRenderer)
#       
#         carbon_latticeActors_r = pointset.PointSet(0.1,
#                                         (0,0,1))
#         carbon_latticeActors_r.initArrays(myNanotube.carbon_lattice2D_r)
#         #carbon_latticeActors_r.addToRenderer(vtk.VTKRenderer)
#       
#         dual_latticeActors_r = pointset.PointSet(0.2,
#                                         (0,0,1))
#         dual_latticeActors_r.initArrays(myNanotube.dual_lattice2D_r)
#         #dual_latticeActors_r.addToRenderer(vtk.VTKRenderer)
#         
#         midpoint2DActor = pointset.PointSet(0.1,
#                                         (0,1,1))
#             
#         midpoint2DActor.initArrays(myNanotube.midpoint2D)
#         
#         midpoint2DActor.addToRenderer(vtk.VTKRenderer)
#         
#         dual_latticeActors = pointset.PointSet(0.05,
#                                         (1,0,0))
#         dual_latticeActors.initArrays(myNanotube.dual_lattice)
#         dual_latticeActors.addToRenderer(vtk.VTKRenderer)
#         #dual_latticeActors.addLabels(vtk.VTKRenderer)
#         
#         dual_latticeActors_r = pointset.PointSet(0.05,
#                                         (0,0,1))
#         dual_latticeActors_r.initArrays(myNanotube.dual_lattice_r)
#         dual_latticeActors_r.addToRenderer(vtk.VTKRenderer)
#         
#         carbon_latticeActors = pointset.PointSet(0.03,
#                                         (0.5,0.,0.5))
#         carbon_latticeActors.initArrays(myNanotube.carbon_lattice)
#         carbon_latticeActors.addToRenderer(vtk.VTKRenderer)
        
        #dual_latticeActors_r.addLabels(vtk.VTKRenderer)
#         
#         midpoint3DActor = pointset.PointSet(0.1,
#                                         (0,1,1))
#         midpoint3DActor.initArrays(myNanotube.midpoint3D)
#         midpoint3DActor.addToRenderer(vtk.VTKRenderer)
        
#         Ch = renderwidgets.LineActor([0,0,0],
#                                      [myNanotube.Ch[0],myNanotube.Ch[1],0],
#                                      (1,0,0))
#         
#         T = renderwidgets.LineActor([0,0,0],
#                                      [myNanotube.T[0]*myNanotube.current_length,myNanotube.T[1]*myNanotube.current_length,0],
#                                      (0,1,0))
#         
        Ch = renderwidgets.LineActor([0,0,0],
                                     [magnitude(myNanotube.Ch),0,0],
                                     (1,0,0))
        
        T = renderwidgets.LineActor([0,0,0],
                                     [0,myNanotube.current_length,0],
                                     (0,1,0))
        
#         M = renderwidgets.LineActor([0,0,myNanotube.midpoint3D.pos[2]],
#                                      myNanotube.midpoint3D.pos,
#                                      (0,0,1))
        #vtk.VTKRenderer.AddActor(M)
        vtk.VTKRenderer.AddActor(Ch)
        vtk.VTKRenderer.AddActor(T)
        vtk.refreshWindow()
        vtk.centerCameraOnPointSet(myNanotube.points2D)
        
        
        
        
        
        mw.setCentralWidget(vtk)
        mw.show()
        sys.exit(app.exec_())
    
if __name__ == "__main__":
    unittest.main() 