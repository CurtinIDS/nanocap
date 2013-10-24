
      subroutine nabor

      include "common.f90"

      parameter (rskin=0.10)
      dimension xold(nmax,3), dxx(3)
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

!+---------------------------------------------------+
!|  O(N^2) loop to create the list of indexed pairs  |
!+---------------------------------------------------+
      do i=1,natom-1
        do j=i+1,natom
	  do ind=1,3
            delta= x(i,ind) - x(j,ind)
            dxx(ind)=delta - box(ind)*dnint(delta/box(ind))
	  end do

!This if-block for non-orthogonal coordinate system
          if (computeshear) then
	    dxx(2)=dxx(2) + shear*dxx(3)
	  endif

	  rijsq=0.0
	  do ind=1,3
	    rijsq=rijsq + dxx(ind)*dxx(ind)
	  end do
	  rij=sqrt(rijsq)

	  !following exceptions for pseudo-hydrogen for C4H8
	  !if ((i.eq.6).and.(j.eq.13)) rij=rcut+1.0
	  !if ((i.eq.7).and.(j.eq.14)) rij=rcut+1.0

          if (rij.lt.rcut) then
            num(i)=num(i)+1
            num(j)=num(j)+1

	    near(i,num(i))=j
	    near(j,num(j))=i

            npair=npair+1
            ipair(npair)=i
            jpair(npair)=j

            inum(npair)=num(i)
            jnum(npair)=num(j)
          end if

        end do
      end do

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

