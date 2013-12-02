subroutine getforce(forcedim, force, energytotal)

    include "common.f90"
    
    integer forcedim,energydim
    real*8 force(forcedim)
    real*8, intent(out) :: energytotal
    
    do i=1,natom
        do ind=1,3
            force((i-1)*3 + ind) = fx(i,ind)
!            if(i==1) then
!                print *, i,"fortran force",fx(i,ind),force((i-1)*3 + ind)
!            end if
!            if(i==2) then
!                print *, i,"fortran force",fx(i,ind),force((i-1)*3 + ind)
!            end if
!            if(i==natom) then
!                print *, i,"fortran force",fx(i,ind),force((i-1)*3 + ind)
!            end if
!            if(i==natom-1) then
!                print *, i,"fortran force",fx(i,ind),force((i-1)*3 + ind)
!            end if
        end do    
    end do
    energytotal = pe

    !print *,"energytotal ", energytotal

end subroutine getforce
