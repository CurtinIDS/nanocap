
      subroutine neighbour

      include "common.f90"

      parameter (rskin=0.10)
      dimension xold(nmax,3), widthcell(3), ipos(3)
      save      xold

!+--------------------------------------------+
!|  Check to see if list needs recalculation  |
!+--------------------------------------------+
      if ((numstep.ne.0).and.(.not.special)) then
        rmovemax=0.0
        do i=1,natom
          rmove=0.0
          do ind=1,3
            rmove=rmove + (x(i,ind)-xold(i,ind))**2
          end do
          rmovemax=max(rmovemax,rmove)
        end do

        if (dsqrt(rmovemax).lt.rskin) return
      end if

!+------------------------+
!|  Clear existing lists  |
!+------------------------+
      rcut=c0+2.0*rskin
      if (special) rcut=c0

      npair=0
      do i=1,natom
        num(i)=0
      end do

      if (cellneighbour) then
!+-------------------------------------------------+
!|  O(N) loop to create the list of indexed pairs  |
!+-------------------------------------------------+
        ! Identify the number of cells for each dimension
        do ind=1,3
          numcells(ind)=int(box(ind)/(rcut+0.1))
          widthcell(ind)=box(ind)/real(numcells(ind))

          if (numcells(1).gt.MAXCELL1) stop 'Increase MAXCELL1'
          if (numcells(2).gt.MAXCELL) stop 'Increase MAXCELL'
          if (numcells(3).gt.MAXCELL) stop 'Increase MAXCELL'
        end do

        ! Clear array containing number of atoms in each cell
        do ix=1,numcells(1)
          do iy=1,numcells(2)
            do iz=1,numcells(3)
              ncell(ix,iy,iz)=0
            end do
          end do
        end do

        ! Populate atoms into the cells (map coordinate into [0,box) first)
        do i=1,natom
          do ind=1,3
            xx= x(i,ind)-box(ind)*dnint(x(i,ind)/box(ind))+0.5*box(ind)
            ipos(ind)=int(xx/widthcell(ind))+1
            if (ipos(ind).gt.numcells(ind)) ipos(ind)=numcells(ind)
          end do

          numincell= ncell(ipos(1),ipos(2),ipos(3)) + 1
          if (numincell.gt.MAXINCELL) stop 'Increase MAXINCELL'

          ncell(ipos(1),ipos(2),ipos(3))= numincell
          icell(ipos(1),ipos(2),ipos(3),numincell) = i
        end do

        ! Loop over cells
        do ix=1,numcells(1)
          do iy=1,numcells(2)
            do iz=1,numcells(3)
              ! Loop over atoms in the cell
              do iloop=1,ncell(ix,iy,iz)
                i=icell(ix,iy,iz,iloop)

                call checkcell(i,ix,iy,iz,iloop+1) ! other atoms in the same cell

                ! This group of three have no unique inverses
                call checkcell(i,ix+1,iy,iz,1)     ! (1,0,0)
                call checkcell(i,ix,iy+1,iz,1)     ! (0,1,0)
                call checkcell(i,ix,iy,iz+1,1)     ! (0,0,1)

                ! This group of three have a single unique inverse each
                call checkcell(i,ix+1,iy+1,iz,1)   ! (1,1,0)
                call checkcell(i,ix+1,iy,iz+1,1)   ! (1,0,1)
                call checkcell(i,ix,iy+1,iz+1,1)   ! (0,1,1)

                call checkcell(i,ix-1,iy+1,iz,1)   ! (-1,1,0)
                call checkcell(i,ix+1,iy,iz-1,1)   ! (1,0,-1)
                call checkcell(i,ix,iy-1,iz+1,1)   ! (0,-1,1)

                ! This direction has three unique inverses
                call checkcell(i,ix+1,iy+1,iz+1,1)   ! (1,1,1)

                call checkcell(i,ix-1,iy+1,iz+1,1)   ! (-1,1,1)
                call checkcell(i,ix+1,iy-1,iz+1,1)   ! (1,-1,1)
                call checkcell(i,ix+1,iy+1,iz-1,1)   ! (1,1,-1)
              end do
            end do
          end do
        end do

!+---------------------------------------------------+
!|  O(N^2) loop to create the list of indexed pairs  |
!+---------------------------------------------------+
      else
        do i=1,natom-1
          do j=i+1,natom
            call checkrij(i,j)
          end do
        end do
      end if

!+-----------------------+
!| Check no NNN overflow |
!+-----------------------+
      numflag=0
      do i=1,natom
        if (num(i).gt.NNN) then
          numflag=1
          write(6,*) 'atom',i,' num(i)=',num(i)
        end if
      end do
      if (numflag.eq.1) stop 'Increase NNN'


!+----------------------------+
!|  Save current coordinates  |
!+----------------------------+
      do i=1,natom
        do ind=1,3
          xold(i,ind)=x(i,ind)
        end do
      end do

      end

