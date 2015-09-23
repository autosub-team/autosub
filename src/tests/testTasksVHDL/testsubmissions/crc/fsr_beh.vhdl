library IEEE;
use IEEE.std_logic_1164.all;

architecture behavior of fsr  is

    constant gen_degree : integer := 8;
    
begin

process(EN,RST,CLK)
   constant top_bit: integer := gen_degree-1;
   variable content: std_logic_vector(gen_degree-1 downto 0);
   variable do_inv: std_logic;
begin
    if(EN='1') then
        if(RST='1') then
            content:= (others=>'0'); 
        elsif(rising_edge(CLK)) then
           do_inv:= content(top_bit) xor DATA_IN;

           content(7) := content(6);
           content(6) := content(5) xor do_inv;
           content(5) := content(4);
           content(4) := content(3);
           content(3) := content(2);
           content(2) := content(1);
           content(1) := content(0) xor do_inv;
           content(0) := do_inv;
   
        end if;
        
        DATA <= content;
    end if;
end process;
    
end behavior; 
