
      subroutine runspecial

      include "common.f90"

      parameter (zero=0.0d0)

      write(6,50) namespecial(1:20)
 50   format(/,'Special Run: ',a20)

      if (namespecial(1:3).eq.'gra') goto 100
      if (namespecial(1:3).eq.'lin') goto 100
      if (namespecial(1:3).eq.'tmm') goto 200
      if (namespecial(1:3).eq.'ben') goto 200
      if (namespecial(1:3).eq.'two') goto 300
      stop 'Bad Argument of special'

!+-----------------------------------------------------------+
!| Graphite/diamond and graphite/linear activiation barriers |
!+-----------------------------------------------------------+
 100  if (namespecial(1:3).eq.'gra') then
	rmin=1.54
	bmin=1.42
	theta0=109.5
      else
	rmin=1.42
	bmin=1.32
	theta0=120.0
      endif
      b0=rmin

      do r=rmin,3.20,0.025
        call minimize(r,b0,theta0,bmin,tmin,zmin)
        write(6,110) r,b0,theta0,pe/natom,zmin
 110    format(3f10.3,2f15.9)

        call makespecial(r,b0,theta0)
        call writexbs
        numstep=numstep+1
      end do
      return

!+---------------------------------------------+
!| Bensan's TMM and benzene out-of-plane bends |
!+---------------------------------------------+
 200  do theta=0,15,1
        call makespecial(zero,zero,theta)
 	call energy

	if (numstep.eq.0) pemin=pe
 	write(6,*) theta,pe-pemin
 	call writexbs
	numstep=numstep+1
      end do
      return

!+---------------------------+
!| Bending of a linear chain |
!+---------------------------+
 300  do theta=0,120,5
        call makespecial(zero,zero,theta)
 	call energy

	if (numstep.eq.0) pemin=pe
 	write(6,*) theta,pe-pemin,z(2)
 	call writexbs
	numstep=numstep+1
      end do
      end

!****************************************************

      subroutine minimize(r,b0,theta0,bmin,tmin,zmin)

      include "common.f90"

      pemin=999

      b1=b0
      b2=max(b0-0.025,bmin)

      theta1=theta0
      theta2=max(theta0-3.0,90.0d0)

      do b=b1,b2,-0.005
        do theta=theta1,theta2,-0.5
	  call makespecial(r,b,theta)
	  call energy

	  if (pe.lt.pemin) then
	    pemin=pe
	    zmin=z(1)
	    b0=b
	    theta0=theta
	  end if
        end do
      end do

      pe=pemin
      end
