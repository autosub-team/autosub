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
	    variable U_out : std_logic_vector(%%INSTRUCTIONLENGTH downto 0) := (others => 'U'); 
	    --non-zero content findig
	    variable count: integer :=0;
	    type con_array is array (0 to 1) of std_logic_vector(%%INSTRUCTIONLENGTH downto 0);
        variable content_clk_check : con_array;
	    type addr_array is array (0 to 1) of integer;
        variable addr_clk_check : addr_array;
        variable out_1,out_2,out_3 : std_logic_vector(%%INSTRUCTIONLENGTH downto 0);
                                    
           --to_string function for report
           function to_string ( a: std_logic_vector) return string is
                    variable b : string (a'length downto 1) := (others => '0');
            begin
                    for i in a'length downto 1 loop
                    b(i) := std_logic'image(a((i-1)))(2);
                    end loop;
                return b;
            end function;        
        
        type random_array is array (0 to %%DATALENGTH) of integer;
        constant random : random_array :=(
                                    %%RANDOM);
  
        type content_array is array (0 to %%DATALENGTH) of std_logic_vector(%%INSTRUCTIONLENGTH downto 0);
        constant content : content_array :=(
        					%%INSTRUCTIONS);

begin

      --------------------check the ROM------------------------
    enable <= '1';
    
     for i in random'range loop
         addr <= std_logic_vector(to_unsigned(random(i),%%ADDRESSLENGTH));     
         wait for Clk_period*2;
             if (output/=content(random(i)-%%START) and output/=U_out) then
	      report " ROM is not properly filled with the data specified in the description file: " &
                     "In address " & to_string(std_logic_vector(to_unsigned(random(i),%%ADDRESSLENGTH))) & 
                     ", the expected content is " & to_string(content(random(i)-%%START)) &
                     ". But the received output is " & to_string(output) & "." 
                     severity failure;
             elsif (output/=content(random(i)-%%START) and output=U_out) then
                     report " Output is '" &  to_string(std_logic_vector(U_out)) & 
                    "'. Probably, you have not correctly assigned or used the output signal 'output' or other variables." severity failure;
             end if;
     end loop;
     
      for i in %%START+%%DATALENGTH+1 to 2**%%ADDRESSLENGTH-1 loop
         addr <= std_logic_vector(to_unsigned(i,%%ADDRESSLENGTH));
        wait for Clk_period*2;
         if (output/=zero_out) then
 	      report " ROM is not properly filled with the data specified in the description file: " &
                     "In address " & to_string(std_logic_vector(to_unsigned(i,%%ADDRESSLENGTH))) & 
                     ", the expected content is zero. But the received output is " & to_string(output) & "." 
                     severity failure;
         end if;
      end loop;
        
     
     for i in 0 to %%START-1 loop
         addr <= std_logic_vector(to_unsigned(i,%%ADDRESSLENGTH));
        wait for Clk_period*2;
         if (output/=zero_out) then
	      report " ROM is not properly filled with the data specified in the description file: " &
                     "In address " & to_string(std_logic_vector(to_unsigned(i,%%ADDRESSLENGTH))) & 
                     ", the expected content is zero. But the received output is " & to_string(output) & "."  
                     severity failure;
         end if;
     end loop;
     
     
    -------------------- clock cycle check------------------------
    --When ROM is enabled and the input changes on the falling edge, 
    --the output should not change.
    
    -- to find two non-zero content
    
    for i in random'range loop
        if (content(random(i)-%%START)/=zero_out and count<2) then
            if (count=1 and content_clk_check(0)/=content(random(i)-%%START)) then
                addr_clk_check(count):=random(i);
                content_clk_check(count):=content(random(i)-%%START);
            end if;
            if count=0 then
                addr_clk_check(count):=random(i);
                content_clk_check(count):=content(random(i)-%%START);
            end if;
            count:=count+1;
        end if;
    end loop;
    
    
    --Check if wrong edge is used
    enable <= '1'; 
    wait until %%OPPOSITECLK(Clk); 
    wait for Clk_period/10;
    addr <= std_logic_vector(to_unsigned(addr_clk_check(0),%%ADDRESSLENGTH)); 
    wait until %%CLK(Clk); 
    wait for Clk_period/10;
    out_1 := output;
    
    wait until %%OPPOSITECLK(Clk); 
    wait for Clk_period/10;
    
    out_2 := output;
    
    if (out_1 /= out_2) then 
        report " The output is changing on %%oppositeClk of the clock signal, but it should not." severity failure;
    end if;
    
    --Check the right edge is used
    wait until %%CLK(Clk); 
    wait for Clk_period/10; 
    addr <= std_logic_vector(to_unsigned(addr_clk_check(1),%%ADDRESSLENGTH)); 
    wait until %%OPPOSITECLK(Clk); 
    wait for Clk_period/10;  
    out_1 := output;  
    wait until %%CLK(Clk); 
    wait for Clk_period/10;
    out_3 := output;  
    if (out_1 = content_clk_check(1) or out_3 /= content_clk_check(1)) then 
        report " Your output does not change on the first %%mainClk after a new address was set on the input 'addr'." severity failure;
    end if; 
    
    ----------------- enable check-----------------------
      --When ROM is disabled and the input changes on the falling edge, 
      --the output should not change on the next rising edge.
         enable <= '0';        
         for i in random'range loop
             addr <= std_logic_vector(to_unsigned(random(i),%%ADDRESSLENGTH)); 
             wait for Clk_period/0.9;
	    if (output = content(random(i)-%%START)) then
		report " The output is not zero when the enable signal is not active." severity failure;
	    elsif (output = U_out) then
		report " Output is '" &  to_string(std_logic_vector(U_out)) & 
		"'. Probably, you have not correctly assigned the output signal 'output' or enable signal." severity failure;
	    end if;             
	end loop;
     
     report "Success" severity failure;  
 
    
   end process;

end Behavioral;