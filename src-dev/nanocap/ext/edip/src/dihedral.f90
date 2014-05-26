
      subroutine dihedral(i)

      include 'common.f90'

      dimension ff(3),dff(3),dgg(3),rr(3),xk(3)
      dimension rx(3,3),dz(3,3)

      if (usedihedral2) call dihedral2(i)
      if (usedihedral4) call dihedral4(i)
      if (nodihedral)   return
      if (zz(i).gt.4.0) return

!+------------------+
!|      k           |
!|       \          |
!|        i--j      |
!|       /    \     |
!|      m      n    |
!+------------------+

      do jj=1,num(i)
      j=near(i,jj)
      if ((zz(j).lt.4.0).and.(dr(i,jj).lt.fhigh)) then

	do kk=1,num(i)
	if ((kk.ne.jj).and.(dr(i,kk).lt.fhigh)) then

	  do mm=kk+1,num(i)
	  if ((mm.ne.jj).and.(dr(i,mm).lt.fhigh)) then

	    do nn=1,num(j)
	    if ((near(j,nn).ne.i).and.(dr(j,nn).lt.fhigh)) then

	      finiteforce(jj)=.true.
	      finiteforce(kk)=.true.
	      finiteforce(mm)=.true.
	      finiteforce2(jj,nn)=.true.

!+-----------------------------------+
!| setup vectors: 1=ik , 2=im , 3=jn |
!+-----------------------------------+
	      do ind=1,3
	        rx(1,ind)=dxdr(i,kk,ind)
	        rx(2,ind)=dxdr(i,mm,ind)
	        rx(3,ind)=dxdr(j,nn,ind)
	      end do

	      rr(1)= dr(i,kk)
	      rr(2)= dr(i,mm)
	      rr(3)= dr(j,nn)

	      ff(1)= f(i,kk)
	      ff(2)= f(i,mm)
	      ff(3)= f(j,nn)
	      ff4= ff(1) * ff(2) * ff(3) * f(i,jj)

	      dff(1)= df(i,kk)
	      dff(2)= df(i,mm)
	      dff(3)= df(j,nn)

	      gg= g3(i)*g3(j)
	      dgg(1)= dzz(i,kk) * dg3(i)* g3(j)
	      dgg(2)= dzz(i,mm) * dg3(i)* g3(j)
	      dgg(3)= dzz(j,nn) *  g3(i)*dg3(j)

!+--------------------------------------------------------------------+
!| g3(Zi)*g3(Zj) * (ahat . bhat x chat)^2 * f(a) * f(b) * f(c) * f(d) |
!+--------------------------------------------------------------------+
              do k1=1,3                  ! k1 refers to a vector
                k2= mod(k1  ,3) + 1      ! k2=k1+1 (mod 3)
                k3= mod(k1+1,3) + 1      ! k3=k1+2 (mod 3)

                xk(1)= rx(k2,2)*rx(k3,3) - rx(k2,3)*rx(k3,2)
                xk(2)= rx(k2,3)*rx(k3,1) - rx(k2,1)*rx(k3,3)
                xk(3)= rx(k2,1)*rx(k3,2) - rx(k2,2)*rx(k3,1)

                dot= rx(k1,1)*xk(1) + rx(k1,2)*xk(2) + rx(k1,3)*xk(3)

	        dz0= ff(k2)*ff(k3)*f(i,jj)
	        dz1= dot*dot * dz0 * (dgg(k1)*ff(k1) + gg*dff(k1))
	        dz2= gg * ff4 * 2.0/rr(k1) * dot

	        do ind=1,3
	          dz(k1,ind)= rx(k1,ind)*(dz1 - dot*dz2) + dz2*xk(ind)
	        end do
              end do

	      z(i)=z(i) + zdih * gg * dot*dot * ff4
	      do ind=1,3
	        dzdx(kk,ind)=dzdx(kk,ind)         + zdih*dz(1,ind)
	        dzdx(mm,ind)=dzdx(mm,ind)         + zdih*dz(2,ind)
	        dzdxx(jj,nn,ind)=dzdxx(jj,nn,ind) + zdih*dz(3,ind)
              end do

!+-----------------------------+
!| force between atoms i and j |
!+-----------------------------+
	      bit1= (g3(i)*dg3(j) + dg3(i)*g3(j)) * f(i,jj) * dzz(i,jj)
	      bit2=  g3(i)* g3(j) * df(i,jj)
	      fac= zdih * dot*dot * ff(1)*ff(2)*ff(3) * (bit1 + bit2)
	      
	      do ind=1,3
	        dzdx(jj,ind)=dzdx(jj,ind) + fac*dxdr(i,jj,ind)
	      end do

!+-----------------------------------------------------+
!| if neighbour of i: dg3(Zi) * g3(Zj) * dot*dot * ff4 |
!+-----------------------------------------------------+
	      do nni=1,num(i)
	        if ((nni.ne.jj).and.(nni.ne.kk).and.(nni.ne.mm)) then
	        if (dr(i,nni).lt.zhigh) then
		  finiteforce(nni)=.true.
	          fac= zdih * dg3(i)*dzz(i,nni) * g3(j) * dot*dot * ff4
		  do ind=1,3
		    dzdx(nni,ind)=dzdx(nni,ind) + fac*dxdr(i,nni,ind)
		  end do
	        end if
	        end if
	      end do

!+-----------------------------------------------------+
!| if neighbour of j: dg3(Zj) * g3(Zi) * dot*dot * ff4 |
!+-----------------------------------------------------+
	      do nnj=1,num(j)
	       if ((near(j,nnj).ne.i).and.(nnj.ne.nn)) then
	       if ((dr(j,nnj).lt.zhigh)) then
	        finiteforce2(jj,nnj)=.true.
	        fac= zdih * dg3(j) * dzz(j,nnj) * g3(i) * dot*dot * ff4
		do ind=1,3
		 dzdxx(jj,nnj,ind)=dzdxx(jj,nnj,ind)+fac*dxdr(j,nnj,ind)
		end do
	       end if
	       end if
	      end do

	    end if
	    end do  !- nn loop
	  end if
	  end do  !--- mm loop
	end if
	end do  !----- kk loop
      end if
      end do  !------- jj loop

      end

