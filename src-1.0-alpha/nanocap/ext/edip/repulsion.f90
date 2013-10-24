
      subroutine repulsion(i)

      include 'common.f90'

      dimension ff(3),dff(3),dgg(3),rr(3),xk(3)
      dimension rx(3,3),dz(3,3)

      if (norepulsion)  return
      if (zz(i).gt.4.0) return

      do jj=1,num(i)
      j=near(i,jj)
      rij=dr(i,jj)
      if ((zz(j).lt.4.0).and.(rij.gt.flow).and.(rij.lt.c0)) then

        do kk=1,num(i)
        if ((kk.ne.jj).and.(dr(i,kk).lt.fhigh)) then

          do mm=kk+1,num(i)
          if ((mm.ne.jj).and.(dr(i,mm).lt.fhigh)) then

	    finiteforce(jj)=.true.
	    finiteforce(kk)=.true.
	    finiteforce(mm)=.true.

!+-----------------------------------+
!| setup vectors: 1=ij , 2=ik , 3=im |
!+-----------------------------------+
	    do ind=1,3
	      rx(1,ind)=dxdr(i,jj,ind)
	      rx(2,ind)=dxdr(i,kk,ind)
	      rx(3,ind)=dxdr(i,mm,ind)
	    end do

	    rr(1)=dr(i,jj)
	    rr(2)=dr(i,kk)
	    rr(3)=dr(i,mm)

	    cc=rr(1)-c0

!	    !!! next bit of code a hack to test shape of pi-pi repulsion
!	    qz=2.0
! 	    qexp= exp(-qz*cc*cc)
! 	    ffq= 1.0/qz * (1.0 - qexp)
! 	     ff(1)= (1.0-f(i,jj)) * ffq
!          dff(1)= (1.0-f(i,jj)) * 2.0*cc*qexp - df(i,jj)*ffq 

 	    ff(1)= (1.0-f(i,jj))*cc*cc
	    ff(2)=      f(i,kk)
	    ff(3)=      f(i,mm)
	    ff123= ff(1) * ff(2) * ff(3)

 	    dff(1)= -df(i,jj)*cc*c!+ (1.0-f(i,jj))*2.0*cc
	    dff(2)=  df(i,kk)
	    dff(3)=  df(i,mm)

	    gg= g3(i)*g(j)
	    dgg(1)= dzz(i,jj) * (dg3(i)*g(j) + dg(j)*g3(i))
	    dgg(2)= dzz(i,kk) *  dg3(i)*g(j)
	    dgg(3)= dzz(i,mm) *  dg3(i)*g(j)

!+-----------------------------------------------------------------------+
!| g3(Zi)*g(Zj) * (ahat . bhat x chat)^2 * f(a)*f(b)*(1-f(c)) * (c-c0)^2 |
!+-----------------------------------------------------------------------+
            do k1=1,3                  ! k1 refers to a vector
              k2= mod(k1  ,3) + 1      ! k2=k1+1 (mod 3)
              k3= mod(k1+1,3) + 1      ! k3=k1+2 (mod 3)

              xk(1)= rx(k2,2)*rx(k3,3) - rx(k2,3)*rx(k3,2)
              xk(2)= rx(k2,3)*rx(k3,1) - rx(k2,1)*rx(k3,3)
              xk(3)= rx(k2,1)*rx(k3,2) - rx(k2,2)*rx(k3,1)

              dot= rx(k1,1)*xk(1) + rx(k1,2)*xk(2) + rx(k1,3)*xk(3)

	      dz1= dot*dot*ff(k2)*ff(k3)* (dgg(k1)*ff(k1) + gg*dff(k1))
	      dz2= gg * ff123 * 2.0/rr(k1) * dot

	      do ind=1,3
	        dz(k1,ind)= rx(k1,ind)*(dz1 - dot*dz2) + dz2*xk(ind)
	      end do
            end do

	    z(i)=z(i) + zrep * gg * dot*dot * ff123
	    do ind=1,3
	      dzdx(jj,ind)=dzdx(jj,ind) + zrep*dz(1,ind)
	      dzdx(kk,ind)=dzdx(kk,ind) + zrep*dz(2,ind)
	      dzdx(mm,ind)=dzdx(mm,ind) + zrep*dz(3,ind)
            end do

!+----------------------------------+
!| neighbours of i: easy derivative |
!+----------------------------------+
	    do nni=1,num(i)
	      if ((nni.ne.jj).and.(nni.ne.kk).and.(nni.ne.mm)) then
	      if (dr(i,nni).lt.zhigh) then
		finiteforce(nni)=.true.
	        fac= zrep * dg3(i)*dzz(i,nni) * g(j) * dot*dot * ff123
		do ind=1,3
		  dzdx(nni,ind)=dzdx(nni,ind) + fac*dxdr(i,nni,ind)
		end do
	      end if
	      end if
	    end do

!+----------------------------------+
!| neighbours of j: easy derivative |
!+----------------------------------+
	    do nnj=1,num(j)
	      if ((near(j,nnj).ne.i).and.(dr(j,nnj).lt.zhigh)) then
		finiteforce2(jj,nnj)=.true.
	        fac= zrep * dg(j)*dzz(j,nnj) * g3(i) * dot*dot * ff123
		do ind=1,3
		 dzdxx(jj,nnj,ind)=dzdxx(jj,nnj,ind)+fac*dxdr(j,nnj,ind)
		end do
	      end if
	    end do

          end if
          end do
        end if
        end do
      end if
      end do

      end

