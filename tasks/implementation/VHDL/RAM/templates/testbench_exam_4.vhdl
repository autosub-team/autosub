LIBRARY IEEE;
USE IEEE.std_logic_1164.ALL;
USE IEEE.numeric_std.ALL;

entity RAM_tb is
end RAM_tb;

architecture Behavioral of RAM_tb is
    component RAM port(Clk : in std_logic;
                       addr1 : in std_logic_vector({{ADDRLENGTH}}  downto 0); --address
                       addr2 : in std_logic_vector({{ADDRLENGTH}}  downto 0); --address
                       en_read : in std_logic; -- read-enable
                       en_write : in std_logic; -- write-enable
                       input : in std_logic_vector({{WRITELENGTH}} downto 0);  --input
                       output : out std_logic_vector({{READLENGTH}} downto 0));  --output
    end component;

    signal Clk : std_logic := '0'; --clock signal
    signal addr1 : std_logic_vector({{ADDRLENGTH}}  downto 0) := (others => '0'); --address
    signal addr2 : std_logic_vector({{ADDRLENGTH}}  downto 0) := (others => '0'); --address
    signal en_read : std_logic := '0'; -- read-enable
    signal en_write : std_logic := '0'; -- write-enable
    signal input : std_logic_vector({{WRITELENGTH}} downto 0) := (others => '0');  --input
    signal output : std_logic_vector({{READLENGTH}} downto 0) := (others => '0');  --output
    constant Clk_period : time := 10 ns;

begin
  -- Instantiate the Unit Under Test (UUT)
 UUT: RAM port map (
        Clk => Clk,
        addr1 => addr1,
        addr2 => addr2,
        en_read => en_read,
        en_write => en_write,
        input => input,
        output => output
        );

   -- Clock process definitions
   Clk_process :process
   begin
        Clk <= '0';
        wait for Clk_period/2;
        Clk <= '1';
        wait for Clk_period/2;
   end process;

 stim_proc: process

        type random_array is array (0 to 5) of std_logic_vector({{ADDRLENGTH}} downto 0);
        constant random_addr : random_array :=(
                                    {{RANDOM_ADDR}});

        type content_array_in is array (0 to 5) of std_logic_vector({{WRITELENGTH}} downto 0);
        constant content_in : content_array_in :=(
        					       {{CONTENT_IN1}});

        constant content_test_in : content_array_in :=(
                                                {{CONTENT_IN2}});

   begin

    -- writing data in the memory
     for i in random_addr'range loop
         en_write <= '1';
         en_read <= '0';
         addr1 <= random_addr(i);
         input <= content_in(i);
         wait for Clk_period;

     -- check if the data has been written in the memory
         en_write <= '0';
         en_read <= '1';
         addr2 <= random_addr(i);
         wait for Clk_period;
     end loop;

          -- check if read and write can happen at the same time
     en_write <= '1';
     en_read <= '1';
     for i in random_addr'range loop
         addr1 <= random_addr(i);
         input <= content_test_in(i);
         addr2 <= random_addr(i);
         wait for Clk_period;
         -- check that the data which is read is the previous one
     end loop;

    -- now the data which is read should be the new one
     en_write <= '0';
     en_read <= '1';
     for i in random_addr'range loop
         addr2 <= random_addr(i);
         wait for Clk_period;
     end loop;

      wait;
   end process;

END;
