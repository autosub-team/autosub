LIBRARY IEEE;
USE IEEE.std_logic_1164.ALL;
USE IEEE.numeric_std.ALL;

entity ROM_tb is
end ROM_tb;

architecture Behavioral of ROM_tb is
    component ROM port(Clk,enable : in std_logic;
     		addr : in std_logic_vector({{ADDRLENGTH}}  downto 0);
     		output : out std_logic_vector({{INSTRUCTIONLENGTH}} downto 0));
    end component;


    signal Clk,enable : std_logic := '0'; --clock signal and enable
    signal addr : std_logic_vector({{ADDRLENGTH}}  downto 0) := (others => '0'); --address
    signal output : std_logic_vector({{INSTRUCTIONLENGTH}} downto 0) := (others => '0');  --output of ROM
    constant Clk_period : time := 10 ns;


BEGIN

    -- Instantiate the Unit Under Test (UUT)
 UUT: ROM port map (
        Clk => Clk, enable => enable, addr => addr, output => output);

   -- Clock process definitions
   Clk_process :process
   begin
        Clk <= '0';
        wait for Clk_period/2;
        Clk <= '1';
        wait for Clk_period/2;
   end process;

   -- Stimulus process
   stim_proc: process

        type random_array is array (0 to {{DATALENGTH}}-1) of integer;
        constant random : random_array :=(
                                    {{RANDOM}});

   begin

     enable <= '1';

     for i in random'range loop
         addr <= std_logic_vector(to_unsigned(random(i),{{ADDRLENGTH}}+1));
         wait for Clk_period;
     end loop;
      wait;
   end process;

END;
