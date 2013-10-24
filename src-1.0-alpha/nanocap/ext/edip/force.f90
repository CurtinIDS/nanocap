
      subroutine force

      include "common.f90"

!+-----------------------+
!| Get Number of Threads |
!+-----------------------+
      !ncpu=1
!$      ncpu=OMP_GET_MAX_THREADS()
      !print *, "fortran ncpus",ncpu
!+------------------------+
!| Clear temporary arrays |
!+------------------------+
      do icpu=1,ncpu
        u2i(icpu)=0.0
        u3i(icpu)=0.0
        udihi(icpu)=0.0
      end do

      do i=1,natom
      do ind=1,3
          do icpu=1,ncpu
            fxx(i,ind,icpu)=0.0
          end do
        end do
      end do

!+--------------------------+
!| Main loop over the atoms |
!+--------------------------+
      call distance
      call cutoff

!$OMP PARALLEL DO SCHEDULE(STATIC) PRIVATE(i)
      do i=1,natom
        call coordination(i)
        call pair(i)
        call triple(i)
      end do
!$OMP END PARALLEL DO

!+--------------------------+
!| Manually reduce energies |
!+--------------------------+
      u2=0.0
      u3=0.0
      udih=0.0
      do icpu=1,ncpu
        u2=u2 + u2i(icpu)
        u3=u3 + u3i(icpu)
        udih=udih + udihi(icpu)
      end do
      pe=u2+u3+udih

!+------------------------+
!| Manually reduce forces |
!+------------------------+
      do i=1,natom
        do ind=1,3
          fx(i,ind)=0.0
          do icpu=1,ncpu
            fx(i,ind)=fx(i,ind) + fxx(i,ind,icpu)
            !print *, "fortran force",fx(i,ind)
          end do
        end do
      end do

      end
