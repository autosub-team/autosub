library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

entity blockcode is
	port(
		rst         : in   std_logic;
		clk         : in   std_logic;
		data_valid  : in   std_logic;
		data        : in   std_logic_vector(%%DATALEN-1 downto 0);
		sink_ready  : in   std_logic;
		code_valid  : out  std_logic;
		code        : out  std_logic_vector(%%CODELEN-1 downto 0)
	);
end blockcode;
