      subroutine volume

      include "common.f90"

      if (smin.gt.smax) then
        vol=box(1)*box(2)*box(3)
      else
        vol=box(1)*box(2)*(smax-smin)
      end if

      end
