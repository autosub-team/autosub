library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

entity counter is
	port(
		CLK         : in   std_logic;
{{entity_in_out}}
	);
end counter;
