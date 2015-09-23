library IEEE;
use IEEE.std_logic_1164.all;

entity crc is
    port
    (   
        NEW_MSG     : in    std_logic; -- rising_edge indicates a message at port MSG, for which the CRC has to be calculated
        MSG         : in    std_logic_vector(21-1 downto 0);
        CLK         : in    std_logic; --clock square wave signal
        CRC_VALID   : out   std_logic; --set to 1 to indicate the CRC calculation is finished and the CRC to MSG is set at port CRC
        CRC         : out   std_logic_vector(8-1 downto 0)
    );
end crc;               
