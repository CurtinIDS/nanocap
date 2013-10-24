
      subroutine checkrij(i,j)

      include "common.f90"

      parameter (rskin=0.10)
      dimension dxx(3)

      rcut=c0+2.0*rskin
      if (special) rcut=c0

      do ind=1,3
        delta= x(i,ind) - x(j,ind)
        dxx(ind)=delta - box(ind)*dnint(delta/box(ind))
      end do

!This if-block for non-orthogonal coordinate system
      if (computeshear) then
       dxx(2)=dxx(2) + shear*dxx(3)
      endif

      rijsq=0.0
      do ind=1,3
        rijsq=rijsq + dxx(ind)*dxx(ind)
      end do
      rij=sqrt(rijsq)

      if (rij.lt.rcut) then
        num(i)=num(i)+1
        num(j)=num(j)+1

        near(i,num(i))=j
        near(j,num(j))=i

        npair=npair+1
        ipair(npair)=i
        jpair(npair)=j

        inum(npair)=num(i)
        jnum(npair)=num(j)
      end if

      end

