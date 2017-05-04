program 
  var N as int ; 
  var SQRT as int ; 
  var B as bool;
begin 
  N := readint ; 
  SQRT := 0 ; 
  B := true;

  if B then
     SQRT := 0 + 1;
  else
     B := false;
  end 

  SQRT := 5 mod 7;
  SQRT := 10 div 8;
  

  B := SQRT = 0;
  B := SQRT != 0;
  B := SQRT < 0;
  B := SQRT > 0;
  B := SQRT <= 0;
  B := SQRT >= 0;

  while SQRT * SQRT <= N do 
    SQRT := SQRT + 1 ; 
  end 

  SQRT := ( SQRT - 1 );

  writeint SQRT ; 

end 
