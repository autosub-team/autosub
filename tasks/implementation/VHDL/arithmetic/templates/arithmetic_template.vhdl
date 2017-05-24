library IEEE;
use IEEE.std_logic_1164.all;

entity arithmetic is
    port(   I1     :in    std_logic_vector(%%I1_WIDTH-1 downto 0); -- Operand 1
            I2     :in    std_logic_vector(%%I2_WIDTH-1 downto 0); -- Operand 2
            O      :out   std_logic_vector(%%O_WIDTH-1  downto 0); -- Output
            C      :out   std_logic;                       -- Carry Flag
            V      :out   std_logic;                       -- Overflow Flag
            VALID  :out   std_logic                        -- Flag to indicate if the solution is valid or not
);
end arithmetic;               
