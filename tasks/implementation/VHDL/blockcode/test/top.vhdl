library IEEE;
use IEEE.std_logic_1164.all;

entity top is
	port
	(
		rst         : in   std_logic;
		clk         : in   std_logic;
		data_valid  : in   std_logic;
		data        : in   std_logic_vector(3-1 downto 0);
		sink_ready  : in   std_logic;
		code_valid  : out  std_logic;
		code        : out  std_logic_vector(5-1 downto 0)
	);
end top;

architecture beh of top is
	component blockcode_source
	port(
        rst         : in   std_logic;
		clk         : in   std_logic;
		data_valid  : in   std_logic;
		data        : in   std_logic_vector(3-1 downto 0);
		sink_ready  : in   std_logic;
		code_valid  : out  std_logic;
		code        : out  std_logic_vector(5-1 downto 0)
	);
	end component;
begin

	device : blockcode_source port map(rst, clk, data_valid, data, sink_ready,
										code_valid, code);

end beh;
