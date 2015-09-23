library IEEE;
use IEEE.std_logic_1164.all;

architecture behavior of truth_table is

begin
    O<= (not D and C) or (D and not C) or A or B ;
end behavior;
