
      subroutine printfinish

      include "common.f90"
      ncpu=1
!$    ncpu=OMP_GET_MAX_THREADS()

      call properties
      etot=eke + pe + elosttherm
      etotstart=ekestart + pestart
      write(6,90) ncpu
      write(6,100) etotstart,pestart
      write(6,110) etot,pe
 90   format(  4X,'This job was run on ',I3,' CPUs')
 100  format(/,4X,'Etot/PE before = ',F14.3,3X,F14.3,' eV')
 110  format(  4X,'Etot/PE after  = ',F14.3,3X,F14.3,' eV')

      end
