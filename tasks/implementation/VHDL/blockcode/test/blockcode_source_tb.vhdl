library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;
use std.textio.ALL;
use IEEE.std_logic_textio.all;

entity blockcode_source_tb is
end blockcode_source_tb;

architecture behavior of blockcode_source_tb is
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
	constant data_len : integer := 3;
	constant code_len : integer := 5;

	signal rst_uut         : std_logic;
	signal clk_uut         : std_logic;
	signal data_valid_uut  : std_logic;
	signal data_uut        : std_logic_vector(data_len-1 downto 0);
	signal sink_ready_uut  : std_logic;
	signal code_valid_uut  : std_logic;
	signal code_uut        : std_logic_vector(code_len-1 downto 0);

	type pattern_type is record
		data_valid	: std_logic;
		data		: std_logic_vector(data_len-1 downto 0);
		sink_ready	: std_logic;
		code_valid	: std_logic;
		code		: std_logic_vector(code_len-1 downto 0);
	end record;

	constant D0 : std_logic_vector(2 downto 0) := "111";
	constant D1 : std_logic_vector(2 downto 0) := "101";
	constant D2 : std_logic_vector(2 downto 0) := "100";
	constant D3 : std_logic_vector(2 downto 0) := "001";
	constant D4 : std_logic_vector(2 downto 0) := "110";

	constant C0 : std_logic_vector(4 downto 0) := "00" & D0;
	constant C1 : std_logic_vector(4 downto 0) := "11" & D1;
	constant C2 : std_logic_vector(4 downto 0) := "10" & D2;
	constant C3 : std_logic_vector(4 downto 0) := "01" & D3;
	constant C4 : std_logic_vector(4 downto 0) := "01" & D4;

    type pattern_array is array (natural range <>) of pattern_type;

    constant patterns : pattern_array:=(
		('1', D0, '1', '0', "-----"), -- '-' is dont care
		('1', D1, '1', '1', C0),
		('0', D1, '1', '1', C1),
		('1', D2, '0', '0', C1),
		('1', D3, '0', '1', C2),
		('1', D4, '1', '1', C2),
		('0', D4, '1', '1', C3),
		('0', D4, '1', '1', C4),
		('0', D4, '1', '0', C4)
	);
begin

	uut: blockcode_source
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
		-- states after edge
		variable code_valid_edge : std_logic;
		variable code_edge : std_logic_vector(code_len-1 downto 0);
	begin
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

			code_valid_edge := code_valid_uut;
			code_edge := code_uut;

			-- check1 for non changing signals during cycle
			wait for clk_period * 1/2;
			if (code_valid_uut /= code_valid_edge) or (code_uut /= code_edge) then
				write(OUTPUT,string'("§{Your design does not behave like specified for clock cycle "));
				write(OUTPUT,integer'image(i+1));
				write(OUTPUT,string'(":"));

                write(OUTPUT,string'("\n"));
                write(OUTPUT,string'("\n"));

				write(OUTPUT,string'("Your output signals change during the clock cycle"));

                write(OUTPUT,string'("\n"));
                write(OUTPUT,string'("\n"));

				write(OUTPUT,string'("At rising edge of clk:"));
                write(OUTPUT,string'("\n"));
				write(OUTPUT,string'("   code= ") & Image(code_edge));
                write(OUTPUT,string'("\n"));
                write(OUTPUT,string'("   code_valid= ") & std_logic'image(code_valid_edge));
                write(OUTPUT,string'("\n"));

				write(OUTPUT,string'("Received:"));
                write(OUTPUT,string'("\n"));
				write(OUTPUT,string'("   code= ") & Image(code_uut));
                write(OUTPUT,string'("\n"));
                write(OUTPUT,string'("   code_valid= ") & std_logic'image(code_valid_uut));
                write(OUTPUT,string'("\n"));
				write(OUTPUT,string'("\n"));
                write(OUTPUT,string'("\n}§"));

				--report "Simulation error" severity failure;
			end if;

			-- check2 for non changing signals during cycle
			wait for clk_period * 1/4;
			if (code_valid_uut /= code_valid_edge) or (code_uut /= code_edge) then
				write(OUTPUT,string'("§{Your design does not behave like specified for clock cycle "));
				write(OUTPUT,integer'image(i+1));
				write(OUTPUT,string'(":"));

                write(OUTPUT,string'("\n"));
                write(OUTPUT,string'("\n"));

				write(OUTPUT,string'("Your output signals change during the clock cycle"));

                write(OUTPUT,string'("\n"));
                write(OUTPUT,string'("\n"));

				write(OUTPUT,string'("At rising edge of clk:"));
                write(OUTPUT,string'("\n"));
				write(OUTPUT,string'("   code= ") & Image(code_edge));
                write(OUTPUT,string'("\n"));
                write(OUTPUT,string'("   code_valid= ") & std_logic'image(code_valid_edge));
                write(OUTPUT,string'("\n"));

				write(OUTPUT,string'("Received:"));
                write(OUTPUT,string'("\n"));
				write(OUTPUT,string'("   code= ") & Image(code_uut));
                write(OUTPUT,string'("\n"));
                write(OUTPUT,string'("   code_valid= ") & std_logic'image(code_valid_uut));
                write(OUTPUT,string'("\n"));
				write(OUTPUT,string'("\n"));
                write(OUTPUT,string'("\n}§"));

				--report "Simulation error" severity failure;
			end if;

        end loop;

        report "Success" severity failure;
    end process test ;
end behavior;
