
      subroutine energy

      include "common.f90"
      open(unit=7,file='energies.txt',status='unknown')

!+--------------------------------------+
!| Clear energies and compute distances |
!+--------------------------------------+
      u2=0.0
      u3=0.0
      udih=0.0

      call distnab
      call cutoff

      do i=1,natom
        call coordination(i)
	a12= a1 + a2*z(i)
	tau=1.0 - z(i)/12.0 * (1.0 + tanh(tau1+tau2*z(i)))

!+------------------+
!| Pair Interaction |
!+------------------+
        do jj=1,num(i)
        if (dr(i,jj).lt.a12-0.001) then

          rij=dr(i,jj)
          bond=exp(-beta*z(i)*z(i))
          pair = aa * (bb/rij**4 - bond) * exp(sigma/(rij-a12))
          write(7,*) rij, pair
          u2=u2 + pair

!+--------------------+
!| Triple Interaction |
!+--------------------+
          do kk=jj+1,num(i)
 	  if (dr(i,kk).lt.a12-0.001) then

	    cosi=0.0
	    do ind=1,3
	      cosi=cosi + dxdr(i,jj,ind)*dxdr(i,kk,ind)
	    end do

            arg12= gamma/(dr(i,jj)-a12) + gamma/(dr(i,kk)-a12)
            zexpgam=exp(arg12 - xmu*(z(i)-4.0)*(z(i)-3.0-0.069/xmu))
!          zexpgam=exp(arg12 - xmu*(z(i)-4.0)*(z(i)-3.0))
            theta= xlam/qq * (1.0 - exp(-qq*(cosi+tau)**2))
            triple = zexpgam*theta
            write(7,*)rij, triple/2.0
            write(7,*)dr(i,kk), triple/2.0
            u3=u3 + triple
        
	  end if
          end do   
!  kk
	end if
        end do
! neighbours
      end do
!  atom

      pe= u2 + u3 + udih
      close(unit=7)
      end
   
