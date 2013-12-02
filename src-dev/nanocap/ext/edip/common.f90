! -*- f90 -*-
      implicit double precision (a-h,o-z)

      double precision mv
      
      parameter (NMAX=10000,NNN=100,NP=INT(NNN*NMAX*0.5))
      parameter (NUMBIN=600,WIDTHBIN=0.01,NGR=2,NVAR=6)
      parameter (NUMBIN2=181,WIDTHBIN2=1.0)
      parameter (MAXCELL1=100,MAXCELL=100,MAXINCELL=50)
!      parameter (MAXCELL=150,MAXINCELL=50)
      parameter (MAXSLAB=1000)
      parameter (MAXCPU=32)
      parameter (pi=3.1415926536)
      parameter (AMASS=12.01*1.66e-27)
      parameter (BOLTZMANN=8.617e-5) 
      parameter (tau1=-6.0*2.5, tau2=6.0)

      character*80 namespecial

      logical finiteforce
      logical finiteforce2

      logical static
      logical special
      logical norings
      logical computeshear
      logical usedihedral2
      logical usedihedral4
      logical newgcutoff
      logical calcstress
      logical steepestdescent
      logical xbspbc
      logical cellneighbour

      logical nolinear
      logical nodihedral
      logical norepulsion

      integer*4 ncpu, icpu
      integer*4 OMP_GET_MAX_THREADS
      integer*4 OMP_GET_THREAD_NUM

      !!! consider 0.025eV/300K !!!
      !parameter (TIMETAU=1e12*1e-10*(AMASS/1.6e-19)**0.5)
      !definition of timetau has moved to constants.f

      common /PARAM1/ aa,bb,beta,sigma,a1,a2
      common /PARAM2/ qq,xlam,xmu,gamma,pilam
      common /PARAM3/ zlow,zhigh,zalpha
      common /PARAM4/ flow,fhigh,falpha
      common /PARAM5/ zdih,zrep,zrep2,c0,bondcutoff

      common /ENTRY/  varlist(0:100,NVAR),npass,nsnap

      common /ELOST/  elosttherm,nrescale
      common /STATE/  u2,u3,udih,pe,tempk,eke,mv,pestart,ekestart,tav
      common /STEPS/  t,h,numstep,istep,nstep,nloop,nprint,itherm
      common /EXTRA/  timetau,tfac,vflag,startt,ntakof,iseed,imsd

      common /SHEAR1/ computeshear
      common /SHEAR2/ shear

      common /FLAGS1/ nolinear,nodihedral,norepulsion,usedihedral2
      common /FLAGS2/ norings,static,special
      common /FLAGS3/ newgcutoff,calcstress,usedihedral4
      common /FLAGS4/ steepestdescent,xbspbc,cellneighbour
      common /FLAGS5/ namespecial

      common /NATOM/  natom
      common /BOXL/   box(3)
      common /ZZZZ/   z(NMAX), zz(NMAX)
      common /ZDERV/  dzdx(NNN,3), dzdxx(NNN,NNN,3)
      common /ZFORC/  finiteforce(NNN), finiteforce2(NNN,NNN)
      common /COORD/  x(NMAX,3), vx(NMAX,3), x0(NMAX,3)
      common /DRXYZ/  dr(NMAX,NNN),dx(NMAX,NNN,3),dxdr(NMAX,NNN,3)
      common /STRES/  totstr(3,3),pressure,biaxial,smin,smax,nstress
      common /BOXVOL/ vol
      common /COMM1/  fx(NMAX,3)

      common /CELLS/  ncell(MAXCELL1,MAXCELL,MAXCELL), numcells(3)
      common /CELLS2/  icell(MAXCELL1,MAXCELL,MAXCELL,MAXINCELL)
      common /PAIRS/  ipair(NP),jpair(NP),inum(NP),jnum(NP),npair
      common /INEAR/  near(NMAX,NNN),num(NMAX),kron(NNN,NNN)

      common /ZCYCL/  f(NMAX,NNN), df(NMAX,NNN), dzz(NMAX,NNN)
      common /GATOM/   g(NMAX),  g2(NMAX),  g3(NMAX)
      common /DGATM/  dg(NMAX), dg2(NMAX), dg3(NMAX)
      common /COM01/  cyclo

      common /GRDAT/ nbin(NGR,NUMBIN),nframe(NGR),igr
      common /ANGLE/ nbin2(NGR,4,NUMBIN2)
      common /FIXED/ ifix
      common /CONDU/ nslab,nswap

      common /EREDC/  u2i(MAXCPU), u3i(MAXCPU), udihi(MAXCPU)
      common /FREDC/  fxx(NMAX,3,MAXCPU)


!$OMP THREADPRIVATE (/ZDERV/,/ZFORC/)
