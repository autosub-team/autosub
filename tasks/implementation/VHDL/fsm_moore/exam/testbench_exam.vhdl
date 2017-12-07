-------------------------------------------------
-- BASIC TESTBENCH FOR THE TASK FSM_MOORE 
-------------------------------------------------

library IEEE;
use IEEE.std_logic_1164.all;
use work.fsm_pkg.all;

entity fsm_tb is
end fsm_tb;
   

architecture behavior of fsm_tb is
    component fsm
        port
        (   
            CLK     : in    std_logic;
            INPUT   : in    std_logic_vector(1 downto 0);
            RST     : in    std_logic;
            OUTPUT  : out   std_logic_vector(1 downto 0);
            STATE   : out   fsm_state
        );
    end component;

    constant clk_period : time := 20 us; -- for 50kHz -> 20 us
 
    ---------------------------------------------------
    --------------- CONNECTING SIGNALS ----------------
    --------------------------------------------------- 
    signal CLK_UUT: std_logic;
    signal INPUT_UUT: std_logic_vector(1 downto 0);
    signal RST_UUT: std_logic;
    signal OUTPUT_UUT: std_logic_vector(1 downto 0);
    signal STATE_UUT: fsm_state;
           
begin

    ---------------------------------------------------
    ------------ UNIT UNDER TEST CREATION -------------
    ---------------------------------------------------
    UUT: fsm
        port map
        (
            CLK    => CLK_UUT,
            RST    => RST_UUT,
            INPUT  => INPUT_UUT,
            OUTPUT => OUTPUT_UUT,
            STATE  => STATE_UUT 
        );
    
    ---------------------------------------------------
    ---------- STIMULATION & CLOCK PROCESS ------------
    ---------------------------------------------------
    stimulate:process
        
    begin          
        -- Stimulation for Reset
        CLK_UUT<='0';
        wait for clk_period/2;
        RST_UUT<='1';
        CLK_UUT<='1';
        wait for clk_period/2;
        RST_UUT<='0';
        
        -- Stimulation Example
        CLK_UUT<='0';
        INPUT_UUT <= "01"; -- change to a valid input here
        wait for clk_period/2;
        CLK_UUT<='1';
        wait for clk_period/2;
        CLK_UUT<='0';
        wait for clk_period/2;
        CLK_UUT<='1';

        wait for 10 ns;

    end process stimulate;

end behavior;
