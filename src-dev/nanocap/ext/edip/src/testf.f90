

subroutine test()
    integer*4 OMP_GET_MAX_THREADS
    integer a
    integer*4 ncpu
    !$      ncpu=OMP_GET_MAX_THREADS()
    print *, "fortran ncpus",ncpu
    
    a = 1
    print *,a
end subroutine test