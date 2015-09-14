-------------------------------------------------
-- BASIC TESTBENCH FOR THE TASK GATES 
-- AUTHOR: Martin Mosbeck
-------------------------------------------------

library IEEE;
use IEEE.std_logic_1164.all;


entity gates_tb is
end gates_tb;

architecture behavior of gates_tb is
    component gates
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

    UUT: gates
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
        wait ;
       
    end process stimulate;
end behavior;
