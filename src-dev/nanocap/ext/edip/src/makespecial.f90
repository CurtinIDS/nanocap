 
       subroutine makespecial(r,b,theta)
 
       include "common.f90"

       if (namespecial(1:3).eq.'gra') goto 100
       if (namespecial(1:3).eq.'lin') goto 200
       if (namespecial(1:3).eq.'tmm') goto 300
       if (namespecial(1:3).eq.'ben') goto 400
       if (namespecial(1:3).eq.'two') goto 500

       stop '>> Should not be here <<'
 
!+-----------------------------------------------+
!| Structure for graphite/diamond transformation |
!+-----------------------------------------------+
 100  rprime=-b*cosd(theta)
      bprime= b*sind(theta)

      xbox=       3.0*bprime
      ybox= sqrt(3.0)*bprime
      zbox= 3.0*(r+rprime)

      nx=2
      ny=3
      nz=1

      natom=0
      do iz=0,nz-1
      do iy=0,ny-1
      do ix=0,nx-1
	do izz=-1,1
         x00= ix*xbox + izz*0.5*bprime
	  y00= iy*ybox + izz*0.5*bprime*sqrt(3.0)
	  z00= iz*zbox + izz*(r+rprime)

	  x(natom+1,1)= x00
	  x(natom+2,1)= x00 +     bprime
	  x(natom+3,1)= x00 + 1.5*bprime
	  x(natom+4,1)= x00 + 2.5*bprime

	  x(natom+1,2)= y00
	  x(natom+2,2)= y00
	  x(natom+3,2)= y00 + 0.5*sqrt(3.0)*bprime
	  x(natom+4,2)= y00 + 0.5*sqrt(3.0)*bprime

	  x(natom+1,3)= z00 + 0.5*rprime
	  x(natom+2,3)= z00 - 0.5*rprime
	  x(natom+3,3)= z00 + 0.5*rprime
	  x(natom+4,3)= z00 - 0.5*rprime

          natom=natom+4
	end do
      end do
      end do
      end do

      box(1)= nx*xbox
      box(2)= ny*ybox
      box(3)= nz*zbox
      return

!+----------------------------------------------+
!| Structure for linear/graphite transformation |
!+----------------------------------------------+
 200  bx= -b*cosd(theta)
      by=  b*sind(theta)

      xbox= 2.0*(r+bx)
      ybox= 2.0*by

      nx=2
      ny=3

      natom=0
      do iy=0,ny-1
        do ix=0,nx-1
          x00= ix*xbox
	  y00= iy*ybox

	  x(natom+1,1)= x00
	  x(natom+2,1)= x00 + 1.0*r
	  x(natom+3,1)= x00 + 1.0*r + bx
	  x(natom+4,1)= x00 + 2.0*r + bx

	  x(natom+1,2)= y00
	  x(natom+2,2)= y00
	  x(natom+3,2)= y00 + by
	  x(natom+4,2)= y00 + by

          natom=natom+4
	end do
      end do

      do i=1,natom
        x(i,3)=0.0
      end do

      box(1)= nx*xbox
      box(2)= ny*ybox
      box(3)= 100.0
      return

!+-------------------------------+
!| Bensan out-of-plane bend: TMM |
!+-------------------------------+
 300  rcc=1.42
      rch=1.33
      rch2= rc!+ 0.5*rch

      root3on2=0.5*sqrt(3.0)
      natom=10

!X-coords
      x(1,1)=  0.0
      x(2,1)= -0.5*rcc
      x(3,1)= -0.5*rcc
      x(4,1)= -0.5*rc!- rch
      x(5,1)= -0.5*rc!- rch
      x(6,1)= -0.5*rc!+ 0.5*rch
      x(7,1)= -0.5*rc!+ 0.5*rch
      x(8,1)=   rcc*cosd(theta)
      x(9,1)=  rch2*cosd(theta)
      x(10,1)= rch2*cosd(theta)

!Y-coords
      x(1,2)= 0.0
      x(2,2)=  root3on2*rcc
      x(3,2)= -root3on2*rcc
      x(4,2)=  root3on2*rcc
      x(5,2)= -root3on2*rcc
      x(6,2)=  root3on2*rc!+ root3on2*rch
      x(7,2)= -root3on2*rc!- root3on2*rch
      x(8,2)= 0.0
      x(9,2)=   root3on2*rch
      x(10,2)= -root3on2*rch

!Z-coords
      do i=1,7
        x(i,3)=0.0
      end do
      x(8,3)=   rcc*sind(theta)
      x(9,3)=  rch2*sind(theta)
      x(10,3)= rch2*sind(theta)

      box(1)=100.0
      box(2)=100.0
      box(3)=100.0
      return

!+-----------------------------------+
!| Bensan out-of-plane bend: benzene |
!+-----------------------------------+
 400  rcc=1.42
      rch=1.33

      root3on2=0.5*sqrt(3.0)
      natom=12

!X-coords
      x(1,1)=  0.0
      x(2,1)=  0.0     + 0.5*rch
      x(3,1)= -1.0*rcc
      x(4,1)= -1.0*rcc- 0.5*rch
      x(5,1)= -1.5*rcc
      x(6,1)= -1.5*rcc- 1.0*rch
      x(7,1)= -1.0*rcc
      x(8,1)= -1.0*rcc- 0.5*rch
      x(9,1)=  0.0
      x(10,1)= 0.0     + 0.5*rch
      x(11,1)=   0.5*rcc      *cosd(theta)
      x(12,1)=  (0.5*rcc+ rch)*cosd(theta)

!Y-coords
      x(1,2)=  -root3on2*rcc
      x(2,2)=  -root3on2*rc!- root3on2*rch
      x(3,2)=  -root3on2*rcc
      x(4,2)=  -root3on2*rc!- root3on2*rch
      x(5,2)=  0.0
      x(6,2)=  0.0
      x(7,2)=   root3on2*rc!
      x(8,2)=   root3on2*rc!+ root3on2*rch
      x(9,2)=   root3on2*rcc
      x(10,2)=  root3on2*rc!+ root3on2*rch
      x(11,2)=  0.0
      x(12,2)=  0.0

!Z-coords
      do i=1,10
        x(i,3)=0.0
      end do
      x(11,3)=   0.5*rcc      *sind(theta)
      x(12,3)=  (0.5*rcc+ rch)*sind(theta)

      box(1)=100.0
      box(2)=100.0
      box(3)=100.0
      return

!+----------------------------------------+
!| Structure for linear chain with a bend |
!+----------------------------------------+
 500  do i=1,7
        x(i,1)= -1.33*(i-1)
        x(i,2)= 0.0
        x(i,3)= 0.0

	x(i+7,1)= 1.33*i * cosd(theta)
	x(i+7,2)= 1.33*i * sind(theta)
	x(i+7,3)= 0.0
      end do

      natom=14
      box(1)=100.0
      box(2)=100.0
      box(3)=100.0

      end

!+-------------------------+
!| Cos function in degrees |
!+-------------------------+
      function cosd(angle)
      include "common.f90"

      cosd=cos(angle*pi/180.0)
      end

!+-------------------------+
!| Sin function in degrees |
!+-------------------------+
      function sind(angle)
      include "common.f90"

      sind=sin(angle*pi/180.0)
      end
