
      subroutine linear(i)

      include 'common.f90'

      dimension ff(2),rr(2),dgg(2),dff(2)
      dimension rx(2,3),dz(2,3)

      if (nolinear)     return
      if (zz(i).gt.3.0) return
      
      do jj=1,num(i)
      j=near(i,jj)
      rij=dr(i,jj)
      if ((zz(j).lt.4.0).and.(rij.gt.flow).and.(rij.lt.c0)) then

        do kk=1,num(i)
        if ((kk.ne.jj).and.(dr(i,kk).lt.fhigh)) then

	  finiteforce(jj)=.true.
	  finiteforce(kk)=.true.

!+----------------------------+
!| setup vectors: 1=ij , 2=ik |
!+----------------------------+
	  do ind=1,3
	    rx(1,ind)=dxdr(i,jj,ind)
	    rx(2,ind)=dxdr(i,kk,ind)
	  end do

	  rr(1)= dr(i,jj)
	  rr(2)= dr(i,kk)
	  cc= rr(1)-c0

	  ff(1)= (1.0-f(i,jj)) * cc*cc
	  ff(2)=      f(i,kk)
	  ff2= ff(1) * ff(2)

	  dff(1)= -df(i,jj)*cc*c!+ (1.0-f(i,jj))*2.0*cc
	  dff(2)=  df(i,kk)

	  gg= g2(i) * g(j)
	  dgg(1)= dzz(i,jj) * (dg2(i)*g(j) + g2(i)*dg(j))
	  dgg(2)= dzz(i,kk) *  dg2(i)*g(j)

!+---------------------------------------------------------------------+
!| g2(Zi) * g(Zj) * [1 - (ahat . chat)^2] * ff(a)*(1-ff(c)) * (c-c0)^2 |
!+---------------------------------------------------------------------+
          do k1=1,2                  ! k1 refers to a vector
            k2= 3-k1                 ! k2=k1+1 (mod 2)

	    dot=0.0
	    do ind=1,3
	      dot=dot + rx(k1,ind)*rx(k2,ind)
	    end do

	    dz1= (1.0-dot*dot) * ff(k2) * (dgg(k1)*ff(k1) + gg*dff(k1))
	    do ind=1,3
	      dz2= -2.0*dot/rr(k1) * (rx(k2,ind) - dot*rx(k1,ind))
	      dz(k1,ind)= rx(k1,ind)*dz1 + dz2*ff2*gg
	    end do
          end do

	  z(i)=z(i) + zrep2 * gg * (1.0-dot*dot) * ff2
          do ind=1,3
	    dzdx(jj,ind)=dzdx(jj,ind) + zrep2*dz(1,ind)
	    dzdx(kk,ind)=dzdx(kk,ind) + zrep2*dz(2,ind)
          end do

!+----------------------------------+
!| neighbours of i: easy derivative |
!+----------------------------------+
	  do nni=1,num(i)
	  if ((nni.ne.jj).and.(nni.ne.kk).and.(dr(i,nni).lt.zhigh)) then
	    finiteforce(nni)=.true.
	    fac= zrep2 * dg2(i)*dzz(i,nni) * g(j) * (1.0-dot*dot) * ff2
	    do ind=1,3
	      dzdx(nni,ind)=dzdx(nni,ind) + fac*dxdr(i,nni,ind)
	    end do
	  end if
	  end do

!+----------------------------------+
!| neighbours of j: easy derivative |
!+----------------------------------+
	  do nnj=1,num(j)
	  if ((near(j,nnj).ne.i).and.(dr(j,nnj).lt.zhigh)) then
	    finiteforce2(jj,nnj)=.true.
	    fac= zrep2 * dg(j)*dzz(j,nnj) * g2(i) * (1.0-dot*dot) * ff2
	    do ind=1,3
	      dzdxx(jj,nnj,ind)=dzdxx(jj,nnj,ind) + fac*dxdr(j,nnj,ind)
	    end do
	  end if
	  end do

        end if
        end do
      end if
      end do

      end

