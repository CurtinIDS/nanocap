
      subroutine dihedral2(i)

      include 'common.f90'

      dimension ff(3),dff(3),dgg(3),rr(3),xk(3)
      dimension rx(3,3),dz(3,3)

      if (zz(i).gt.4.0) return

!  +---------------+
!  |   k           |
!  |    \          |
!  |     i--j      |
!  |         \     |
!  |          m    |
!  +---------------+

      do jj=1,num(i)
      j=near(i,jj)
      if ((zz(j).lt.4.0).and.(dr(i,jj).lt.fhigh)) then

	do kk=1,num(i)
	if ((kk.ne.jj).and.(dr(i,kk).lt.fhigh)) then

	  do mm=1,num(j)
	  if ((near(j,mm).ne.i).and.(dr(j,mm).lt.fhigh)) then

	    finiteforce(jj)=.true.
	    finiteforce(kk)=.true.
	    finiteforce2(jj,mm)=.true.

!+-----------------------------------+
!| setup vectors: 1=ij , 2=ik , 3=jm |
!+-----------------------------------+
	    do ind=1,3
	      rx(1,ind)=dxdr(i,jj,ind)
	      rx(2,ind)=dxdr(i,kk,ind)
	      rx(3,ind)=dxdr(j,mm,ind)
	    end do

	    rr(1)= dr(i,jj)
	    rr(2)= dr(i,kk)
	    rr(3)= dr(j,mm)

	    ff(1)= f(i,jj)
	    ff(2)= f(i,kk)
	    ff(3)= f(j,mm)
	    ff3= ff(1) * ff(2) * ff(3)

	    dff(1)= df(i,jj)
	    dff(2)= df(i,kk)
	    dff(3)= df(j,mm)

	    gg= g3(i)*g3(j)
	    dgg(1)= dzz(i,jj) *(dg3(i)* g3(j) + g3(i)*dg3(j))
	    dgg(2)= dzz(i,kk) * dg3(i)* g3(j)
	    dgg(3)= dzz(j,mm) *  g3(i)*dg3(j)

!+-------------------------------------------------------------+
!| g3(Zi)*g3(Zj) * (ahat . bhat x chat)^2 * f(a) * f(b) * f(c) |
!+-------------------------------------------------------------+
            do k1=1,3                  ! k1 refers to a vector
              k2= mod(k1  ,3) + 1      ! k2=k1+1 (mod 3)
              k3= mod(k1+1,3) + 1      ! k3=k1+2 (mod 3)

              xk(1)= rx(k2,2)*rx(k3,3) - rx(k2,3)*rx(k3,2)
              xk(2)= rx(k2,3)*rx(k3,1) - rx(k2,1)*rx(k3,3)
              xk(3)= rx(k2,1)*rx(k3,2) - rx(k2,2)*rx(k3,1)

              dot= rx(k1,1)*xk(1) + rx(k1,2)*xk(2) + rx(k1,3)*xk(3)

	      dz0= ff(k2)*ff(k3)
	      dz1= dot*dot * dz0 * (dgg(k1)*ff(k1) + gg*dff(k1))
	      dz2= gg * ff3 * 2.0/rr(k1) * dot

	      do ind=1,3
	        dz(k1,ind)= rx(k1,ind)*(dz1 - dot*dz2) + dz2*xk(ind)
	      end do
            end do

	    z(i)=z(i) + 0.5*zdih * gg * dot*dot * ff3
	    do ind=1,3
	      dzdx(jj,ind)=dzdx(jj,ind)         + 0.5*zdih*dz(1,ind)
	      dzdx(kk,ind)=dzdx(kk,ind)         + 0.5*zdih*dz(2,ind)
	      dzdxx(jj,mm,ind)=dzdxx(jj,mm,ind) + 0.5*zdih*dz(3,ind)
            end do

!+-----------------------------------------------------+
!| if neighbour of i: dg3(Zi) * g3(Zj) * dot*dot * ff3 |
!+-----------------------------------------------------+
	    do nni=1,num(i)
	      if ((nni.ne.jj).and.(nni.ne.kk)) then
	      if (dr(i,nni).lt.zhigh) then
	        finiteforce(nni)=.true.
	        fac=0.5*zdih * dg3(i)*dzz(i,nni) * g3(j) * dot*dot * ff3
	        do ind=1,3
	          dzdx(nni,ind)=dzdx(nni,ind) + fac*dxdr(i,nni,ind)
		end do
	      end if
	      end if
	    end do

!+-----------------------------------------------------+
!| if neighbour of j: dg3(Zj) * g3(Zi) * dot*dot * ff3 |
!+-----------------------------------------------------+
	    do nnj=1,num(j)
	      if ((near(j,nnj).ne.i).and.(nnj.ne.mm)) then
	      if ((dr(j,nnj).lt.zhigh)) then
	        finiteforce2(jj,nnj)=.true.
	        fac=0.5*zdih*dg3(j) * dzz(j,nnj) * g3(i) * dot*dot * ff3
		do ind=1,3
		 dzdxx(jj,nnj,ind)=dzdxx(jj,nnj,ind)+fac*dxdr(j,nnj,ind)
		end do
	      end if
	      end if
	    end do

	  end if
	  end do  !--- mm loop
	end if
	end do  !----- kk loop
      end if
      end do  !------- jj loop

      end

