
      subroutine checkinput

      include "common.f90"

!+-------------------------------------+
!| Implied settings from logical flags |
!+-------------------------------------+
      if (special)      norings=.true.
      if (special)      npass=-1
      if (special)      nsnap=1

      if (static)       npass=-1
      if (usedihedral2) nodihedral=.true.
      if (usedihedral4) nodihedral=.true.


!+-----------------------------------+
!| Absence of token "run" is allowed |
!+-----------------------------------+
      if (npass.eq.0) then
        npass=1
	do i=1,NVAR
	  varlist(1,i)= varlist(0,i)
	end do
      endif

!+--------------------------------------+
!| Check control variables are sensible |
!+--------------------------------------+
      do i=1,npass
        itherm=int(varlist(i,4))
        igr=int(varlist(i,5))
        imsd=int(varlist(i,6))

	if ((itherm.lt.0).or.(itherm.gt.4)) then
	  stop 'itherm is out of range'
	elseif ((igr.lt.0).or.(igr.gt.NGR)) then
	  stop 'igr is out of range'
	elseif ((imsd.lt.0).or.(imsd.gt.1)) then
	  stop 'imsg is out of range'
	endif
      end do

      if (nslab.gt.MAXSLAB) stop 'Increase MAXSLAB'
      if (mod(nslab,2).ne.0) stop 'nslab must be even'
      if (nswap.ne.0) then
        if (npass.ne.1) stop 'npass must be one for thermal calc'
      end if


      end
