library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity demux is
    port ( IN1  : in  std_logic_vector(({{IN1_width}} - 1) downto 0);
           SEL  : in  std_logic_vector(({{SEL_width}} - 1) downto 0);
{{outputs_entity}}
end demux;
