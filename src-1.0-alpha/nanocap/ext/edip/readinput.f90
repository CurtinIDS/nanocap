!***********************************************************************

!    call defaults    <defaults needed for readinput go here>
!    call readinput
!    call checkinput  <cleaning up after readinput done here>

!Token for each variable: eg. nstep=500
!Equals sign separates token and argument
!Semi-colon and newline separate commands
!Tabs and spaces are treated as whitespace
!Remaining text on line after '#' ignored
!Include directive using #include= <filename>

!***********************************************************************

      subroutine readinput

      include "common.f90"

      character*256 remspace,filename(100),line,value
      logical       error,errorflag

!+--------------------------------------------+
!| line 100: read new file                    |
!| line 200: read new line                    |
!| line 300: read new entry (on current line) |
!+--------------------------------------------+

      n=6
      errorflag=.false.
      if (iargc().ne.1) stop ">>> No input file <<<"
      call getarg(1,value)

 100  n=n+1
      filename(n)=value
      open(unit=n,file=filename(n),status='old')

 200  read(n,'(a256)',end=400) line

 300  line=remspace(line)

      value=line(index(line,'=')+1:)
      value=remspace(value)
      nsemi=index(value,';')
      if (nsemi.ne.0) value=value(1:nsemi-1)

      if (line(1:9).eq."#include=") goto 100
      if (line(1:1).eq."#")         goto 200
       
      !print *,"call parse", line,value,error
      call parse(line,value,error)

      if (error) then
        errorflag=.true.
        write(6,310) filename(n)(1:60)
        write(6,320) line(1:60)

 310    format('Error in file: ',a60)
 320    format('  Can''t understand: ',a60)
      end if

!+--------------------------------------------------+
!| Semi-colons separate multiple commands on a line |
!+--------------------------------------------------+
      nsemi=index(line,';')
      if (nsemi.ne.0) then
        line=line(nsemi+1:)
	goto 300   ! read more commands on current line
      else
        goto 200   ! read new line
      end if

!+-----------------------------------------------------+
!| If nested via #include then return to previous file |
!+-----------------------------------------------------+
 400  close(unit=n)
      n=n-1
      if (n.gt.6) goto 200

      if (errorflag) stop
      end
