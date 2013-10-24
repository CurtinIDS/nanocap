
      subroutine distance

      include "common.f90"

      dimension dxx(3)

!+---------------------------+
!| Clear energies and forces |
!+---------------------------+
      u2=0.0
      u3=0.0
      udih=0.0

      do i=1,natom
	do ind=1,3
          fx(i,ind)=0.0d0
	end do
      end do

!+-------------------------------+
!| Calcdistances and components |
!+-------------------------------+
      do loop=1,npair
        i=ipair(loop)
        j=jpair(loop)

	ii=inum(loop)
	jj=jnum(loop)

	do ind=1,3
          delta= x(i,ind) - x(j,ind)
          dxx(ind)=delta - box(ind)*dnint(delta/box(ind))
	end do

!This if-block for non-orthogonal coordinate system
        if (computeshear) then
	  dxx(2)=dxx(2) + shear*dxx(3)
	endif

	drr=0.0
	do ind=1,3
	  drr=drr + dxx(ind)*dxx(ind)
          dx(i,ii,ind)=  dxx(ind)
          dx(j,jj,ind)= -dxx(ind)
	end do
	drr=sqrt(drr)

	dr(i,ii)= drr
	dr(j,jj)= drr

	do ind=1,3
	  dxdr(i,ii,ind)= dx(i,ii,ind)/drr
	  dxdr(j,jj,ind)= dx(j,jj,ind)/drr
        end do
      end do

      end
