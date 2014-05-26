
      subroutine writexbs

      include "common.f90"

      dimension xx(NMAX,3)

!+------------------------------------------------+
!| Decide to print in.bs, in.mv or nothing at all |
!+------------------------------------------------+
      if (nsnap.ne.0) then
        do i=1,natom
          do ind=1,3
            if (xbspbc) then
	      xx(i,ind)=x(i,ind)-box(ind)*nint(x(i,ind)/box(ind))
	    else
	      xx(i,ind)=x(i,ind)
	    end if
	  end do
        end do

        if (numstep.eq.0)                 goto 100
	if (mod(numstep,abs(nsnap)).eq.0) goto 110
      end if
      return

!+-----------------+
!| Write out in.bs |
!+-----------------+
 100  call system("/bin/rm -f in.mv")
      open(unit=8,file='in.bs',status='unknown')
       write(8,120) ((xx(i,ind),ind=1,3),i=1,natom)
       write(8,*) 'spe! C 0.2 red'
       write(8,*) 'bonds C C 0 ',bondcutoff,' 0.07 grey'
       write(8,*) 'in!3'
       write(8,*) '* box=',(real(box(ind)),ind=1,3)
       write(8,*) 'tmat 1 0 0 0 0 1 0 1 0'
      close(unit=8)

      return

!+-----------------+
!| Write out in.mv |
!+-----------------+
 110  if (nsnap.lt.0) call system("/bin/rm -f in.mv")
      open(unit=8,file='in.mv',status='unknown',access='append')
       write(8,130) numstep,t*timetau,tempk
       write(8,140) ((xx(i,ind),ind=1,3),i=1,natom)
      close(unit=8)

 120  format('atom C ',3F9.3)
 130  format(/,'frame step=',I6,', time=',f7.3,' ps, temp=',f7.1,' K')
 140  format(3F9.3)

      end
