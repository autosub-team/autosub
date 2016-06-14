library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.NUMERIC_STD.ALL;

entity ALU is
    port(   A,B     : in    std_logic_vector(1 downto 0);
		 Op,Clk : in    std_logic;
            R       : out   std_logic_vector(1 downto 0));
end ALU;               
