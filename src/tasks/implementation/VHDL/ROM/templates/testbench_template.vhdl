
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
USE ieee.numeric_std.all;

entity ROM_tb is
end ROM_tb;

architecture Behavioral of ROM_tb is
    component ROM port(Clk,enable : in std_logic;
     		addr : in std_logic_vector(%%ADDRLENGTH  downto 0);
     		output : out std_logic_vector(%%INSTRUCTIONLENGTH downto 0));
    end component;


    signal Clk,enable : std_logic := '0'; --clock signal and enable
    signal addr : std_logic_vector(%%ADDRLENGTH  downto 0) := (others => '0'); --address
    signal output : std_logic_vector(%%INSTRUCTIONLENGTH downto 0) := (others => '0');  --output of ROM
    constant Clk_period : time := 10 ns;

begin
  -- Instantiate the Unit Under Test (UUT)
 UUT: ROM port map (
        Clk => Clk, enable => enable, addr => addr, output => output);

   -- Clock process definitions
   Clk_process :process
   begin
        Clk <= '0';
        wait for Clk_period/2;
        Clk <= '1';
        wait for Clk_period/2;
   end process;
  
 stim_proc: process  
        
        variable err : std_logic := '0';
        variable zero_out : std_logic_vector(%%INSTRUCTIONLENGTH downto 0) := (others => '0');     
        variable zero_addr : std_logic_vector(%%ADDRLENGTH downto 0) := (others => '0');     

        type random_array is array (0 to %%DATALENGTH) of integer;
        constant random : random_array :=(
                                    %%RANDOM);
  
        type content_array is array (0 to %%DATALENGTH) of std_logic_vector(%%INSTRUCTIONLENGTH downto 0);
        constant content : content_array :=(
        					%%INSTRUCTIONS);

begin

      -----------------check enable-----------------------
      --When ROM is disabled and the input changes on the falling edge, 
      --the output should not change on the next rising edge.
         enable <= '0';        
         for i in random'range loop
             addr <= std_logic_vector(to_unsigned(random(i),%%ADDRESSLENGTH)); 
             wait for Clk_period/0.9;
             if (output = content(random(i)-%%START)) then
                 err := '1';
             end if;             
         end loop; 
         if err='1' then 
           report " Probably you did not use the enable signal correctly, or there is a problem with using signals and variables." severity failure;
         end if;
         err := '0';   

    --------------------check clock cycle------------------------
    --When ROM is enabled and the input changes on the falling edge, 
    --the output should not change.
    
    enable <= '1';  
        addr <= zero_addr;
        wait until %%CLK(Clk);
        
        if content(random(1)-%%START)/=zero_out then      
            addr <= std_logic_vector(to_unsigned(random(0),%%ADDRESSLENGTH));  
        else
            addr <= std_logic_vector(to_unsigned(random(1),%%ADDRESSLENGTH)); 
        end if; 
        
        wait until %%OPPOSITECLK(Clk); 
        wait for Clk_period/10;
        if (output /= zero_out) then
	       err :='1';
        end if;
   
      if err='1' then 
         report " Probably ROM is not operating on the right edge of clock cycle, or there is a problem with using signals and variables." severity failure;
      end if;
      err :='0';
      
      --------------------check the ROM------------------------
    enable <= '1';
    
     for i in random'range loop
         addr <= std_logic_vector(to_unsigned(random(i),%%ADDRESSLENGTH));     
         wait for Clk_period;
             if (output/=content(random(i)-%%START)) then
                 err := '1';
             end if;
     end loop;
     
     for i in 0 to 10 loop
         addr <= std_logic_vector(to_unsigned(i,%%ADDRESSLENGTH));
        wait for Clk_period;
         if (output/=zero_out) then
             err := '1';
         end if;
     end loop;
     
     for i in 2**%%ADDRESSLENGTH-10 to 2**%%ADDRESSLENGTH-1 loop
         addr <= std_logic_vector(to_unsigned(i,%%ADDRESSLENGTH));
        wait for Clk_period;
         if (output/=zero_out) then
          err := '1';
         end if;
     end loop;
     
    if (err = '1') then 
        report " ROM is not properly filled with the data specified in the description file." severity failure;       
    else
        report "Success" severity failure;  
    end if; 
    
   end process;

end Behavioral;