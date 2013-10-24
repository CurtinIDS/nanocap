
      SUBROUTINE CONSTANTS

      INCLUDE "common.f90"

      timetau=1e12*1e-10*sqrt(AMASS/1.6e-19)

      WRITE(6,100)
      WRITE(6,110) 
      WRITE(6,120) 
      WRITE(6,130) AMASS
      WRITE(6,140) timetau*1000

 100  FORMAT(/,'Reduced Units:')
 110  FORMAT(' ENERGY: 1 eV')
 120  FORMAT(' LENGTH: 1 Angstrom')
 130  FORMAT(' MASS: ',1p,E9.3,' kg')
 140  FORMAT(' TIME: ',F6.2,' fs')

      END

