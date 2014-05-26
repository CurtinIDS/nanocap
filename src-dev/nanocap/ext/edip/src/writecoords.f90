 
      subroutine writecoords

      include "common.f90"

      if (special) return

      open(unit=7,file='RESTART',status='unknown')
 
      write(7,110) t,istep,natom
      write(7,120) box(1),box(2),box(3)
      write(7,120) ( x(i,1), x(i,2), x(i,3),i=1,natom)
      write(7,120) (vx(i,1),vx(i,2),vx(i,3),i=1,natom)
      write(7,120) (x0(i,1),x0(i,2),x0(i,3),i=1,natom)
      write(7,130) u2,u3
      write(7,140) pe,eke,pe+eke
      write(7,150) t,istep,tempk

 100  format('SI.',a3,'.',i4.4)
 110  format(d23.11,2x,i10,2x,i8)
 120  format(3d23.11)
 130  format(5x,'U2=',f10.2,5x,'U3=',f9.4)
 140  format(5x,'PE=',f10.2,5x,'KE=',f10.3,5x,'Etot=',f10.2)
 150  format(5x,'t/tau = ',f9.4,' after ',i10,' steps,  T=',f8.2,'(K) ')

      close(unit=7)
      end

