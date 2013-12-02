
      subroutine printinput

      include "common.f90"

      WRITE(6,100)
      WRITE(6,110) NPASS
      WRITE(6,120) NTAKOF
      WRITE(6,130) NPRINT
      WRITE(6,140) NSNAP

      do i=1,npass
        write(6,150) varlist(i,1)
        write(6,160) (int(varlist(i,j)),j=2,4)
        write(6,170) (int(varlist(i,j)),j=5,6)
      end do

 100  FORMAT(/,'Three dimensional EDIP/Z/pi potential for carbon',/)
 110  FORMAT('NPASS=',I2)
 120  FORMAT('NTAKOF=',I1)
 130  FORMAT('NPRINT=',I3)
 140  FORMAT('NSNAP=',I4)

 150  FORMAT('H=',F7.5)
 160  FORMAT('  NSTEP=',I6,'  STARTT=',I5,'  ITHERM=',I1)
 170  FORMAT('  IGR=',I1,'  IMSD=',I1)

      end

