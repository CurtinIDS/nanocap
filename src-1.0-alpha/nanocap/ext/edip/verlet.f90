
      subroutine verlet

      include "common.f90"

      dimension xnext(nmax,3),xprev(nmax,3)
      save      xnext

!+---------------------------------------------------+
!|  Increment counters and store previous positions  |
!+---------------------------------------------------+
      t=t+h
      istep=istep+1
      numstep=numstep+1

!+-----------------------------+
!|  Steepest Descent Algorithm |
!+-----------------------------+
      if (steepestdescent) then
        call force
        do i=ifix+1,natom
          do ind=1,3
            x(i,ind)= x(i,ind) + h*fx(i,ind)
            vx(i,ind)= fx(i,ind)
          end do
        end do

        call properties
        return
      end if

      do i=ifix+1,natom
	do ind=1,3
          xprev(i,ind) = x(i,ind)
	end do
      end do

!+----------------------------------+
!|  R(t+h)=R(t)+V(t)*h+F(t)*h**2/2  |
!+----------------------------------+
      if (vflag.gt.0.5) then
        do i=ifix+1,natom
	  do ind=1,3
            xnext(i,ind)=x(i,ind) + vx(i,ind)*h + fx(i,ind)*h*h*0.5
	  end do
        end do
      end if

!+---------------------------------------+
!|  assign R(t) = R(t+h) from last step  |
!+---------------------------------------+
      do i=ifix+1,natom
	do ind=1,3
          x(i,ind)=xnext(i,ind)
	end do
      end do

! +-------------------------------------------------------+
! |  Cal!F(t+h), and thus find R(t+2h) and V(t+h) using  |
! |           R(t+h)=2R(t)-R(t-h)+F(t)*h**2               |
! |           V(t)=(R(t+h)-R(t-h))/2h                     |
! +-------------------------------------------------------+
!    write(*,*)'In Verlet...'
      call force

      do i=ifix+1,natom
	do ind=1,3
          xnext(i,ind)= 2.0*x(i,ind) - xprev(i,ind) + fx(i,ind)*h*h
          vx(i,ind)= (xnext(i,ind) - xprev(i,ind))/(2.0*h)
	end do
      end do

      call stress(0)
      call properties
      tav=tav + tempk

      end

