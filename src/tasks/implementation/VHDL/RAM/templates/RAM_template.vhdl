library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

entity RAM is
    port( Clk : in std_logic;
     	  addr1 : in std_logic_vector(%%ADDRLENGTH downto 0);
	  addr2 : in std_logic_vector(%%ADDRLENGTH downto 0);
          %%ENTITY
     		);
end RAM;  

