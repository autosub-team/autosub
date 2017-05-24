-------------------------------------------------
-- BASIC TESTBENCH FOR THE TASK PWM 
-- AUTHOR: Martin Mosbeck
-------------------------------------------------

library IEEE;
use IEEE.std_logic_1164.all;

entity pwm_tb is
end pwm_tb;

architecture behavior of pwm_tb is
    component pwm
         port(  CLK     : in    std_logic;
                O       : out   std_logic);
    end component;


    constant clk_period : time := 20 ns; -- for 50MHz -> 20 ns

    ---------------------------------------------------
    --------------- CONNECTING SIGNALS ----------------
    --------------------------------------------------- 
    signal CLK_UUT, O_UUT :std_logic;
 
begin

    ---------------------------------------------------
    ------------ UNIT UNDER TEST CREATION -------------
    ---------------------------------------------------
    UUT: pwm
        port map
        (
            CLK=>CLK_UUT,
            O=>O_UUT
        );

    ---------------------------------------------------
    --------------- CLOCK STIMULATION -----------------
    ---------------------------------------------------

    --generates the global clock cycles 
    clk_generator : process

    begin
        CLK_UUT <= '0';
        wait for clk_period/2;  
        CLK_UUT <= '1';
        wait for clk_period/2; 
    end process;


end behavior;
