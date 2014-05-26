
      subroutine printav

      include "common.f90"

      nloop=min(nloop,nstep)

      write(6,100) nloop,tav/dfloat(nloop)
      write(6,110) nrescale
      write(6,120) ELOSTtherm

 100  format(/,'Average Temp. over last ',I7,' steps : ',F9.2,' (K)')
 110  format('Number of thermostat rescales: ',I5)
 120  format('Energy removed by thermostat:',1P,E10.2,' eV')

      end

