program 
  var N as int ; 
  var SQRT as int ; 
  var AFTERIF as int;
begin 
  N := readInt ; 
  SQRT := 0 ; 

  if SQRT * SQRT <= N then 
    SQRT := SQRT + 1 ; 
    N := 5 ;
  end ; 

  AFTERIF := 100 ;

end 
