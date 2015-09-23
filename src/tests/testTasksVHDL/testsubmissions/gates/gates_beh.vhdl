library IEEE;
use IEEE.std_logic_1164.all;
use work.IEEE_1164_Gates_pkg.all;

architecture behavior of gates is
signal s1 : std_logic;
signal s2 : std_logic;
signal s3 : std_logic;
signal s4 : std_logic;
signal s5 : std_logic;
signal notA : std_logic;
signal notB : std_logic;
signal notC : std_logic;
signal notD : std_logic;

begin
G0 : NOR3
   port map
   (
      I1 => notA,
      I2 => notB,
      I3 => D,
      O  => s1
   );

G1 : OR3
   port map
   (
      I1 => B,
      I2 => notC,
      I3 => notD,
      O  => s2
   );

G2 : NAND2
   port map
   (
      I1 => A,
      I2 => notD,      
      O  => s3
   );

G3 : AND2
   port map
   (
      I1 => A,
      I2 => notD,      
      O  => s4
   );

G4 : NOR4
   port map
   (
      I1=>s1,
      I2=>s2,
      I3=>s3,
      I4=>s4,
      O=> s5
   );

O    <= s5;

notA <= not A;
notB <= not B;
notC <= not C;
notD <= not D;

end behavior;
