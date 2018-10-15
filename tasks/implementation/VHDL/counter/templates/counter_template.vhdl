library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

entity counter is
	port(
		CLK         : in   std_logic;
		RST         : in   std_logic;
	{% if enable %}
		Enable      : in   std_logic;	
	{% endif %}
		Sync{{ sync_variation }}   : in   std_logic;
		Async{{ async_variation}}   : in   std_logic;
	{% if input_necessary %}
		Input       : in   std_logic_vector(({{ counter_width }}-1) downto 0);	
	{% endif %}
	{% if overflow %}
		Overflow    : out  std_logic;
	{% endif %}
		Output      : out  std_logic_vector(({{ counter_width }}-1) downto 0)
	);
end counter;
