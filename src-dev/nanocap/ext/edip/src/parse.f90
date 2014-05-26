
      subroutine parse(line,value,error)

      include "common.f90"

      character(len=*) line, value
      logical error

      !print *, "fortran parse ",line,value,error
      error=.false.
      !print *,"call parse ", line,value,error,index(line,'bondcutoff=')
!+-----------------------------------+
!| Parameters for EDIP two-body term |
!+-----------------------------------+
      if (index(line,'aa=').eq.1) then 
        read(value,*,err=100) aa
      elseif (index(line,'bb=').eq.1) then 
        read(value,*,err=100) bb
      elseif (index(line,'beta=').eq.1) then 
        read(value,*,err=100) beta
      elseif (index(line,'sigma=').eq.1) then 
        read(value,*,err=100) sigma
      elseif (index(line,'a1=').eq.1) then 
        read(value,*,err=100) a1
      elseif (index(line,'a2=').eq.1) then 
        read(value,*,err=100) a2
    
!
!      elseif (index(line,'NMAX=').eq.1) then
!        read(value,*,err=100) NMAX
!      elseif (index(line,'NNN=').eq.1) then
!        read(value,*,err=100) NNN
!      elseif (index(line,'MAXCELL=').eq.1) then
!        read(value,*,err=100) MAXCELL
!      elseif (index(line,'MAXINCELL=').eq.1) then
!        read(value,*,err=100) MAXINCELL
!      elseif (index(line,'MAXCELL1=').eq.1) then
!        read(value,*,err=100) MAXCELL1
!+-------------------------------------+
!| Parameters for EDIP three-body term |
!+-------------------------------------+
      elseif (index(line,'gamma=').eq.1) then 
        write(*,*) "read gamma", gamma
        read(value,*,err=100) gamma
      elseif (index(line,'qq=').eq.1) then 
        read(value,*,err=100) qq
      elseif (index(line,'xlam=').eq.1) then 
        read(value,*,err=100) xlam
!    elseif (index(line,'pilam=').eq.1) then 
!      read(value,*,err=100) pilam
      elseif (index(line,'xmu=').eq.1) then 
        read(value,*,err=100) xmu

!+-----------------------------------------+
!| Parameters for generalised coordination |
!+-----------------------------------------+
      elseif (index(line,'zrep=').eq.1) then 
        read(value,*,err=100) zrep
      elseif (index(line,'zrep2=').eq.1) then 
        read(value,*,err=100) zrep2
      elseif (index(line,'zdih=').eq.1) then 
        read(value,*,err=100) zdih
      elseif (index(line,'c0=').eq.1) then 
        read(value,*,err=100) c0

!+------------------------------------------------+
!| Parameters for cutoff functions f(r) and zz(r) |
!+------------------------------------------------+
      elseif (index(line,'zlow=').eq.1) then 
        read(value,*,err=100) zlow
      elseif (index(line,'zhigh=').eq.1) then 
        read(value,*,err=100) zhigh
      elseif (index(line,'zalpha=').eq.1) then 
        read(value,*,err=100) zalpha

      elseif (index(line,'flow=').eq.1) then 
        read(value,*,err=100) flow
      elseif (index(line,'fhigh=').eq.1) then 
        read(value,*,err=100) fhigh
      elseif (index(line,'falpha=').eq.1) then 
        read(value,*,err=100) falpha

      elseif (index(line,'bondcutoff=').eq.1) then 
        read(value,*,err=100) bondcutoff
      
!+-----------------------------------------------------+
!| These control values are stored in single variables |
!+-----------------------------------------------------+
      elseif (index(line,'ntakof=').eq.1) then
        read(value,*,err=100) ntakof
      elseif (index(line,'nprint=').eq.1) then 
        read(value,*,err=100) nprint
      elseif (index(line,'nsnap=').eq.1) then 
        read(value,*,err=100) nsnap

      elseif (index(line,'computeshear').eq.1) then 
        computeshear=.true.
      elseif (index(line,'shear=').eq.1) then 
        read(value,*,err=100) shear

      elseif (index(line,'nolinear').eq.1) then 
        nolinear=.true.
      elseif (index(line,'nodihedral').eq.1) then 
        nodihedral=.true.
      elseif (index(line,'norepulsion').eq.1) then 
        norepulsion=.true.

      elseif (index(line,'calcstress').eq.1) then 
        calcstress=.true.
      elseif (index(line,'smin=').eq.1) then 
        read(value,*,err=100) smin
      elseif (index(line,'smax=').eq.1) then 
        read(value,*,err=100) smax

      elseif (index(line,'cyclo=').eq.1) then 
        read(value,*,err=100) cyclo

      elseif (index(line,'nslab=').eq.1) then 
        read(value,*,err=100) nslab
      elseif (index(line,'nswap=').eq.1) then 
        read(value,*,err=100) nswap

      elseif (index(line,'ifix=').eq.1) then 
        read(value,*,err=100) ifix

      elseif (index(line,'newgcutoff').eq.1) then 
        newgcutoff=.true.
      elseif (index(line,'usedihedral2').eq.1) then 
        usedihedral2=.true.
      elseif (index(line,'usedihedral4').eq.1) then 
        usedihedral4=.true.
      elseif (index(line,'norings').eq.1) then 
        norings=.true.
      elseif (index(line,'static').eq.1) then 
        static=.true.
      elseif (index(line,'steepestdescent').eq.1) then 
        steepestdescent=.true.
      elseif (index(line,'xbspbc').eq.1) then 
        xbspbc=.true.
      elseif (index(line,'cellneighbour').eq.1) then 
        cellneighbour=.true.

      elseif (index(line,'special=').eq.1) then 
        special=.true.
	namespecial=value

!+---------------------------------------------+
!| The token `run' indexes the array variables |
!+---------------------------------------------+
      elseif (index(line,'run').eq.1) then 
        npass=npass+1
	do i=1,NVAR
	  varlist(npass,i)=varlist(npass-1,i)
	end do

!+---------------------------------------------+
!| These control values are stored in an array |
!+---------------------------------------------+
      elseif (index(line,'h=').eq.1) then 
        read(value,*,err=100) varlist(npass,1)
      elseif (index(line,'nstep=').eq.1) then 
        read(value,*,err=100) varlist(npass,2)
      elseif (index(line,'temp=').eq.1) then 
        read(value,*,err=100) varlist(npass,3)
      elseif (index(line,'therm=').eq.1) then 
        read(value,*,err=100) varlist(npass,4)
      elseif (index(line,'gr=').eq.1) then 
        read(value,*,err=100) varlist(npass,5)
      elseif (index(line,'msd=').eq.1) then 
        read(value,*,err=100) varlist(npass,6)

!+------------------------------+
!| If no match we have an error |
!+------------------------------+
      elseif (line(1:1).ne.';') then
        error=.true.
      end if
      return

 100  error=.true.
      end
