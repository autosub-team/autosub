library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.Numeric_Std.all;
use IEEE.STD_LOGIC_UNSIGNED.all;

entity RAM is
    port( Clk : in std_logic;
     	  addr1 : in std_logic_vector(%%ADDRLENGTH downto 0);
	  addr2 : in std_logic_vector(%%ADDRLENGTH downto 0);
          %%ENTITY
     		);
end RAM;  

