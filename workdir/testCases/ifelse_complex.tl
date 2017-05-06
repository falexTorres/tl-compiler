program 
  var N as int ; 
  var SQRT as int ; 
  var AFTERELSE as int;
begin 
  N := readInt ; 
  SQRT := 0 ; 

  if SQRT * SQRT <= N then 
    SQRT := SQRT + 1 ; 
    N := 5 ;
  else
    N := 2 ;
  end ;

  if SQRT * SQRT <= N then 
    SQRT := SQRT + 1 ; 
    N := 5 ;
  end ;

  if SQRT * SQRT <= N then 
    SQRT := SQRT + 1 ; 
    N := 5 ;
  else
    N := 2 ;
  end ; 

  AFTERELSE := 100 ;

end 
