--fill max at cycle 1 ; empty to zero at cycle 11

--00: fifo_state= 0  next_action= fill
----------------------------------
--01: fifo_state= 0  next_action= fill
----------------------------------
--02: fifo_state= 1  next_action= fill
----------------------------------
--03: fifo_state= 2  next_action= fill
----------------------------------
--04: fifo_state= 3  next_action= empty
----------------------------------
--05: fifo_state= 2  next_action= keep
----------------------------------
--06: fifo_state= 2  next_action= keep
----------------------------------
--07: fifo_state= 2  next_action= keep
----------------------------------
--08: fifo_state= 2  next_action= keep
----------------------------------
--09: fifo_state= 2  next_action= fill
----------------------------------
--10: fifo_state= 3  next_action= empty
----------------------------------
--11: fifo_state= 2  next_action= empty
----------------------------------
--12: fifo_state= 1  next_action= empty
----------------------------------
--13: fifo_state= 0  next_action= empty
----------------------------------
--14: fifo_state= 0  next_action= keep
----------------------------------
--15: fifo_state= 0  next_action= empty
----------------------------------
--16: fifo_state= 0  next_action= empty
----------------------------------
--17: fifo_state= 0  next_action= keep
----------------------------------
--18: fifo_state= 0  next_action= fill
----------------------------------
--19: fifo_state= 1  next_action= keep
----------------------------------
--20: fifo_state= 1  next_action= keep
----------------------------------
library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;
use std.textio.ALL;
use IEEE.std_logic_textio.all;

entity blockcode_tb is
end blockcode_tb;

architecture behavior of blockcode_tb is
	component blockcode
		port(
			rst         : in   std_logic;
			clk         : in   std_logic;
			data_valid  : in   std_logic;
			data        : in   std_logic_vector(0 to 5-1);
			sink_ready  : in   std_logic;
			code_valid  : out  std_logic;
			code        : out  std_logic_vector(0 to 8-1)
		);
	end component;

	-- function to print std_logic_vectors
    function Image(In_Image : Std_Logic_Vector) return String is
        variable L : Line;  -- access type
        variable W : String(1 to In_Image'length) := (others => ' ');
    begin
         WRITE(L, In_Image);
         W(L.all'range) := L.all;
         Deallocate(L);
         return W;
    end Image;

	constant clk_period : time := 10 ms;
	constant data_len : integer := 5;
	constant code_len : integer := 8;

	signal rst_uut         : std_logic;
	signal clk_uut         : std_logic;
	signal data_valid_uut  : std_logic;
	signal data_uut        : std_logic_vector(0 to data_len-1);
	signal sink_ready_uut  : std_logic;
	signal code_valid_uut  : std_logic;
	signal code_uut        : std_logic_vector(0 to code_len-1);

	type pattern_type is record
		data_valid	: std_logic;
		data		: std_logic_vector(0 to data_len-1);
		sink_ready	: std_logic;
		code_valid	: std_logic;
		code		: std_logic_vector(0 to code_len-1);
	end record;

	type pattern_array is array (natural range <>) of pattern_type;
    
	constant patterns : pattern_array:=(
		('1',"10010",'0','0',"--------"),
		('1',"01100",'0','1',"10010101"),
		('1',"01111",'0','1',"10010101"),
		('1',"11101",'0','1',"10010101"),
		('0',"11101",'1','1',"10010101"),
		('1',"00011",'1','1',"01100011"),
		('1',"11110",'1','1',"01111000"),
		('1',"00000",'1','1',"11101101"),
		('1',"01110",'1','1',"00011011"),
		('1',"10100",'0','1',"11110110"),
		('0',"10100",'1','1',"11110110"),
		('0',"10100",'1','1',"00000000"),
		('0',"10100",'1','1',"01110010"),
		('0',"10100",'1','1',"10100010"),
		('1',"10011",'1','0',"10100010"),
		('0',"10011",'1','1',"10011111"),
		('0',"10011",'1','0',"10011111"),
		('1',"10000",'1','0',"10011111"),
		('1',"11011",'0','1',"10000100"),
		('1',"00010",'1','1',"10000100")
	);

	signal code_valid_expected : std_logic;
	signal code_expected : std_logic_vector(0 to code_len-1);

begin

	uut: blockcode
		port map(
			rst => rst_uut,
			clk => clk_uut,
			data_valid => data_valid_uut,
			data => data_uut,
			sink_ready => sink_ready_uut,
			code_valid => code_valid_uut,
			code => code_uut
		);

    -- generates the global clock cycles
    clk_generator : process
    begin
        clk_uut <= '0';
        wait for clk_period/2;
        clk_uut <= '1';
        wait for clk_period/2;
    end process;

	test: process
	begin
		-- reset in first cycle
		wait until rising_edge(clk_uut);
		rst_uut <= '1';

		for i in patterns'range loop
			wait until rising_edge(clk_uut);
			rst_uut <= '0';
			data_valid_uut <= patterns(i).data_valid;
			data_uut <= patterns(i).data;
			sink_ready_uut <= patterns(i).sink_ready;

			-- wait for the results
			wait for 10 ns;
			
			code_valid_expected <= patterns(i).code_valid;
			code_expected <= patterns(i).code;

			-- compare to expected results
			if not std_match(code_valid_uut, patterns(i).code_valid) or
			   not std_match(code_uut, patterns(i).code) then
				write(OUTPUT,string'("§{Your design does not behave like specified for clock cycle "));
				write(OUTPUT,integer'image(i+1));
				write(OUTPUT,string'(":"));

				write(OUTPUT,string'("\n"));
				write(OUTPUT,string'("\n"));

				write(OUTPUT,string'("Expected:"));
				write(OUTPUT,string'("\n"));
				write(OUTPUT,string'("   code= ") & Image(patterns(i).code));
				write(OUTPUT,string'("\n"));
				write(OUTPUT,string'("   code_valid= ") & std_logic'image(patterns(i).code_valid));
				write(OUTPUT,string'("\n"));

				write(OUTPUT,string'("Received::"));
				write(OUTPUT,string'("\n"));
				write(OUTPUT,string'("   code= ") & Image(code_uut));
				write(OUTPUT,string'("\n"));
				write(OUTPUT,string'("   code_valid= ") & std_logic'image(code_valid_uut));
				write(OUTPUT,string'("\n"));
				write(OUTPUT,string'("\n"));
				write(OUTPUT,string'("\n}§"));

				report "Simulation error" severity failure;
			end if;

        end loop;

        report "Success" severity failure;
    end process test;
end behavior;

