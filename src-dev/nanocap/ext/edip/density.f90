
      subroutine density

      include "common.f90"

      volm=vol*1e-30
      rho=dfloat(natom)*amass/volm

      write(6,100)
      write(6,110) box(1)
      write(6,120) box(2)
      write(6,130) box(3)
      write(6,140) volm*1e27
      write(6,150) rho/1000

 100  format(/,'System Size')
 110  format(' XBOX: ',F8.2,' Ang.')
 120  format(' YBOX: ',F8.2,' Ang.')
 130  format(' ZBOX: ',F8.2,' Ang.')
 140  format(' Volume: ',F6.2,' cubic_nanometres')
 150  format(' Density: ',F5.3,' g/cc')

      end

