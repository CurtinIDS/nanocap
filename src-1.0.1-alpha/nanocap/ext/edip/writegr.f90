
      subroutine writegr

      include "common.f90"

      dimension rho(NGR)

!+-------------------+
!| Decision to print |
!+-------------------+
      if (mod(numstep,nprint).ne.0) return

!+----------------------+
!|  Write g(r) to file  |
!+----------------------+
      open(unit=9,file='gr.out',status='unknown')
      avrho=dfloat(natom)/(box(1)*box(2)*box(3))

      do i=1,numbin
        r= (i-0.5)*widthbin
	fac= dfloat(natom) * 4.0*pi*r*r * widthbin

        do j=1,NGR
          if (nframe(j).eq.0) then
	    rho(j)=0.0
	  else
	    rho(j)=2.0*nbin(j,i)/(fac*dfloat(nframe(j)))
	  end if
	end do

	write(9,100) r,(rho(j)/avrho,j=1,NGR)
 100    format(5f10.4)
      end do

      close(unit=9)
      end

