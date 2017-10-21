-------------------------------------------------
-- BASIC TESTBENCH FOR THE TASK ARITHMETIC
-- AUTHOR: Martin Mosbeck
-------------------------------------------------
library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

entity arithmetic_tb is
end arithmetic_tb;


architecture behavior of arithmetic_tb is

    constant I1_len:integer:= {{I1_WIDTH}};
    constant I2_len:integer:= {{I2_WIDTH}};
    constant O_len:integer:= {{O_WIDTH}};

    subtype I1_TYPE is std_logic_vector(I1_len-1 downto 0);
    subtype I2_TYPE is std_logic_vector(I2_len-1 downto 0);
    subtype O_TYPE  is std_logic_vector(O_len-1 downto 0); 


    component arithmetic
        port(  I1     :in    I1_TYPE;    -- Operand 1
               I2     :in    I2_TYPE;    -- Operand 2
               O      :out   O_TYPE;     -- Output
               C      :out   std_logic;  -- Carry Flag
               V      :out   std_logic;  -- Overflow Flag
               VALID  :out   std_logic); -- Flag to indicate if the solution is valid or not);
    end component;

    signal I1_UUT     :I1_TYPE;
    signal I2_UUT     :I2_TYPE;
    signal O_UUT      :O_TYPE;
    signal C_UUT      :std_logic;
    signal V_UUT      :std_logic;
    signal VALID_UUT  :std_logic;

begin
    ---------------------------------------------------
    ------------ UNIT UNDER TEST CREATION -------------
    ---------------------------------------------------
    UUT:arithmetic 
        port map
        (
            I1=>I1_UUT,
            I2=>I2_UUT,
            O=>O_UUT,
            C=>C_UUT,
            V=>V_UUT,
            VALID=>VALID_UUT
        );

    ---------------------------------------------------
    -------------- STIMULATION PROCESS ----------------
    --------------------------------------------------- 
    stimulate: process
     
    begin
        -- Stimulation Example

        -- Set the inputs   
        I1_UUT <= "{{I1_EXAMPLE}}";
        I2_UUT <= "{{I2_EXAMPLE}}";
        
        --Wait for the results.
        wait for 10 ns;
           
    end process stimulate;
end behavior;
