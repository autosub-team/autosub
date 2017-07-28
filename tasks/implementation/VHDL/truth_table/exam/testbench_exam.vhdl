-------------------------------------------------
-- BASIC TESTBENCH FOR THE TASK TRUTH_TABLE 
-- AUTHOR: Martin Mosbeck
-------------------------------------------------

library IEEE;
use IEEE.std_logic_1164.all;


entity truth_table_tb is
end truth_table_tb;

architecture behavior of truth_table_tb is
    component truth_table
         port(  A,B,C,D : in    std_logic;
                O       : out   std_logic);
    end component;
   
    ---------------------------------------------------
    --------------- CONNECTING SIGNALS ----------------
    --------------------------------------------------- 
    signal A_UUT,B_UUT,C_UUT,D_UUT,O_UUT : std_logic;

begin

    ---------------------------------------------------
    ------------ UNIT UNDER TEST CREATION -------------
    ---------------------------------------------------
    UUT: truth_table 
        port map(
                     A=>A_UUT,
                     B=>B_UUT,
                     C=>C_UUT,
                     D=>D_UUT,
                     O=>O_UUT
                );

    ---------------------------------------------------
    -------------- STIMULATION PROCESS ----------------
    ---------------------------------------------------
    stimulate:process

    begin
    -- Stimulation Example     
        A_UUT<='0';
        B_UUT<='1';
        C_UUT<='1';
        D_UUT<='0';

    -- Wait for Results
        wait for 10 ns;
       
    end process stimulate;
end behavior;
