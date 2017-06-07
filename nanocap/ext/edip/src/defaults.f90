
      subroutine defaults

      include "common.f90"

!These defaults are according to 
!  a) carbon/edip/param,
!  b) carbon/edip/run4/all4o, and
!  c) carbon/edip/potential

!Two-body potential parameters
      aa=20.0853862863495
      bb=0.827599951322299
      beta=0.0490161172713279
      sigma=1.25714643580808
      a1=1.89225338775144
      a2=0.169794491000172

!Three-body potential parameters
      gamma=1.2406975366223
      xlam=53.7116179513016
      qq=3.5
      xmu=0.25
      pilam=0.0

!Counting the coordination
      zlow=1.46
      zhigh=2.274108
      zalpha=1.544583

      flow=zlow
      fhigh=2.0
      falpha=zalpha

!Pi-bonding parameters
      zdih=0.30
      zrep=0.04
      zrep2=0.04
      c0=3.2

!Coordination cutoff
      bondcutoff=1.80

!Control File defaults
      npass=0

      varlist(0,1)=0.05   ! h
      varlist(0,2)=1000   ! nstep
      varlist(0,3)=300    ! temp
      varlist(0,4)=1      ! therm
      varlist(0,5)=1      ! gr
      varlist(0,6)=1      ! msd

      computeshear=.false.
      shear=0.0

      nolinear=.false.
      nodihedral=.false.
      norepulsion=.false.

      usedihedral2=.false.
      usedihedral4=.false.
      newgcutoff=.false.
      steepestdescent=.false.
      xbspbc=.false.
      cellneighbour=.false.

      cyclo=-1.0

      smin=0.0
      smax=-1.0
      calcstress=.false.

      norings=.false.
      special=.false.
      static=.false.

      ifix=0

      nswap=0
      nslab=10


      !write(*,*) "end edip defaults"
      end
