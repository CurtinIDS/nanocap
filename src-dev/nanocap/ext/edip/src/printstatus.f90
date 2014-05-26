
      subroutine printstatus

      include "common.f90"

!+-------------------+
!| Decision to print |
!+-------------------+
      if (mod(numstep,nprint).ne.0) return

      call properties
      etot= eke + pe + elosttherm

      xmsd=0.0
      zav=0.0
      sp1frac=0
      sp2frac=0
      sp3frac=0

      do i=1,natom
	zav=zav + z(i)
	do ind=1,3
          xmsd=xmsd + (x(i,ind) - x0(i,ind))**2
	end do

        ii=0
	do jj=1,num(i)
	  if (dr(i,jj).lt.bondcutoff) ii=ii+1
	end do
	if (ii.eq.2) sp1frac=sp1frac+1
	if (ii.eq.3) sp2frac=sp2frac+1
	if (ii.eq.4) sp3frac=sp3frac+1
      end do
      xmsd=xmsd/dfloat(natom)
      zav=zav/dfloat(natom)
      sp1frac= 100.0*sp1frac/dfloat(natom)
      sp2frac= 100.0*sp2frac/dfloat(natom)
      sp3frac= 100.0*sp3frac/dfloat(natom)

      if (nloop.le.nprint) then
        write(6,200)
        write(6,210)
        write(6,220)
      end if


      write(6,300) numstep,t*timetau
      write(6,310) pe,etot
      write(6,320) tempk
      write(6,330) xmsd
      write(6,340) zav
      write(6,350) sp1frac
      write(6,350) sp2frac
      write(6,350) sp3frac
      write(6,360) mv
!    if (.not.calcstress) pressure=0.0
      write(6,370) pressure

      call flush(6)

 200  format(/)
 210  format('step  time(ps)  PE(eV)   Etot(eV)',/)
 220  format('   Temp(K) MSD(Ang) Zav  %sp %sp2 %sp3  MVtot P(GPa)',/)
!  1P statements make first digit in exponential notation non-zero
 300  format(I8.8,1X,1P,E9.3,/)
 310  format(1X,F14.3,1X,F14.3)
 320  format(1X,F8.2)
 330  format(1X,1P,E9.3)
!340  format($,1X,1P,E9.3)
 340  format(1X,F5.2)
 350  format(1X,F5.1)
 360  format(1X,F8.3)
 370  format(  1X,1P,E10.4)

      end

