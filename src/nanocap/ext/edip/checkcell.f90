
      subroutine checkcell(i,ix,iy,iz,jstart)

      include "common.f90"

      ! Wrap-around indices of the cells
      if (ix.eq.0) ix=numcells(1)
      if (iy.eq.0) iy=numcells(2)
      if (iz.eq.0) iz=numcells(3)

      if (ix.gt.numcells(1)) ix=1
      if (iy.gt.numcells(2)) iy=1
      if (iz.gt.numcells(3)) iz=1

      ! Loop over the required atoms in the cell
      do jloop=jstart,ncell(ix,iy,iz)
        j=icell(ix,iy,iz,jloop)

        call checkrij(i,j)
      end do

      end
