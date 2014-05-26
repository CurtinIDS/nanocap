
      subroutine writestress

      include "common.f90"

      if (.not.calcstress) return
!    call stress(0)
      fac= 160.219 / vol / nstress

      write(6,*) 
      write(6,*) 'Volume [Ang^3]=',vol
      write(6,*) 'nstress=',nstress
      write(6,*)
      write(6,*) 'Stress Tensor [GPa]'
      write(6,100) 'X',(fac*totstr(1,ind),ind=1,3)
      write(6,100) 'Y',(fac*totstr(2,ind),ind=1,3)
      write(6,100) 'Z',(fac*totstr(3,ind),ind=1,3)

      write(6,*)
      write(6,*) 'Hydrostati!Pressure / Biaxial Stress [GPa]'
      write(6,*) pressure,biaxial

 100  format(4x,1a,3f15.7)

      end
