      subroutine passcoords(natomin,boxxin,boxyin,boxzin,rdim,r)
    
      include "common.f90"
 
      integer natomin,rdim
      real*8 boxxin,boxyin,boxzin
      real*8 r(rdim)

      natom = natomin
      box(1) = boxxin
      box(2) = boxyin
      box(3) = boxzin

      !print *,"fortran natom",natom,rdim,"box",box(1),box(2),box(3)
      t=0.0
      istep=0
      do i=1,natom
        do ind=1,3
          x(i,ind)=r((i-1)*3 + ind)
          vx(i,ind)=0.0
          x0(i,ind)=x(i,ind)
          !print *, "fortran position ",x(i,ind)
        end do
      end do
      
!+-----------------+
!| Kronecker Delta |
!+-----------------+
      do i=1,NNN
        do j=1,NNN
          if (i.ne.j) kron(i,j)=0.0
          if (i.eq.j) kron(i,j)=1.0
        end do
      end do

      end subroutine passcoords
