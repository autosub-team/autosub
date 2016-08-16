LIBRARY IEEE;
USE IEEE.std_logic_1164.ALL;
USE IEEE.numeric_std.ALL;

entity RAM_tb is
end RAM_tb;

architecture Behavioral of RAM_tb is
    component RAM port(Clk : in std_logic;
                       addr1 : in std_logic_vector(%%ADDRLENGTH  downto 0); --address
                       addr2 : in std_logic_vector(%%ADDRLENGTH  downto 0); --address
                       en_read1 : in std_logic; -- read-enable
                       en_read2 : in std_logic; -- read-enable
                       en_write : in std_logic; -- write-enable    
                       input : in std_logic_vector(%%WRITELENGTH downto 0);  --input
                       output1 : out  std_logic_vector(%%READLENGTH downto 0);  --output 
                       output2 : out std_logic_vector(%%READLENGTH downto 0));  --output
    end component;

    signal Clk : std_logic := '0'; --clock signal
    signal addr1 : std_logic_vector(%%ADDRLENGTH  downto 0) := (others => '0'); --address
    signal addr2 : std_logic_vector(%%ADDRLENGTH  downto 0) := (others => '0'); --address
    signal en_read1 : std_logic := '0'; -- read-enable    
    signal en_read2 : std_logic := '0'; -- read-enable
    signal en_write : std_logic := '0'; -- write-enable    
    signal input : std_logic_vector(%%WRITELENGTH downto 0) := (others => '0');  --input
    signal output1 : std_logic_vector(%%READLENGTH downto 0) := (others => '0');  --output 
    signal output2 : std_logic_vector(%%READLENGTH downto 0) := (others => '0');  --output   
    constant Clk_period : time := 10 ns;

begin
  -- Instantiate the Unit Under Test (UUT)
 UUT: RAM port map (
        Clk => Clk, 
        addr1 => addr1, 
        addr2 => addr2,
        en_read1 => en_read1,
        en_read2 => en_read2,
        en_write => en_write,
        input => input,
        output1 => output1,
        output2 => output2
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
      
    --------------------check the ROM------------------------
     -- the output should be "ZZZ.." when control signals are zero
     en_read2 <= '0';
     wait for Clk_period;
     if (output2/=no_reading) then
        report " 'ZZ...' should be displayed on the output when nothing is read from the memory." severity failure;
     end if; 
     en_read1 <= '0';
     wait for Clk_period;
     if (output1/=no_reading) then
        report " 'ZZ...' should be displayed on the output when nothing is read from the memory." severity failure;
     end if;   
    
    --check the size of RAM
     en_write <= '1';
     en_read1 <= '0';
     en_read2 <= '0';
     if (%%WRITELENGTH+1)/(%%DATASIZE)=2 then
        addr1 <= std_logic_vector(to_unsigned((2**(%%ADDRLENGTH+1)-2),%%ADDRLENGTH+1)); 
     else
        addr1 <= std_logic_vector(to_unsigned((2**(%%ADDRLENGTH+1)-1),%%ADDRLENGTH+1));  
     end if;     input <= content_in(1);  
     wait for Clk_period;
     
     -- check both read lines
     for i in random_addr'range loop
        en_write <= '1';
        en_read1 <= '0';
        en_read2 <= '0';
        addr1 <= random_addr(i);   
        input <= content_in(i); 
        wait for Clk_period; 
        if (output1/=no_reading and output2/=no_reading) then
            report " When en_read are not active, the outputs should be 'ZZ...'." severity failure;
        end if;          
        -- check if en_write and en_read1 are working correctly
        en_write <= '0';
        en_read1 <= '1';
        en_read2 <= '0';
        addr1 <= random_addr(i);   
        wait for Clk_period;      
        if (output1/=content_out(i)) then
            report " The data cannot be written to the memory correctly, or the content of memory cannot be read when en_read1 is active." severity failure;
        elsif (output2/=no_reading) then
            report " When second reading is not active, the output 2 should be 'ZZ...'." severity failure;
        end if;

        -- check if en_write and en_read2 are working correctly
        en_read1 <= '0';
        en_read2 <= '1';
        addr2 <= random_addr(i);   
        wait for Clk_period;      
        if (output2/=content_out(i)) then
            report " The data cannot be written to the memory correctly, or the content of memory cannot be read when en_read2 is active." severity failure;
        elsif (output1/=no_reading) then
                report " When first reading is not active, the output 1 should be 'ZZ...'." severity failure;        
        end if;            
     end loop;
     
     -- check if higher significant half of input is not written in the memory correctly
     en_read1 <= '0';
     en_write <= '0';
     en_read2 <= '1';
     for i in random_addr'range loop                  
        if (%%WRITELENGTH+1)/(%%READLENGTH+1)=2 then
            addr2 <= std_logic_vector(to_unsigned(to_integer(unsigned(random_addr(i)))+1, %%ADDRLENGTH+1));
            wait for Clk_period;   
            if (output2/=content_in(i)(%%WRITELENGTH downto %%READLENGTH+1)) then
                report " The higher significant half of input is not written to the memory correctly, or the content of memory cannot be read." severity failure;
            end if;        
        end if;
     end loop;
  
     -- read 1 and write should not be active at the same time
     en_read2 <= '0';
     for i in random_addr'range loop
         en_write <= '1';
         en_read1 <= '1';
         addr1 <= random_addr(i);   
         input <= content_test_in(i); 
         wait for Clk_period;
         -- check that the data which is read is the previous one
         en_write <= '0';
         wait for Clk_period;
         if (output1/=content_out(i)) then
            report " When en_read1 and en_write are active at the same time, nothing should happen to the memory." severity failure;
         end if;        
     end loop;

     -- check if both read lines work together correctly   
     for i in random_addr'range loop
         en_read1 <= '1';
         en_read2 <= '1';
         en_write <= '0';
         addr1 <= random_addr(i); 
         addr2 <= random_addr(15-i);
         wait for Clk_period;
         if (output1/=content_out(i)) then
            report " There is a problem with two reading processes from the memory at the same time. The first reading is not operating correctly." severity failure;
         elsif output2/=content_out(15-i) then
            report " There is a problem with two reading processes from the memory at the same time. The second reading is not operating correctly." severity failure;
         end if;       
     end loop;
     
     -- it is not possible both reading to and writing from the same address
     en_read1 <= '0';
     for i in random_addr'range loop
         en_read2 <= '1';
         en_write <= '1';
         addr1 <= random_addr(i);  
         addr2 <= random_addr(i);  
         input <= content_test_in(i); 
         wait for Clk_period;
         if (output1/=no_reading and output2/=no_reading) then
            report " When en_read are not active, the outputs should be 'ZZ...'." severity failure;
         end if;           
         -- check that the data which is read is the previous one
         en_read2 <= '1';
         en_write <= '0';
         wait for Clk_period;
         if (output2/=content_out(i)) then
            report " Writing and second reading operations should not happen to the same address at the same time. If it happens, the content should not change." severity failure;
         end if;        
     end loop;    
           
    -- check if both write and read2 work together correctly   
    en_read1 <= '0';
    en_read2 <= '1';
    en_write <= '1';
    
    addr1 <= random_addr(0);  
    input <= content_test_in(0);
    wait for Clk_period;
    
    for i in 1 to 15 loop

        addr2 <= random_addr(i-1);  
        addr1 <= random_addr(i);  
        input <= content_test_in(i);
        wait for Clk_period;
        -- check that the data which is read is the previous one
        if (output2/=content_test_out(i-1)) then
           report " There is a problem with writing and second reading operations together on two different addresses at the same time." severity failure;
        end if; 
        if (output1/=no_reading) then
            report " When en_read1 is not active, the output1 should be 'ZZ...'." severity failure;
        end if;         
    end loop;

     -- check if higher significant half of input is not written in the memory correctly
     en_read1 <= '0';
     en_write <= '0';
     en_read2 <= '1';
     for i in random_addr'range loop                  
        if (%%WRITELENGTH+1)/(%%READLENGTH+1)=2 then
            addr2 <= std_logic_vector(to_unsigned(to_integer(unsigned(random_addr(i)))+1, %%ADDRLENGTH+1));
            wait for Clk_period;   
            if (output2/=content_test_in(i)(%%WRITELENGTH downto %%READLENGTH+1)) then
                report " The higher significant half of input is not written to the memory correctly, or the content of memory cannot be read." severity failure;
            end if;        
        end if;
     end loop;
    
     report "Success" severity failure;  
    
   end process;

end Behavioral;