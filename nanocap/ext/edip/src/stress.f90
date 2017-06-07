      subroutine stress(i,jj,fij,ind)

      include "common.f90"
      logical inrange
      if (.not.calcstress) return
      if (numstep.eq.0) return

      if (i.eq.0) then
        nstress=nstress + 1
        do j=1,natom
          if (inrange(x(j,3))) then
            do in1=1,3
            do in2=1,3
              totstr(in1,in2)=totstr(in1,in2) + vx(j,in1)*vx(j,in2)
            end do
            end do
          end if
        end do

          fac= 160.219 / vol / nstress

!        write(6,*) 'end of loop over atoms in stress'

          biaxial=0.0
          pressure=0.0
!        write(6,*)totstr(1,1),totstr(2,2),totstr(3,3),biaxial,pressure
          do in1=1,3
           pressure=pressure + fac*totstr(in1,in1)
           if (in1.eq.2) biaxial=pressure/2.0
          end do
      
          pressure=pressure/3.0
!        write(6,*) pressure,biaxial

      else
        j=near(i,jj)
        zav= 0.5*(x(i,3) + x(j,3))
        if (inrange(zav)) then
          do in2=1,3
            totstr(ind,in2)=totstr(ind,in2) - fij*dx(i,jj,in2)
          end do
        end if

      end if
      end

!=====================================

      function inrange(zval)

      include "common.f90"
      logical inrange

      inrange=.false.
      if (smin.gt.smax)                      inrange=.true.
      if ((zval.gt.smin).and.(zval.lt.smax)) inrange=.true.

      end
