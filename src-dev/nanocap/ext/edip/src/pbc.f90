      program pbc

      parameter (NMAX=10000,cutoff=1.85)

      dimension    x(NMAX,3),nn(NMAX), box(3), nnn(10)
      character*80 arg1,arg2,arg3,arg4

!+-----------------------------------------+
!| Parse command line and read coordinates |
!+-----------------------------------------+
      call getarg(1,arg1)
      call getarg(2,arg2)
      call getarg(3,arg3)
      call getarg(4,arg4)

      read(arg1,*) natom
      read(arg2,*) box(1)
      read(arg3,*) box(2)
      read(arg4,*) box(3)

      write(6,*) 'natom=',natom

      do i=1,natom
        read(5,*) (x(i,ind),ind=1,3)
      end do

!+----------------------+
!| Compute coordination |
!+----------------------+
      do i=1,natom
        nn(i)=0
      end do

      do i=1,natom
        do j=i+1,natom
	  rijsq=0
	  do ind=1,3
	    dx= x(i,ind)-x(j,ind)
	    dx=dx - box(ind)*nint(dx/box(ind))
	    rijsq=rijsq + dx*dx
	  end do
	  rij=sqrt(rijsq)

          if (rij.lt.cutoff) nn(i)=nn(i)+1
          if (rij.lt.cutoff) nn(j)=nn(j)+1
	end do
      end do

!+---------------------------------+
!| Compute coordination statistics |
!+---------------------------------+
      do i=1,10
        nnn(i)=0
      end do

      do i=1,natom
        if (nn(i).le.1) nn(i)=1
        if (nn(i).ge.5) nn(i)=5
	nnn(nn(i))= nnn(nn(i)) + 1
      end do

      do i=1,5
        write(6,100) i,real(nnn(i))/natom * 100
 100    format('%nn',i1,'= ',F6.2)
      end do

!+-------------------+
!| Write pbc.bs file |
!+-------------------+
      open(unit=7,file='pbc.bs',status='unknown')
      do i=1,natom
	do ind=1,3
          x(i,ind)=x(i,ind) - box(ind)*nint(x(i,ind)/box(ind))
          !x(i,ind)=x(i,ind) - box(ind)*(nint(x(i,ind)/box(ind)-0.5)+0.5)
	end do

	write(7,110) nn(i),(x(i,ind),ind=1,3)
 110    format('atom C',i1,3F10.3)
      end do

      write(7,*) 'spe!C1 0.25 black'
      write(7,*) 'spe!C2 0.25 red'
      write(7,*) 'spe!C3 0.25 green'
      write(7,*) 'spe!C4 0.25 blue'
      write(7,*) 'spe!C5 0.25 orange'
      write(7,*) 'in!3'

      write(7,120) cutoff
 120  format('bonds * * 0 ',F5.2,' 0.075 0.8')

      end

