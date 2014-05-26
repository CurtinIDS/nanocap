
      subroutine readcoords

      include "common.f90"

      if (special)     goto 50
      if (ntakof.eq.0) goto 100
      if (ntakof.eq.1) goto 200
      if (ntakof.eq.2) goto 300
      stop

!+-----------------------------------+
!| Dummy routine when special=.true. |
!+-----------------------------------+
 50   natom=1
      do ind=1,3
         x(1,ind)=0.0
        vx(1,ind)=0.0
        box(ind)=10.0
      end do
      return

!+----------------------------------------------+
!| (ntakof=0) Starting from atom positions only |
!+----------------------------------------------+
 100  open(unit=7,file='START',status='old')
      read(7,*) natom
      read(7,*) box(1),box(2),box(3)
      read(7,*) (x(i,1),x(i,2),x(i,3),i=1,natom)

      write(6,110) natom
      write(6,120)
      write(6,130)

 110  format(/,'Read in ',I8,' atoms.')
 120  format('Starting new simulation.')
 130  format('All velocities set to zero.  MSD set to zero.')

      t=0.0
      istep=0
      do i=1,natom
        do ind=1,3
          vx(i,ind)=0.0
          x0(i,ind)=x(i,ind)
        end do
      end do

      close(unit=7)
      return


!+---------------------------------------------------------------+
!| (ntakof=1) Continue on from existing phase point, restart MSD |
!+---------------------------------------------------------------+
 200  open(unit=7,file='START',status='old')
      read(7,210) t,istep,natom
      read(7,220) box(1),box(2),box(3)
      read(7,220) ( x(i,1), x(i,2), x(i,3),i=1,natom)
      read(7,220) (vx(i,1),vx(i,2),vx(i,3),i=1,natom)

      write(6,230) natom
      write(6,240) istep
      write(6,250) 

 210  format(d23.11,2x,i10,2x,i8)
 220  format(3d23.11)
 230  format(/,'Read in ',I8,' atoms.')
 240  format('Restart from step ',I8)
 250  format('Using previous velocities.  MSD set to zero.')

      do i=1,natom
	do ind=1,3
          x0(i,ind)=x(i,ind)
	end do
      end do

      close(unit=7)
      return


!+---------------------------------------------------------------+
!| (ntakof=2) Continue on from existing phase point and MSD data |
!+---------------------------------------------------------------+
 300  open(unit=7,file='START',status='old')
      read(7,310) t,istep,natom
      read(7,320) box(1),box(2),box(3)
      read(7,320) ( x(i,1), x(i,2), x(i,3),i=1,natom)
      read(7,320) (vx(i,1),vx(i,2),vx(i,3),i=1,natom)
      read(7,320) (x0(i,1),x0(i,2),x0(i,3),i=1,natom)

      write(6,330) natom
      write(6,340) istep
      write(6,350)

 310  format(d23.11,2x,i10,2x,i8)
 320  format(3d23.11)
 330  format(/,'Read in ',I8,' atoms.')
 340  format('Restart from step ',I8)
 350  format('Using previous velocities and MSD values')

      close(unit=7)
      end

