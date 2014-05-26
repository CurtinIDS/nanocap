
      subroutine printrings

      include "common.f90"

      character*80 exe,awk

      if (norings) return

!+------------------------------------------+
!| Write out coordinates in xyz file format |
!+------------------------------------------+
      open(unit=9,file='tmp.edip.xyz',status='unknown')
      write(9,*) natom
      write(9,*) 'EDIP',box(1)
      do i=1,natom
        write(9,*) 'C',(x(i,j),j=1,3)
      end do
      close(unit=9)

!+----------------------------------------------+
!| Create script to be read as stdin by Rings.x |
!+----------------------------------------------+
      open(unit=9,file='tmp.edip.stdin',status='unknown')
      write(9,*) 'tmp.edip.xyz'
      write(9,*) bondcutoff
      write(9,*) '12'
      close(unit=9)

!+---------------------------------------+
!| Execute shell command and tidy output |
!+---------------------------------------+
      write(6,*)
      exe="/usr/people/nigel/carbon/rings/Rings.x"
      awk="tail -14 | awk '{print ""#"",$0}'"
      call system(exe//" < tmp.edip.stdin | "//awk)
      call system("/bin/rm -f tmp.edip.xyz tmp.edip.stdin")

      end
