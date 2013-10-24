
      subroutine distribution

      include "common.f90"

      dimension dxx(3)

!+-----------------------------------+
!| Decision to compute distributions |
!+-----------------------------------+
      if (igr.eq.0)             return
      if (mod(numstep,10).ne.0) return

      nframe(igr)=nframe(igr)+1

!+--------------------------------+
!| Accumulate distance statistics |
!+--------------------------------+

      do i=1,natom-1
        do j=i+1,natom
          do ind=1,3
            delta= x(i,ind) - x(j,ind)
            dxx(ind)=delta - box(ind)*dnint(delta/box(ind))
          end do

          rijsq=0.0
          do ind=1,3
            rijsq=rijsq + dxx(ind)*dxx(ind)
          end do
          rij=sqrt(rijsq)

          ibin=int(rij/widthbin)+1
          if (ibin.le.NUMBIN) nbin(igr,ibin)=nbin(igr,ibin)+1
        end do
      end do

!+-----------------------------+
!| Accumulate angle statistics |
!+-----------------------------+
      do i=1,natom
        nn=0
	do jj=1,num(i)
	  if (dr(i,jj).lt.bondcutoff) nn=nn+1
	end do

	do jj=1,num(i)
	if (dr(i,jj).lt.bondcutoff) then
	  do kk=jj+1,num(i)
	  if (dr(i,kk).lt.bondcutoff) then
	    cosi=0.0
	    do ind=1,3
	      cosi=cosi + dxdr(i,jj,ind)*dxdr(i,kk,ind)
	    end do

	    angle=acos(cosi)*180.0/pi
	    ibin=int(angle/widthbin2)+1
	    nbin2(igr,1,ibin)=nbin2(igr,1,ibin) + 1
	    if (nn.le.4) nbin2(igr,nn,ibin)=nbin2(igr,nn,ibin) + 1
	  end if
	  end do
	end if
	end do
      end do

      end
