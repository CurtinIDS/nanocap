
      subroutine writetheta

      include "common.f90"

      dimension values(NGR,4)

!+-------------------+
!| Decision to print |
!+-------------------+
      if (mod(numstep,nprint).ne.0) return

!+--------------------------------+
!|  Write nbin2 to file theta.out |
!+--------------------------------+
      open(unit=9,file='theta.out',status='unknown')

      do i=1,numbin2
        angle= (i-0.5)*widthbin2
	do j=1,4
	  do k=1,NGR
	    if (nframe(k).eq.0) then
	      values(k,j)=0.0
	    else
	      values(k,j)=nbin2(k,j,i)/dfloat(natom*nframe(k))
	    end if
	  end do
	end do
	write(9,100) angle,((values(k,j),j=1,4),k=1,NGR)
 100    format(F6.2,8F7.4)
      end do

      close(unit=9)
      end

