ENTITY top IS END top;

ARCHITECTURE example OF top IS
  SIGNAL w,x,y,z : integer := 0; -- initialised to 0 (zero)
BEGIN
  p1 : PROCESS(z)
    VARIABLE a : integer := 0; -- initialised to 0 (zero)
  BEGIN
	  a := a + 100;
	  w <= w + 80;
	  x <= a + w AFTER 40 ns;
	  y <= a - w AFTER 60 ns;
 END PROCESS;
 
 p2: PROCESS
 BEGIN
	 z <= (x + y) AFTER 70 ns;
	 --z <= x AFTER 70 ns;
	 WAIT ON x,y;
 END PROCESS;
END example;
