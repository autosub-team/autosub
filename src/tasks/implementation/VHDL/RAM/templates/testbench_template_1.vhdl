LIBRARY IEEE;
USE IEEE.std_logic_1164.ALL;
USE IEEE.numeric_std.ALL;
use IEEE.STD_LOGIC_UNSIGNED.ALL; 


entity RAM_tb is
end RAM_tb;
architecture Behavioral of RAM_tb is
    component RAM port(Clk : in std_logic;
                       addr1 : in std_logic_vector(%%ADDRLENGTH  downto 0); --address
                       addr2 : in std_logic_vector(%%ADDRLENGTH  downto 0); --address
                       en_read : in std_logic; -- read-enable
                       en_write1 : in std_logic; -- write-enable
                       en_write2 : in std_logic; -- write-enable    
                       input1 : in std_logic_vector(%%WRITELENGTH downto 0);  --input
                       input2 : in std_logic_vector(%%WRITELENGTH downto 0);  --input 
                       output : out std_logic_vector(%%READLENGTH downto 0));  --output
    end component;

    signal Clk : std_logic := '0'; --clock signal
    signal addr1 : std_logic_vector(%%ADDRLENGTH  downto 0) := (others => '0'); --address
    signal addr2 : std_logic_vector(%%ADDRLENGTH  downto 0) := (others => '0'); --address
    signal en_read : std_logic := '0'; -- read-enable    
    signal en_write1 : std_logic := '0'; -- write-enable
    signal en_write2 : std_logic := '0'; -- write-enable    
    signal input1 : std_logic_vector(%%WRITELENGTH downto 0) := (others => '0');  --input
    signal input2 : std_logic_vector(%%WRITELENGTH downto 0) := (others => '0');  --input 
    signal output : std_logic_vector(%%READLENGTH downto 0) := (others => '0');  --output      
    constant Clk_period : time := 10 ns;

begin
  -- Instantiate the Unit Under Test (UUT)
 UUT: RAM port map (
        Clk => Clk, 
        addr1 => addr1, 
        addr2 => addr2,
        en_read => en_read,
        en_write1 => en_write1,
        en_write2 => en_write2,
        input1 => input1,
        input2 => input2,
        output => output
        );

   -- Clock process definitions
   Clk_process :process
   begin
        Clk <= '0';
        wait for Clk_period/2;
        Clk <= '1';
        wait for Clk_period/2;
   end process;
  
 stim_proc: process

        constant no_reading : std_logic_vector(%%READLENGTH downto 0) := (others => 'Z');
   
        type random_array is array (0 to 15) of std_logic_vector(%%ADDRLENGTH downto 0);
        constant random_addr : random_array :=(
                            %%RANDOM_ADDR);
  
        type content_array_in is array (0 to 15) of std_logic_vector(%%WRITELENGTH downto 0);
        constant content_in : content_array_in :=(
        					%%CONTENT_IN1);
        type content_array_out is array (0 to 15) of std_logic_vector(%%READLENGTH downto 0);
        constant content_out : content_array_out :=(
                                      %%CONTENT_OUT1);        					
        					
        constant content_test_in : content_array_in :=(
                                   %%CONTENT_IN2);        					
        constant content_test_out : content_array_out :=(
                                   %%CONTENT_OUT2); 
begin
      
    --------------------check the RAM------------------------
    --check the size of RAM
     en_write1 <= '1';
     en_read <= '0';
     en_write2 <= '0';
     if (%%WRITELENGTH+1)/(%%DATASIZE)=2 then
        addr1 <= std_logic_vector(to_unsigned((2**(%%ADDRLENGTH+1)-2),%%ADDRLENGTH+1)); 
     else
        addr1 <= std_logic_vector(to_unsigned((2**(%%ADDRLENGTH+1)-1),%%ADDRLENGTH+1));  
     end if;     input1 <= content_in(1);  
     wait for Clk_period;   
    
     -- the output should be "ZZZ.." when control signals are zero
    en_write1 <= '0';
    en_read <= '0';
    en_write2 <= '0';
    wait for Clk_period;
    if (output/=no_reading) then
       report " 'ZZ...' should be displayed on the output when nothing is read from the memory." severity failure;
    end if; 

     -- check en_write1 only
     en_write2 <= '0';
     for i in random_addr'range loop
        en_write1 <= '1';
        en_read <= '0';
        addr1 <= random_addr(i);   
        input1 <= content_in(i); 
        wait for Clk_period;
        if (output/=no_reading) then
            report " When en_read is not active, the output should be 'ZZ...'." severity failure;
        end if;          
        -- check if the data has been written in the memory
        en_write1 <= '0';
        en_read <= '1';
        addr1 <= random_addr(i);   
        wait for Clk_period;      
        if (output/=content_out(i)) then
            report " The data cannot be written to the memory correctly by en_write1, or the content of memory cannot be read." severity failure;
        end if;  
        -- check if higher significant half of input is not written to the memory correctly                 
        if (%%WRITELENGTH+1)/(%%READLENGTH+1)=2 then
            addr1 <= std_logic_vector(to_unsigned(conv_integer(random_addr(i))+1,%%ADDRLENGTH+1));
            wait for Clk_period;   
            if (output/=content_in(i)(%%WRITELENGTH downto %%READLENGTH+1)) then
                report " The more significant half of input is not written to the memory correctly, or the content of memory cannot be read." severity failure;
            end if;
        end if;
     end loop;
     
     -- check en_write2 only
     en_write1 <= '0';
     for i in random_addr'range loop
        en_write2 <= '1';
        en_read <= '0';
        addr2 <= random_addr(i);   
        input2 <= content_test_in(i); 
        wait for Clk_period; 
        if (output/=no_reading) then
            report " When en_read is not active, the output should be 'ZZ...'." severity failure;
        end if;            
        -- check if the data has been written in the memory
        en_read <= '1';
        en_write2 <= '0';
        addr1 <= random_addr(i);   
        wait for Clk_period; 
        if (output/=content_test_out(i)) then
            report " The data cannot be written to the memory correctly by en_write2, or the content of memory cannot be read." severity failure;
        end if;  
        -- check if higher significant half of input is not written in the memory correctly                 
        if (%%WRITELENGTH+1)/(%%READLENGTH+1)=2 then
            addr1 <= std_logic_vector(to_unsigned(conv_integer(random_addr(i))+1,%%ADDRLENGTH+1));
            wait for Clk_period;   
            if (output/=content_test_in(i)(%%WRITELENGTH downto %%READLENGTH+1)) then
                report " The more significant half of input is not written to the memory correctly, or the content of memory cannot be read." severity failure;
            end if;
        end if;  
     end loop;
  
     -- read and write1 should not be active at the same time 
     en_write2 <= '0';
     en_read <= '1';
     for i in random_addr'range loop
         en_write1 <= '1';
         addr1 <= random_addr(i);   
         input1 <= content_in(i); 
         wait for Clk_period;
         -- check that the data which is read is the previous one
         en_write1 <= '0';
         wait for Clk_period;
         if (output/=content_test_out(i)) then
            report " When en_read and en_write1 are active at the same time, nothing should happen to the memory." severity failure;
         end if;        
     end loop;

     -- it is not possible to have two write actions in the same address
     for i in random_addr'range loop
     	 en_write1 <= '1';
     	 en_write2 <= '1';
         en_read <= '0';
         addr1 <= random_addr(i);  
         addr2 <= random_addr(i);  
         input1 <= content_in(i); 
         input2 <= content_in(i);
         wait for Clk_period;
         if (output/=no_reading) then
            report " When en_read is not active, the output should be 'ZZ...'." severity failure;
         end if;             
         -- check that the data which is read is the previous one
         en_read <= '1';
     	    en_write1 <= '0';
     	    en_write2 <= '0';
         wait for Clk_period;
         if (output/=content_test_out(i)) then
            report " write 1 and write 2 should not happen to the same address at the same time." severity failure;
         end if;        
     end loop;
     
     -- check if both write lines work together correctly   
     for i in random_addr'range loop
         en_read <= '0';
         en_write2 <= '1';
         en_write1 <= '1';
         addr1 <= random_addr(i);  
         addr2 <= random_addr(15-i);  
         input1 <= content_in(i);
         input2 <= content_in(15-i); 
         wait for Clk_period;
         if (output/=no_reading) then
            report " When en_read is not active, the output should be 'ZZ...'." severity failure;
         end if;             
         -- check that the data which is read is the previous one
         en_read <= '1';
         en_write2 <= '0';
         en_write1 <= '0';
         addr1 <= random_addr(i); 
         wait for Clk_period;
         if (output/=content_out(i)) then
            report " There is a problem with writing in two different addresses at the same time." severity failure;
         end if;
        -- check if higher significant half of input is not written in the memory correctly                 
        if (%%WRITELENGTH+1)/(%%READLENGTH+1)=2 then
            addr1 <= std_logic_vector(to_unsigned(conv_integer(random_addr(i))+1,%%ADDRLENGTH+1));
            wait for Clk_period;   
            if (output/=content_in(i)(%%WRITELENGTH downto %%READLENGTH+1)) then
                report " The more significant half of input is not written in the memory correctly, or the content of memory cannot be read." severity failure;
            end if;
        end if;
                
         addr1 <= random_addr(15-i); 
         wait for Clk_period;
         if (output/=content_out(15-i)) then
            report " There is a problem with writing in two different addresses at the same time." severity failure;
         end if;  
        -- check if higher significant half of input is not written in the memory correctly                 
        if (%%WRITELENGTH+1)/(%%READLENGTH+1)=2 then
            addr1 <= std_logic_vector(to_unsigned(conv_integer(random_addr(15-i))+1,%%ADDRLENGTH+1));
            wait for Clk_period;   
            if (output/=content_in(15-i)(%%WRITELENGTH downto %%READLENGTH+1)) then
                report " The more significant half of input is not written in the memory correctly, or the content of memory cannot be read." severity failure;
            end if;
        end if;     
     end loop;

     -- it is not possible to have write2 and read actions in the same address
     for i in random_addr'range loop
     	 en_write1 <= '0';
     	 en_write2 <= '1';
         en_read <= '1';
         addr1 <= random_addr(i);  
         addr2 <= random_addr(i);  
         input2 <= content_test_in(i);
         wait for Clk_period;
         -- check that the data which is read is the previous one
         if (output/=no_reading) then
            report " Reading and second writing operations should not happen to the same address at the same time. If so, the output should be 'ZZ...'." severity failure;
         end if;        
     end loop;
      
     -- check if both write2 and read work together correctly   
     en_write1 <= '0';
     en_read <= '1';
     en_write2 <= '1';
     
     addr2 <= random_addr(0);  
     input2 <= content_test_in(0);
     wait for Clk_period;
     
     for i in 1 to 15 loop

         addr1 <= random_addr(i-1);  
         addr2 <= random_addr(i);  
         input2 <= content_test_in(i);
         wait for Clk_period;
         -- check that the data which is read is the previous one
         if (output/=content_test_out(i-1)) then
            report " There is a problem with reading and second writing operations together on two different addresses at the same time." severity failure;
         end if; 
        -- check if higher significant half of input is not written in the memory correctly                 
        if (%%WRITELENGTH+1)/(%%READLENGTH+1)=2 then
            addr1 <= std_logic_vector(to_unsigned(conv_integer(random_addr(i-1))+1,%%ADDRLENGTH+1));
            wait for Clk_period;   
            if (output/=content_test_in(i-1)(%%WRITELENGTH downto %%READLENGTH+1)) then
                report " The more significant half of input is not written to the memory correctly, or the content of memory cannot be read." severity failure;
            end if;
        end if;   
     end loop;
    
     report "Success" severity failure;  
    
   end process;

end Behavioral;