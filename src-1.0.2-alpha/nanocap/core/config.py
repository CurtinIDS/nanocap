'''
Created on Aug 1, 2013

@author: Marc Robinson
'''
from nanocap.core.util import *
import getpass,os

class Config(object):
    def __init__(self):
        self.opts = {}
        self.defaults = [("FullereneCarbonAtomRadius" , 0.02),
                    ("FullereneDualLatticePointRadius" , 0.02),
                    ("FullereneDualLatticePointColourRGB" , (1,0,0)),
                    ("FullereneCarbonAtomColourRGB" , (0,0,0)),
                     
                    ("TubeCarbonAtomColourRGB" , (0,0,0)),
                    ("TubeDualLatticePointColourRGB" , (0,1,0)),
                    ("CappedTubeDualLatticePointColourRGB" , (0,1,1)),
                    ("CappedTubeCarbonAtomColourRGB" , (0,0,0)),
                    ("CapDualLatticePointColourRGB" , (1,0,1)),
                     
                    ("FullereneDualLatticeNFixedEquator" , 0),
                    ("FullereneDualLatticeFixPole" , True),
                     
                    ("FullereneCarbonAtomNFixedEquator" , 0),
                    ("FullereneCarbonAtomFixPole" , True),
                     
                    ("FullereneUseRandomSeed" , True),
                    ("NanotubeCapRandomSeed" , 316512311),
                    ("NanotubeCapUseRandomSeed" , True),
                    ("FullereneRandomSeed" , 316512311),
                     
                    ("GenType" , "Fullerene"),
                     
                    ("isNanotube" , 0),
                    ("NanotubeDamping" , False),
                    ("NanotubeDampingCutoff" , 1.0),
                    ("NanotubeDampingConstant" , 10.0),
                     
                    ("EstimateCapPoints" , True),
                    ("RenderLock" , False),
                    ("GUIlock" , False),
                    ("updatingRender" , False),
                     
                    ("Mode" , "Basic"),
                    ("NFullereneDualLatticePoints" , 32),
                    ("NFullereneCarbonAtoms" , 60),
                     
                    ("NCapDualLatticePoints" , 14),
                    ("NTubeDualLatticePoints" , 32),
                    ("NCappedTubeDualLatticePoints" , 32),
                     
                    ("NTubeCarbonAtoms" , 0),
                    ("NCappedTubeCarbonAtoms" , 30),
                    ("NCapCarbonAtoms" , 16),
                     
                    ("TubeDualLatticePointRadius" , 0.02),
                    #"CapDualLatticePointRadius" , 0.02
                    ("CappedTubeDualLatticePointRadius" , 0.02),
                    ("CapDualLatticePointRadius" , 0.02),
                    ("CappedTubeCarbonAtomRadius" , 0.02),
                    ("TubeCarbonAtomRadius" , 0.02),
                    ("CarbonBondThickness" , 0.004),
                    ("NanotubeChiralityN" , 5),
                    ("NanotubeChiralityM" , 5),
                    ("NanotubeChiralityU" , 5),
                     
                     
                     
                    ("MinType" , "LBFGS"),
                    ("MinLoop" , False),
                    ("StopMin" , False),
                    ("NStructures" , 1),
                    ("NMaxStructures" , 50),
                    ("AddGaussians" , False),
                    ("ResetPerIteration" , False),
                    ("RandomPertubationPerIteration" , False),
                    ("BasinClimb" , False),
                    ("MinSteps" , 2),
                    ("MinTol" , 1e-10),
                    ("RenderUpdate" , 1),
                    ("KnownMinimum" , 0),
                    ("GaussianWidth" , 0.5),
                    ("GaussianHeight" , 0.5),
                    ("StopCriteriaIP" , False),
                    ("StopCriteriaPentsOnly" , False),
                     
                     
                    ("CalcTriangulation" , True),
                    ("ShowTriangulation" , True),
                    #"CalcCarbonAtoms" , False
                    #"ShowCarbonAtoms" , False 
                    ("CarbonMinimise" , False ),
                    ("CarbonForceField" , "Scaled Topology" ),
                    ("CalcCarbonBonds" , True ),
                    ("ShowCarbonBonds" , True ),
                    ("CalcCarbonRings" , True ),
                    ("ShowCarbonRings" , True),
                    ("CalcSchlegel" , False),
                    ("ShowScreenInfo" , True ),
                    ("SaveImages" , False),
                     
                    ("SchlegelGamma" , 0.5),
                    ("SchlegelCutoff" , 0.9),
                     
                    ("ShowTubeCarbonAtoms" , True),
                    ("ShowTubeCarbonAtomsLabels" , False),
                    ("ShowTubeDualLatticePoints" , True),
                    ("ShowTubeDualLatticePointsLabels" , False),
                    ("ShowCappedTubeDualLatticePoints" , True),
                    ("ShowCappedTubeDualLatticePointsLabels" , False),
                    ("ShowCapDualLatticePoints" , True),
                    ("ShowCapDualLatticePointsLabels" , False),
                    ("ShowFullereneDualLatticePoints" , True),
                    ("ShowFullereneDualLatticePointsLabels" , False),
                    ("ShowFullereneDualLatticePointsBox" , False),
                    ("ShowFullereneCarbonAtoms" , True),
                    ("ShowFullereneCarbonAtomsLabels" , False),
                    ("ShowFullereneCarbonAtomsBox" , False),
                    ("ShowCappedTubeCarbonAtoms" , True),
                    ("ShowCappedTubeCarbonAtomsLabels" , False),
                    ("CalcFullereneCarbonAtoms" , True),
                    ("CalcCappedTubeCarbonAtoms" , True),
                     
                    ("AutoNanotubeZCutoff" , True),
                    ("NanotubeZCutoff" , 2.0),
                    ("NanotubeLength" , 2.0)]
        self.setDefaults()
        
        #self.setUser()
        #self.setHomeDir()
    
    def setUser(self,uname=None):
        if(uname!=None):self.opts["User"] = uname
        else:self.opts["User"] = getpass.getuser()
        printl("set NanoCap User:",self.opts["User"])
        
    def setHomeDir(self,dir=None):
        if(dir!=None):self.opts["Home"] = dir
        else:self.opts["Home"] = os.path.join(os.path.expanduser("~"),".nanocap")
        printl("set NanoCap Home:",self.opts["Home"])

        if not (os.path.exists(self.opts["Home"])):
            printl("NanoCap Home does not exist, creating...",self.opts["Home"])
            os.mkdir(self.opts["Home"])
            
            
    
    def __str__(self):
        string = "NanoCap Config: \n"
        for key in sorted(self.opts.iterkeys()):
            string+= "%s: %s\n" % (key, self.opts[key])
        return string
    
    def setDefaults(self):
        for key,val in self.defaults:
            self.opts[key] = val
            