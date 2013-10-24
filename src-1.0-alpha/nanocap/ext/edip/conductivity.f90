      subroutine conductivity

      include 'common.f90'

      integer   slab_atoms
      dimension slab_atoms(MAXSLAB),slab_ke(MAXSLAB),slab_temp(MAXSLAB)

      save swap_ke

      if (nswap.eq.0)              return
      if (mod(numstep,nswap).ne.0) return

! 	    Write header line for first line of output
      if (numstep.eq.nswap) then
        swap_ke=0.0

        open(unit=8,file='thermal.out',status='unknown')
        area=box(2)*box(3)
        write(8,100) nslab,nswap,area,box(1)
        close(unit=8)
 100    format('# ',I3,1x,I4,1x,F9.3,1x,F9.3)
      end if

! 	    Cold slab = slab number 1
! 	    Hot slab = slab in the middle

      hot_ke=-1.0
      cold_ke=1000.0
      xslab= box(1)/nslab
      middle=nslab/2+1

      do loop=1,nslab
        slab_ke(loop)=0.0
        slab_atoms(loop)=0
      end do

      do i=1,natom
        xx= x(i,1)-box(1)*dnint(x(i,1)/box(1))  ! projects to [-L/2:+L/2]
        if (xx.lt.0.0) xx=xx+box(1)             ! projects to [0:L]
        islab=int(xx/xslab)+1
        if (islab.gt.nslab) islab=nslab         ! just in case xx=nslab+1

        atom_ke=0.5*(vx(i,1)**2+vx(i,2)**2+vx(i,3)**2)
        slab_ke(islab)=slab_ke(islab)+atom_ke
        slab_atoms(islab)=slab_atoms(islab)+1

        if ((islab.eq.1).and.(atom_ke.gt.hot_ke)) then
          ihot=i
          hot_ke=atom_ke
        endif

        if ((islab.eq.middle).and.(atom_ke.lt.cold_ke)) then
          icold=i
          cold_ke=atom_ke
        endif
      end do

! 	    Check that the swap is correct
        ehot=vx(ihot,1)**2+vx(ihot,2)**2+vx(ihot,3)**2
        ecold=vx(icold,1)**2+vx(icold,2)**2+vx(icold,3)**2
      if(ehot.le.ecold) then
        write(6,*) 'warning, a velocityswap in the wrong direction'
      endif

! 	    Swapping the velocities of the hot and cold atoms
      do ind=1,3
        vold=vx(ihot,ind)
        vx(ihot,ind)=vx(icold,ind)
        vx(icold,ind)=vold
      end do
      vflag=1.0

      swap_ke=swap_ke + hot_ke - cold_ke

! 	    Adjust KE of cold & hot slabs, and convert to Kelvin
      slab_ke(1)= slab_ke(1)           - hot_ke + cold_ke
      slab_ke(middle)= slab_ke(middle) + hot_ke - cold_ke

      do loop=1,nslab
        slab_temp(loop)=slab_ke(loop)/dfloat(slab_atoms(loop)) * tfac
      end do

! 	    Write temperature of slabs to file
      open(unit=8,file='thermal.out',status='unknown',access='append')
      tnow=numstep*h*timetau
      write(8,110) tnow,swap_ke,(slab_temp(loop),loop=1,nslab)
      close(unit=8)

 110  format(F9.3,1X,F9.3,999(1X,F7.2))

      end
