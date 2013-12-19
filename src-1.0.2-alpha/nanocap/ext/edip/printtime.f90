
      subroutine printtime(iflag)

      include "common.f90"

      character*24 date
      integer      tstart,time
      save         tstart

      call fdate(date)

      if (iflag.eq.1) then
        tstart=time()
        write(6,100) date
      else
	if (static) numstep=1
        tdiff= dfloat(time()-tstart)

        write(6,110) date
        write(6,120) tdiff/60
        write(6,130) int(tdiff/dfloat(natom*numstep)*1e6)
        write(6,140) numstep*h*timetau
      end if

 100  format(/,'Simulation begun ',A24)
 110  format(/,'Simulation completed ',A24)
 120  format('  wall-clock time: ',F7.2,' minutes')
 130  format('  performance: ',i6,' microseconds/atom/timestep')
 140  format('  simulation time: ',F7.2,' ps')

      end

