-------------------------------------------------
-- BASIC TESTBENCH FOR THE TASK CRC
-- AUTHOR: Martin Mosbeck
-------------------------------------------------

library IEEE;
use IEEE.std_logic_1164.all;

entity crc_tb is
end crc_tb;

architecture behavior of crc_tb is
    component crc is
        port
        (
            NEW_MSG   : in std_logic;
            MSG       : in std_logic_vector(%%MSGLEN-1 downto 0);
            CLK       : in std_logic;
            CRC_VALID : out std_logic;
            CRC       : out std_logic_vector(%%CRCWIDTH-1 downto 0)
        );
    end component; 

    constant clk_period : time := 20 ns;  -- for 50MHz -> 20 ns   

    ---------------------------------------------------
    --------------- CONNECTING SIGNALS ----------------
    ---------------------------------------------------   
    signal NEW_MSG_UUT      : std_logic;
    signal MSG_UUT          : std_logic_vector(%%MSGLEN-1 downto 0);
    signal CLK_UUT          : std_logic;
    signal CRC_VALID_UUT    : std_logic;
    signal CRC_UUT          : std_logic_vector(%%CRCWIDTH-1 downto 0);

begin

    ---------------------------------------------------
    ------------ UNIT UNDER TEST CREATION -------------
    ---------------------------------------------------

    UUT: crc
        port map
        (
            NEW_MSG    => NEW_MSG_UUT,
            MSG        => MSG_UUT,
            CLK        => CLK_UUT,
            CRC_VALID  => CRC_VALID_UUT,
            CRC        => CRC_UUT
        );
 
    ---------------------------------------------------
    --------------- CLOCK GENERATION ------------------
    ---------------------------------------------------
    clk_generator : process
    begin
        CLK_UUT <= '0';
        wait for clk_period/2;
        CLK_UUT <= '1';
        wait for clk_period/2;
    end process;

    ---------------------------------------------------
    -------------- STIMULATION PROCESS ----------------
    ---------------------------------------------------

    stimulate :process
    begin
        -- Stimulation Example
        NEW_MSG_UUT<='0';
        wait until rising_edge(CLK_UUT);
        MSG_UUT<="%%MSG_EXAMPLE";
        NEW_MSG_UUT<='1';
        wait until rising_edge(CLK_UUT);
        NEW_MSG_UUT <= '0';
        
        wait for 10 ns;

    end process stimulate;  
end behavior;
