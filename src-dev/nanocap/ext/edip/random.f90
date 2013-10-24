       program random_atoms

       real rand

       write(6,100)
       write(6,110)
       read(5,*) boxx,boxy,boxz,ndens
       natom = nint(0.001*ndens*boxx*boxy*boxz)
 100   format('LATTICE: Random atoms generator  ')
 110   format('LATTICE: Enter x,y,z box dimensions and number density')
 120   format('LATTICE: Number Density= ',f6.3)
 130   format('BOX: box x= ',f6.3,'  box y= ',f6.3,'  box z= ',f6.3)

       iseed=31415
       dummy=rand(iseed)

       write(6,120) natom
       write(6,130) boxx,boxy,boxz

       open(unit=7,file='RESTART_random',status='unknown')
       write(7,*) 0, 0, natom
       write(7,*) boxx,boxy,boxz

       do i=0,natom-1
             call atom(boxx,boxy,boxz)
       end do

       close(unit=7)

       end

!**********************************************************************

       subroutine atom(boxx,boxy,boxz)

       real    rand
       real    boxx,boxy,boxz

       xdiff= 1.0*(rand()-0.5) * boxx
       ydiff= 1.0*(rand()-0.5) * boxy
       zdiff= 1.0*(rand()-0.5) * boxz

       write(7,100) xdiff, ydiff, zdiff
 100   format(3(f7.3,3x))
       end
