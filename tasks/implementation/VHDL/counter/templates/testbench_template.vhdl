library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use std.textio.all;
use ieee.std_logic_textio.all;

entity counter_tb is
end counter_tb;

architecture Behavioral of counter_tb is

	component counter is
		port (
			CLK  : in  STD_LOGIC;
%%entity_in_out
	);
	end component;

	constant random_counter_value : integer := %%random_counter_value;
	constant init_value : integer := %%init_value;
	constant counter_width : integer := %%counter_width;
	constant counter_max : integer := %%counter_max;

	-- TODO: remove debugging signals:
	signal bla0 : std_logic := '0';
	signal bla1 : std_logic := '0';
	signal bla2 : std_logic := '0';
	signal bla3 : std_logic := '0';

	type type_input_test_array is array(0 to (3 - 1)) of std_logic_vector((counter_width-1) downto 0);
	signal input_test_array : type_input_test_array := (%%input_test_array);

	-- Inputs and Outputs:
	signal CLK : std_logic := '0';
%%signal_in_out

	-- Clock period definitions:
	constant CLK_period : time := 20 ns;

	function image(in_image : std_logic_vector) return string is
		variable L : Line;  -- access type
		variable W : String(1 to in_image'length) := (others => ' ');
	begin
		WRITE(L, in_image);
		W(L.all'range) := L.all;
		Deallocate(L);
		return W;
	end image;

begin

	UUT: counter
		port map
		(	CLK => CLK,
%%port_map_in_out
			);

	test_counter_beh: process
		variable i : integer := 0;
	begin

	   -- check initial value:
		wait for CLK_period/4;
		if (Output /= std_logic_vector(to_unsigned(init_value, Output'length))) then
			report "§{Initial counter value not right. Received " & image(Output) & ". Expected " & image(std_logic_vector(to_unsigned(init_value, Output'length))) & ".}§" severity failure;
		end if;
		wait for CLK_period/2;
		bla0 <= '1';
%%enable_check_code

		-- check counter output values for one full cycle:
		for i in (init_value + 1) to (counter_max-1) loop
			if (Output /= std_logic_vector(to_unsigned(i, Output'length))) then
				report "§{Output value not right. Received " & image(Output) & ". Expected " & image(std_logic_vector(to_unsigned(i, Output'length))) & ".}§" severity failure;
			end if;
			wait for CLK_period;
		end loop;
		bla1 <= '1';
%%overflow_check_code
		bla2 <= '1';
%%synchronous_check_code
		bla3 <= '1';
%%asynchronous_check_code

	report "Success" severity failure;
	end process test_counter_beh;




	-- Clock process definitions
   CLK_process :process
   begin
		CLK <= '0';
		wait for CLK_period/2;
		CLK <= '1';
		wait for CLK_period/2;
   end process;

end Behavioral;
