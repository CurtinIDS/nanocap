
      subroutine properties

      include "common.f90"

!+------------------------------------------------+
!| Calculate the Energy, Momentum and Temperature |
!+------------------------------------------------+
      mv=0.0
      eke=0.0

      do ind=1,3
        vxsum=0.0
        do i=ifix+1,natom
          vxsum=vxsum + vx(i,ind)
          eke=eke + 0.5*vx(i,ind)**2
        end do
        mv=mv + vxsum*vxsum
      end do

      mv=dsqrt(mv)
      tempk=eke/(dfloat(natom-ifix))*tfac

      end
 
