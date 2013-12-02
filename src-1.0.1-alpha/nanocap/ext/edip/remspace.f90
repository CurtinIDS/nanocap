
      function remspace(value)

      character*256 remspace,value

      do 100 i=1,256
        if (value(i:i).eq.' ')      goto 100
        if (ichar(value(i:i)).eq.9) goto 100
        remspace=value(i:)
        return
 100  continue

      remspace="#"
      end

