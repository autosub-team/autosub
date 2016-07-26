library IEEE;
use IEEE.std_logic_1164.all;

entity ROM is
    port(  Clk,enable : in std_logic;
     		addr : in std_logic_vector(%%ADDRLENGTH downto 0);
     		output : in std_logic_vector(%%INSTRUCTIONLENGTH downto 0));
end ROM;  

