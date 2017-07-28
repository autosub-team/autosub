library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.NUMERIC_STD.ALL;

entity ALU is
    port(  Clk,enable : in std_logic;
     		A,B : in std_logic_vector(3 downto 0);
     		slc : in std_logic_vector(1 downto 0); 
     		R : out std_logic_vector(3 downto 0); 
     		flag : out std_logic);
end ALU;  

