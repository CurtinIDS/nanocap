
      subroutine distnab

      include "common.f90"

      dimension dxx(3)

!+--------------------------+
!| Clear list of neighbours |
!+--------------------------+
      do i=1,natom
        num(i)=0.0
      end do

!+---------------------------------------------+
!|  O(N^2) loop to create the neighbour lists  |
!+---------------------------------------------+
      do i=1,natom-1
      do j=i+1,natom
        do ind=1,3
          delta= x(i,ind) - x(j,ind)
          dxx(ind)=delta - box(ind)*dnint(delta/box(ind))
	end do

!+---------------------------------------------------------+
!| Shear elasti!constant needs non-orthogonal coordinates |
!+---------------------------------------------------------+
        if (computeshear) then
	  dxx(2)=dxx(2) + shear*dxx(3)
	endif

	rijsq=0.0
	do ind=1,3
	  rijsq=rijsq + dxx(ind)*dxx(ind)
	end do
	rij=sqrt(rijsq)

!+-------------------------------------------------+
!| If within cutoff store in num/near indexed list |
!+-------------------------------------------------+
        if (rij.lt.c0) then
          num(i)=num(i)+1
          num(j)=num(j)+1

	  near(i,num(i))=j
	  near(j,num(j))=i

	  dr(i,num(i))= rij
	  dr(j,num(j))= rij

	  do ind=1,3
            dx(i,num(i),ind)=  dxx(ind)
            dx(j,num(j),ind)= -dxx(ind)

	    dxdr(i,num(i),ind)=  dxx(ind)/rij
	    dxdr(j,num(j),ind)= -dxx(ind)/rij
	  end do
        end if
      end do
      end do

      end

