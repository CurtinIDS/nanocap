
      subroutine init

      include "common.f90"

!+-----------------+
!| g(r) statistics |
!+-----------------+
      do ix=1,NGR
        nframe(ix)=0
        do i=1,numbin
          nbin(ix,i)=0.0
        end do
      end do

!+------------------+
!| Angle statistics |
!+------------------+
      do i=1,NGR
        do j=1,3
          do k=1,numbin2
            nbin2(i,j,k)=0
          end do
        end do
      end do

!+---------------+
!| Stress Tensor |
!+---------------+
      do ind1=1,3
	do ind2=1,3
          totstr(ind1,ind2)= 0.0
	end do
      end do

!+-----------------+
!| Kronecker Delta |
!+-----------------+
      do i=1,NNN
        do j=1,NNN
          if (i.ne.j) kron(i,j)=0.0
          if (i.eq.j) kron(i,j)=1.0
        end do
      end do

!+---------------------------------------+
!| Set the temperature conversion factor |
!+---------------------------------------+
      ndim=3
      tfac=2.0/ndim / BOLTZMANN

!+-------------------------+
!| Initialise some numbers |
!+-------------------------+
      vflag=0
      nstress=0
      numstep=0
      iseed=31415
      elosttherm=0.0

!+--------------------------------------------+
!| Store initial Potential and Kineti!Energy |
!+--------------------------------------------+
      call volume
      call neighbour
      write(6,*)'Initializing...'
      call force
!    call energy
      call properties
      call writexbs
!    call stress(0)

      pestart= pe
      ekestart= eke
      end 
