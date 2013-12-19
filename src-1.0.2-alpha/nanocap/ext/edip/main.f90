
      program carbon_edip

      include "common.f90"

      call printtime(1)

!+-------------------+
!| Read control file |
!+-------------------+
      call defaults
      call readinput
      call checkinput
!disable stress calcs in parallelized version (not correctly coded)
      calcstress = .false.   
      call printinput

!+-----------------------------------+
!| Read coordinate file & initialise |
!+-----------------------------------+
      call constants
      call readcoords
      call init
      call density

      !if (special) call runspecial

!+-----------+
!| Main loop |
!+-----------+
      do ipass=1,npass
        h=varlist(ipass,1)
        nstep=varlist(ipass,2)
        startt=varlist(ipass,3)
        itherm=varlist(ipass,4)
	igr=varlist(ipass,5)
	imsd=varlist(ipass,6)

        tav=0.0
        vflag=1.0
        nrescale=0

        do nloop=1,nstep
          call verlet
	  call distribution
          call therm
          call conductivity
          call neighbour

          call writexbs
          call printstatus
          call writetheta
          call writegr
        end do

        call printav
	call resetmsd
      end do

!+-------------+
!| Cleaning up |
!+-------------+
      call writestress
      call writecoords
      call printrings
      call printfinish
      call printtime(2)

      end
 
