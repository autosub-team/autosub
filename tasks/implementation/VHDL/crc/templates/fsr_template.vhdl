library IEEE;
use IEEE.std_logic_1164.all;

entity fsr is
    port 
    (
        EN      : in std_logic;
        RST     : in std_logic; -- rising edge of RST should reset the content of the shift register to all 0
        CLK     : in std_logic; -- shift and feedback operations should be done on rising edge of CLK
        DATA_IN : in std_logic; -- the bit which shall be shifted in
        DATA    : out std_logic_vector(%%CRCWIDTH-1 downto 0) -- the current content  of the feedback shift register
    );
end fsr ;
