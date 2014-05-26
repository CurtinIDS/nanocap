
      subroutine edgetherm

      include "common.f90"

      logical edge(NMAX)


!+--------------------------------------+
!| Decide whether to do anything at all |
!+--------------------------------------+
      if (mod(numstep,50).ne.0) return

!+-----------------------------------------+
!| Identify atoms in the thermostat region |
!+-----------------------------------------+
      ntherm=0
      do i=1,natom
        edge(i)=.false.
	do ind=1,3
	  if (x(i,ind).lt.0.0) edge(i)=.true.
	end do
	if (edge(i)) ntherm=ntherm+1
      end do

!+------------------------------------------+
!| Compute temperature in thermostat region |
!+------------------------------------------+
      eke=0.0
      do i=1,natom
        if (edge(i)) then
	  do ind=1,3
	    eke= eke + 0.5*vx(i,ind)**2
	  end do
        end if
      end do
      tempk= tfa!* eke/dfloat(ntherm)
      vfac=dsqrt(startt/tempk)

!+------------------------------------------------+
!| Rescale thermostat atoms to target temperature |
!+------------------------------------------------+
      call properties
      ekeold=eke
      vflag=1.0

      do i=1,natom
	if (edge(i)) then
          do ind=1,3
            vx(i,ind)=vx(i,ind)*vfac
          end do
	end if
      end do

!+-------------------------------------+
!| Find how much energy lost or gained |
!+-------------------------------------+
      call properties
      elosttherm=elosttherm + ekeold - eke
      nrescale=nrescale+1

      end

