
      subroutine coordination(i)

      include 'common.f90'


      z(i)=zz(i)

!+----------------------------+
!| Setup neighbours of atom i |
!+----------------------------+
      do jj=1,num(i)
	if ((dr(i,jj).gt.zlow).and.(dr(i,jj).lt.zhigh)) then
	  finiteforce(jj)=.true.
	else
	  finiteforce(jj)=.false.
	end if
        do ind=1,3
          dzdx(jj,ind)=dzz(i,jj)*dxdr(i,jj,ind)
        end do
      end do

!+-------------------------------------+
!| Setup neighbours-of-neighbours of i |
!+-------------------------------------+
      do jj=1,num(i)
      do kk=1,num(near(i,jj))
        finiteforce2(jj,kk)=.false.
        do ind=1,3
          dzdxx(jj,kk,ind)=0.0
        end do
      end do
      end do

!+-------------------------------+
!| Call sp/sp2 terms if required |
!+-------------------------------+
      call dihedral(i)
      call repulsion(i)
      call linear(i)

      end

