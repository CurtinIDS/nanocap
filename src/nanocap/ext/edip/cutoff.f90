! -*- f90 -*-
      subroutine cutoff

      include "common.f90"

!+-------------------------------------------+
! | Compute spherical part of Z for all atoms |
!+-------------------------------------------+
      do i=1,natom
	zz(i)=0
        if (cyclo.gt.0.0) zz(i)=cyclo

        do jj=1,num(i)
	  rij=dr(i,jj)
	  if (rij.gt.zhigh-0.001) then
	    dzz(i,jj)=0.0

	  elseif (rij.lt.zlow+0.001) then
	    dzz(i,jj)=0.0
	    zz(i)=zz(i)+1.0

	  else
	    frac=(rij-zlow)/(zhigh-zlow)
	    recip= 1.0/(1.0-1.0/frac**3)
	    expz= exp(zalpha*recip)

	    zz(i)=zz(i) + expz
	    dzz(i,jj)= -3.0/frac**4/(zhigh-zlow) * expz*zalpha*recip**2
	  end if
	end do
      end do

!+----------------------------------------------------------------------+
!| Compute f(r) for the Zpi cutoff (only needed if g(Zi) less than 4.0) |
!+----------------------------------------------------------------------+
      do i=1,natom
 	if (zz(i).lt.4.0) then
        do jj=1,num(i)
	  rij=dr(i,jj)
	  if (rij.gt.fhigh-0.001) then
	    f(i,jj)=0.0
	    df(i,jj)=0.0

	  elseif (rij.lt.flow+0.001) then
	    f(i,jj)=1.0
	    df(i,jj)=0.0

	  else
	    frac=(rij-flow)/(fhigh-flow)
	    recip= 1.0/(1.0-1.0/frac**3)
	    expf= exp(falpha*recip)

	    f(i,jj)=  expf
	    df(i,jj)= -3.0/frac**4/(fhigh-flow) * expf*falpha*recip**2
	  end if
	end do
 	end if
      end do

!+--------------------------------------+
!| Compute g3(Zi) for sp2 contributions |
!+--------------------------------------+
      do i=1,natom
	if ((zz(i).lt.2.0).or.(zz(i).gt.4.0)) then
 	   g3(i)=0.0
 	  dg3(i)=0.0

	else
	  arg= zz(i)-3.0
	   g3(i)=         (arg*arg - 1.0)**2
	  dg3(i)= 4.0*arg*(arg*arg - 1.0)
	end if
      end do

!+-------------------------------------+
!| Compute g2(Zi) for sp contributions |
!+-------------------------------------+
      do i=1,natom
	if ((zz(i).lt.1.0).or.(zz(i).gt.3.0)) then
	   g2(i)=0.0
	  dg2(i)=0.0

	else
	  arg= zz(i)-2.0
	   g2(i)=         (arg*arg - 1.0)**2
	  dg2(i)= 4.0*arg*(arg*arg - 1.0)
	end if
      end do

!+---------------------------------------+
!| Compute g(Zi) for any pi-contribution |
!+---------------------------------------+
      do i=1,natom
        if (zz(i).gt.3.0) then
	   g(i)=  g3(i)
	  dg(i)= dg3(i)

	elseif ((zz(i).gt.2.0).or.(.not.newgcutoff)) then
 	   g(i)= 1.0
 	  dg(i)= 0.0

	else
	   g(i)=  g2(i)
	  dg(i)= dg2(i)
	end if
      end do

!     do i=1,natom
!	if (zz(i).lt.3.0) then
!	  g(i)=1.0
!	  dg(i)=0.0
!
!	elseif  (zz(i).gt.4.0) then
!	  g(i)=0.0
!	  dg(i)=0.0
!
!	else
!	  arg= zz(i)-3.0
!	  g(i)=          (arg*arg - 1.0)**2
!	  dg(i)= 4.0*arg*(arg*arg - 1.0)
!	end if
!     end do

      end
