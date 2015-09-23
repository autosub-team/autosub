library IEEE;
use IEEE.std_logic_1164.all;

architecture behavior of pwm is
signal clk_cnt: natural := 0;

constant period :integer := 2500;
constant duty : integer := 1400;

begin

    clk_count : process(CLK)
    begin
        if(rising_edge(CLK)) then
            if(clk_cnt = period) then
               clk_cnt <= 1;
            else
               clk_cnt <= clk_cnt + 1;
            end if;
        end if;  
    end process;    

    siggen: process(clk_cnt) 
    begin
        if(clk_cnt = duty) then
            O <= '0';
        elsif(clk_cnt = period) then
            O <= '1';
        end if;
   end process;
       

end behavior;
