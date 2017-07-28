library IEEE;
use IEEE.STD_LOGIC_1164.all;
use IEEE.NUMERIC_STD.all;

entity register_file is
    port(
         IN1    : in  std_logic_vector((%%n - 1) downto 0);
         WA1    : in  std_logic_vector((%%address_width_n - 1) downto 0);
         WE1    : in  std_logic;
         
         IN2    : in  std_logic;
         WA2    : in  std_logic_vector((%%address_width_reg0 - 1) downto 0);
         WE2    : in  std_logic;
         
         RA1    : in  std_logic_vector((%%address_width_n - 1) downto 0);
         
         CLK    : in  std_logic;
         
         Output : out std_logic_vector((%%n - 1) downto 0)
         );
end register_file;