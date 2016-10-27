LIBRARY IEEE;
USE IEEE.std_logic_1164.ALL;
USE IEEE.numeric_std.ALL;


entity RAM_tb is
end RAM_tb;

architecture Behavioral of RAM_tb is
    component RAM port(Clk : in std_logic;
                       addr1 : in std_logic_vector(%%ADDRLENGTH downto 0); --address
                       addr2 : in std_logic_vector(%%ADDRLENGTH downto 0); --address
                       en_read1 : in std_logic; -- read-enable
                       en_read2 : in std_logic; -- read-enable
                       en_write1 : in std_logic; -- write-enable 
                       en_write2 : in std_logic; -- write-enable    
                       input1 : in std_logic_vector(%%WRITELENGTH downto 0);  --input
                       input2 : in std_logic_vector(%%WRITELENGTH downto 0);  --input
                       output1 : out  std_logic_vector(%%READLENGTH downto 0);  --output 
                       output2 : out std_logic_vector(%%READLENGTH downto 0));  --output
    end component;

    signal Clk : std_logic := '0'; --clock signal
    signal addr1 : std_logic_vector(%%ADDRLENGTH  downto 0) := (others => '0'); --address
    signal addr2 : std_logic_vector(%%ADDRLENGTH  downto 0) := (others => '0'); --address
    signal en_read1 : std_logic := '0'; -- read-enable    
    signal en_read2 : std_logic := '0'; -- read-enable
    signal en_write1 : std_logic := '0'; -- write-enable
    signal en_write2 : std_logic := '0'; -- write-enable     
    signal input1 : std_logic_vector(%%WRITELENGTH downto 0) := (others => '0');  --input
    signal input2 : std_logic_vector(%%WRITELENGTH downto 0) := (others => '0');  --input
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
        en_write1 => en_write1,
        en_write2 => en_write2,
        input1 => input1,
        input2 => input2,
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
        
        constant zero_out : std_logic_vector(%%READLENGTH downto 0) := (others => '0');
        constant Z_out : std_logic_vector(%%READLENGTH downto 0) := (others => 'Z');
        constant U_out : std_logic_vector(%%READLENGTH downto 0) := (others => 'U');
           --to_string function for report
           function to_string ( a: std_logic_vector) return string is
                    variable b : string (a'length downto 1) := (others => '0');
            begin
                    for i in a'length downto 1 loop
                    b(i) := std_logic'image(a((i-1)))(2);
                    end loop;
                return b;
            end function;   
            
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
     if (output2/=Z_out and output2/=U_out) then
        report " output2 should be high impedance (Z) when nothing is read from the memory using en_read2 operation." severity failure;
     elsif (output2/=Z_out and output2=U_out) then
        report " Probably, you did not assign or use the output signal 'output2' correctly." severity failure;
     end if; 
     
     en_read1 <= '0';
     wait for Clk_period;
     if (output1/=Z_out and output1/=U_out) then
        report " output1 should be high impedance (Z) when nothing is read from the memory using en_read1 operation" severity failure;
     elsif (output1/=Z_out and output1=U_out) then
           report " Probably, you did not assign or use the output signal 'output1' correctly." severity failure;
     end if;    
     
    --check the size of RAM
     en_write1 <= '1';
     en_read1 <= '0';
     en_write2 <= '0';
     en_read2 <= '0';
     if (%%WRITELENGTH+1)/(%%DATASIZE)=2 then
        addr1 <= std_logic_vector(to_unsigned((2**(%%ADDRLENGTH+1)-2),%%ADDRLENGTH+1)); 
     else
        addr1 <= std_logic_vector(to_unsigned((2**(%%ADDRLENGTH+1)-1),%%ADDRLENGTH+1));  
     end if;     input1 <= content_in(1);  
     wait for Clk_period;
     
     -- check all read and write lines
     
     -- check if en_write1 and en_read1 are working correctly
     ------------------------------------------------------- 
     for i in random_addr'range loop
        en_write1 <= '1';
        en_write2 <= '0';
        en_read1 <= '0';
        en_read2 <= '0';
        addr1 <= random_addr(i);   
        addr2 <= random_addr(15-i); 
        input1 <= content_in(i); 
        input2 <= content_test_in(15-i);
        wait for Clk_period; 
        if (output1/=Z_out or output2/=Z_out) then
            report " In your code, the outputs are not high impedance (Z) when only en_write1 is enabled." severity failure;
        end if; 
        
        --check en_write2 should not work when en_write1 is only active
        
        en_write1 <= '0';
        en_read1 <= '1';
        addr1 <= random_addr(15-i); 
        wait for Clk_period;
        --the output2 is high impedance when read1 is only active
        if (output2/=Z_out) then
            report " In your code, output2 is not high impedance (Z) when only en_read1 is enabled." severity failure;
        end if; 
                 
        if (output1=content_test_out(15-i) and content_test_out(15-i)/=content_out(15-i) and content_test_out(15-i)/=zero_out) then
            report " In your code, the data is written to address addr2 of the RAM when only en_write1 is enabled." severity failure;
        end if;
                
        ---check write2 is not operating when only write1 is active
        
        en_read1 <= '1';
        addr1 <= random_addr(i); 
        addr2 <= random_addr(15-i); 
        input1 <= content_test_in(15-i); 
        input2 <= content_test_in(15-i);  
        wait for Clk_period;   
                   
            --the output2 is high impedance when read1 is only active
            if (output2/=Z_out) then
                report " In your code, output2 is not high impedance (Z) when only en_read1 is enabled." severity failure;
            end if;  
            
            --check non of writing happen to the memory
            en_read1 <= '1';
            addr1 <= random_addr(i); 
            wait for Clk_period;     
            if (output1=content_test_out(15-i) and content_test_out(15-i)/=content_out(i)  and content_test_out(15-i)/=zero_out) then
                report " The data is written to address addr1 of the RAM when only en_read1 is enabled." severity failure;
            end if;  
            
            --check non of writing happen to the memory
            en_read1 <= '1';
            addr1 <= random_addr(15-i); 
            wait for Clk_period;     
            if (output1=content_test_out(15-i) and content_test_out(15-i)/=content_out(15-i) and content_test_out(15-i)/=zero_out) then
                report " The data is written to address addr2 of the RAM when only en_read1 is enabled." severity failure;
            end if;    
        
            -- check if the date is written to the memory by en_write1
            en_write1 <= '0';
            en_read1 <= '1';
            addr1 <= random_addr(i);   
            wait for Clk_period;     
            if (output1/=content_out(i)) then
                report " The data cannot be written to the memory correctly when en_write1 is enabled, or the content of memory cannot be read when en_read1 is enabled." severity failure;
            end if;
        
        
        -- check if most significant half of input is not written to the memory correctly                 
        if (%%WRITELENGTH+1)/(%%DATASIZE)=2 then        
         if (%%READLENGTH+1)/(%%DATASIZE)=2 then
             addr1 <= std_logic_vector(to_unsigned(to_integer(unsigned(random_addr(i)))+1, %%ADDRLENGTH+1));
             wait for Clk_period; 
             if (output1(%%DATASIZE-1 downto 0)/=content_in(i)(%%WRITELENGTH downto %%DATASIZE)) then
                 report " The upper half of input1 is not written to the memory correctly when en_write1 is only enabled. Note that the length of input is twice the length of each memory cell." severity failure;
             end if;              
         end if;
                 
        if (%%READLENGTH+1)/(%%DATASIZE)=1 then
            addr1 <= std_logic_vector(to_unsigned(to_integer(unsigned(random_addr(i)))+1, %%ADDRLENGTH+1));
            wait for Clk_period;   
            if (output1/=content_in(i)(%%WRITELENGTH downto %%READLENGTH+1)) then
                report " The upper half of input1 is not written to the memory correctly when en_write1 is only enabled." severity failure;
            end if;
        end if;
        end if;

    end loop;                                                 
        
        -- check if en_write2 and en_read2 are working correctly
        -------------------------------------------------------
        en_write1 <= '0';
        en_read1 <= '0'; 
    for i in 0 to 7 loop
        en_write2 <= '1';
        en_read2 <= '0';
        addr1 <= random_addr(15-i); 
        addr2 <= random_addr(i);  
        input1 <= content_in(i);
        input2 <= content_test_in(i);  
        wait for Clk_period; 
        if (output1/=Z_out or output2/=Z_out) then
            report " In your code, the outputs are not high impedance (Z) only en_write2 is enabled." severity failure;
        end if;  
        
         --check en_write1 should not work when en_write2 is only active
        en_write2 <= '0';
        en_read1 <= '1';
        addr2 <= random_addr(15-i); 
        wait for Clk_period;         
        if (output1=content_out(i) and content_out(i)/=content_out(15-i)) then
            report " In your code, the data is written to address addr1 of the RAM when only en_write2 is enabled." severity failure;
        end if;
                       
        ---check write1 is not operating when only write2 is active
        
        -- to make the output1 be different from high impedance
        en_write2 <= '0';
        en_read2 <= '0';
        en_read1 <= '1';
        wait for Clk_period;
        en_read1 <= '0';
        -----
        en_read2 <= '1';
        addr1 <= random_addr(8+i); 
        addr2 <= random_addr(15-i); 
        input1 <= content_in(15-i); 
        input2 <= content_in(i);  
        wait for Clk_period; 
        
            --the output1 is high impedance when read2 is only active
            if (output1/=Z_out) then
                report " In your code, output1 is not high impedance (Z) when only en_read2 is enabled." severity failure;
            end if;  
       
         --check non of writing happen to the memory
        en_read1 <= '1';
        en_read2 <= '0';
        addr1 <= random_addr(8+i); 
        wait for Clk_period;   
        if (output2/=Z_out) then
	    report " In your code, output2 is not high impedance (Z) only en_read1 is enabled." severity failure;
	end if;  
        if (output1=content_out(15-i) and content_out(15-i)/=content_out(i+8)) then
            report " The data is written to address addr1 of the RAM when only en_read2 is enabled." severity failure;
        end if;

        addr1 <= random_addr(15-i); 
        wait for Clk_period;     
        if (output1=content_out(i) and content_out(i)/=content_in(15-i)) then
            report " The data is written to address addr2 of the RAM when only en_read2 is enabled." severity failure;
        end if;
        en_read1 <= '0';        
            -- check if en_write and en_read1 are working correctly
            en_write2 <= '0';
            en_read2 <= '1';
            addr2 <= random_addr(i);   
            wait for Clk_period;      
            if (output2/=content_test_out(i)) then
                report " The data cannot be written to the memory correctly when en_write2 is enabled, or the content of memory cannot be read when en_read2 is enabled." severity failure;
            end if;  
            
        -- check if most significant half of input is not written to the memory correctly  
        if (%%WRITELENGTH+1)/(%%DATASIZE)=2 then  
        if (%%READLENGTH+1)/(%%DATASIZE)=1 then
            addr2 <= std_logic_vector(to_unsigned(to_integer(unsigned(random_addr(i)))+1, %%ADDRLENGTH+1));
            wait for Clk_period;   
            if (output2/=content_test_in(i)(%%WRITELENGTH downto %%READLENGTH+1)) then
                report " The upper half of input2 is not written to the memory correctly when en_write2 is only enabled." severity failure;
            end if;
        end if;
       end if;
              
     end loop;    
    for i in 8 to 15 loop
         en_write2 <= '1';
         en_read2 <= '0';
         addr2 <= random_addr(i);  
         input2 <= content_test_in(i);  
         wait for Clk_period;          
  end loop;
  
     -- read1 and write1 should not be active at the same time
     --------------------------------------------------------
     en_write2 <= '0';
     en_read2 <= '0';
     for i in random_addr'range loop
         en_write1 <= '1';
         en_read1 <= '1';
         addr1 <= random_addr(i);    
         input1 <= content_in(i); 
         wait for Clk_period;
                  
        if (output1/=Z_out and output2/=Z_out) then
            report " In your code, the outputs are not high impedance (Z) when only en_write1 and en_read1 are both enabled." severity failure;
         end if; 
         -- check that the data which is read is the previous one
         en_write1 <= '0';
         
         wait for Clk_period;
         if (output1/=content_test_out(i)) then
            report " In your code, input1 is written to the memory when en_write1 and en_read1 are both enabled." severity failure;
         end if;         
     end loop;
     
     -- read2 and write2 should not be active at the same time
     --------------------------------------------------------
     en_write1 <= '0';
     en_read1 <= '0';
     for i in random_addr'range loop
         en_read2 <= '1';
         en_write2 <= '1';
         addr2 <= random_addr(i);   
         input2 <= content_in(i); 
         wait for Clk_period;
         
         if (output1/=Z_out and output2/=Z_out) then
            report " In your code, the outputs are not high impedance (Z) when only en_write2 and en_read2 are both enabled." severity failure;
         end if;          
         -- check that the data which is read is the previous one
         en_write2 <= '0';
         
         wait for Clk_period; 
         if (output2/=content_test_out(i)) then
            report " In your code, input2 is written to the memory when en_write2 and en_read2 are both enabled." severity failure;
         end if;       
     end loop;    

     -- it is not possible both reading to and writing from the same address
     -----------------------------------------------------------------------
     en_read1 <= '0';
     en_write2 <= '0';
     for i in 0 to 5 loop
         en_read2 <= '1';
         en_write1 <= '1';
         addr1 <= random_addr(i);  
         addr2 <= random_addr(i);  
         input1 <= content_in(i); 
         wait for Clk_period;
         if (output1/=Z_out or output2/=Z_out) then
            report " In your code, the outputs are not high impedance (Z) when en_read2 and en_write1 are both enabled and operating on the same address." severity failure;
         end if; 
         -- check that the data which is read is the previous one
         en_read2 <= '1';
         en_write1 <= '0';
         wait for Clk_period;
         if (output1/=Z_out) then
             report " In your code, output1 is not high impedance (Z) when only en_read2 is enabled." severity failure;
         end if;  
         
         if (output2/=content_test_out(i)) then
            report " In your code, input1 is written to the RAM when en_read2 and en_write1 are both enabled and operating on the same address." severity failure;
         end if;              
     end loop;
     
    --------------- 

      for i in 0 to 5 loop
         en_read2 <= '1';
         en_write1 <= '1';
	addr1 <= std_logic_vector(to_unsigned(to_integer(unsigned(random_addr(i)))+1, %%ADDRLENGTH+1));  
	addr2 <= random_addr(i);  
	input1 <= content_in(i);
	wait for Clk_period;            
	-- check that the data which is read is the previous one
         en_write1 <= '0';
        addr2 <= random_addr(i);  
	wait for Clk_period;
	if  (%%READLENGTH+1)/(%%DATASIZE)=2 then 
	if (output2/=content_test_out(i)) then
	  report " In your code, the content of RAM changes when en_read2 and en_write1 are enabled and addr1 is equal to the next higher address of addr2 (addr1=addr2+1). But, the content of the RAM must not be changed and the outputs shall be high impedance (Z) in this case." severity failure;
	end if;
      
	elsif  (%%WRITELENGTH+1)/(%%DATASIZE)=1 then 
	 addr2 <= std_logic_vector(to_unsigned(to_integer(unsigned(random_addr(i)))+1, %%ADDRLENGTH+1));  
	 wait for Clk_period;
         if (output2(%%DATASIZE-1 downto 0)/=content_out(i)(%%DATASIZE-1 downto 0)) then
            report " In your code, input1 is not written to the RAM correctly when en_write1 and en_read2 are both enabled are enabled and addr1 is equal to the next higher address of addr2 (addr1=addr2+1)." severity failure;	
         end if;
     end if;
   end loop; 
    ---------- 
   for i in 8 to 15 loop
         en_read2 <= '1';
         en_write1 <= '1';
	addr1 <= random_addr(i); 
	addr2 <= std_logic_vector(to_unsigned(to_integer(unsigned(random_addr(i)))+1, %%ADDRLENGTH+1)); 
	input1 <= content_in(i);
	wait for Clk_period;          
	-- check that the data which is read is the previous one
         en_write1 <= '0';
         addr2 <= random_addr(i);
	wait for Clk_period;
	if  (%%WRITELENGTH+1)/(%%DATASIZE)=2 then  
	if (output2/=content_test_out(i)) then
	    report " In your code, the content of RAM changes when en_read2 and en_write1 are enabled and addr2 is equal to the next higher address of addr1 (addr2=addr1+1). But, the content of the RAM must not be changed and the outputs shall be high impedance (Z) in this case." severity failure;
	end if;              
	elsif  (%%WRITELENGTH+1)/(%%DATASIZE)=1 then   
         if (output2/=content_out(i)) then
            report " In your code, input1 is not written to the RAM correctly when en_write1 and en_read2 are both enabled and addr2 is equal to the next higher address of addr1 (addr2=addr1+1)." severity failure;	
         end if;
     end if;
  end loop; 
  
      ---to have a proper data in the RAM 
   en_read1 <= '0';
   en_read2 <= '0';
   en_write2 <= '0';
   en_write1 <= '1';
   for i in random_addr'range loop
      addr1 <= random_addr(i);
      input1 <= (others => '0');
      wait for Clk_period; 
      addr1 <= std_logic_vector(to_unsigned(to_integer(unsigned(random_addr(i)))+1, %%ADDRLENGTH+1)); 
      wait for Clk_period;
   end loop;
   for i in random_addr'range loop
      input1 <= content_test_in(i);
      addr1 <= random_addr(i);
      wait for Clk_period;
   end loop; 
       
     -- it is not possible both read1 to and write2 from the same address
     -----------------------------------------------------------------------     
     en_read2 <= '0';
     en_write1 <= '0';
     for i in 0 to 5 loop
         en_read1 <= '1';
         en_write2 <= '1';
         addr1 <= random_addr(i);  
         addr2 <= random_addr(i);  
         input2 <= content_in(i); 
         wait for Clk_period;
         if (output1/=Z_out or output2/=Z_out) then
            report " In your code, outputs are not high impedance (Z) when en_read1 and en_write2 are both enabled and operating on the same address." severity failure;
         end if; 
         -- check that the data which is read is the previous one
         en_read1 <= '1';
         en_write2 <= '0';
         wait for Clk_period;
         if (output2/=Z_out) then
             report " In your code, output2 is not high impedance (Z) when only en_read1 is enabled." severity failure;
         end if;  
         
         if (output1/=content_test_out(i)) then
            report " In your code, input2 is written to the RAM when en_read1 and en_write2 are both enabled and operating on the same address." severity failure;
         end if;              
     end loop;     
  -------
       
      for i in 0 to 5 loop
         en_read1 <= '1';
         en_write2 <= '1';
	addr1 <= random_addr(i);  
	addr2 <= std_logic_vector(to_unsigned(to_integer(unsigned(random_addr(i)))+1, %%ADDRLENGTH+1));  
	input2 <= content_in(i);
	wait for Clk_period;            
	-- check that the data which is read is the previous one
         en_write2 <= '0';
         addr1 <= random_addr(i);
	wait for Clk_period;
	if (%%READLENGTH+1)/(%%DATASIZE)=2 then 
	  if (output1/=content_test_out(i)) then
	   report " In your code, the content of RAM changes when en_read1 and en_write2 are both enabled and addr2 is equal to the next higher address of addr1 (addr2=addr1+1)." severity failure;
	  end if;
	  
	elsif (%%READLENGTH+1)/(%%DATASIZE)=1 then 
	 addr1 <= std_logic_vector(to_unsigned(to_integer(unsigned(random_addr(i)))+1, %%ADDRLENGTH+1));  
	 wait for Clk_period;
         if (output1(%%DATASIZE-1 downto 0)/=content_out(i)(%%DATASIZE-1 downto 0)) then
            report " In your code, input2 is not written to the RAM correctly when en_write2 and en_read1 are both enabled are enabled and addr2 is equal to the next higher address of addr1 (addr2=addr1+1)." severity failure;	
         end if;
        end if;
      end loop;
    --------
      
      for i in 8 to 15 loop
         en_read1 <= '1';
         en_write2 <= '1';
	addr1 <= std_logic_vector(to_unsigned(to_integer(unsigned(random_addr(i)))+1, %%ADDRLENGTH+1));  
	addr2 <= random_addr(i); 
	input2 <= content_in(i);
	wait for Clk_period;          
	-- check that the data which is read is the previous one
         en_write2 <= '0';
         addr1 <= random_addr(i);
	wait for Clk_period;
	if (%%WRITELENGTH+1)/(%%DATASIZE)=2 then 
	  if (output1/=content_test_out(i)) then
	    report " In your code, the content of RAM changes when en_read1 and en_write2 are both enabled and addr1 is equal to the next higher address of addr2 (addr1=addr2+1)." severity failure;
	  end if; 
	  
	 elsif (%%WRITELENGTH+1)/(%%DATASIZE)=1 then 
         if (output1/=content_out(i)) then
            report " In your code, input2 is not written to the RAM correctly when en_write2 and en_read1 are both enabled and addr1 is equal to the next higher address of addr2 (addr1=addr2+1)." severity failure;	        
	end if;
      end if; 
    end loop; 

   ---to have a proper data in the RAM 
   en_read1 <= '0';
   en_read2 <= '0';
   en_write2 <= '0';
   en_write1 <= '1';
   for i in random_addr'range loop
      addr1 <= random_addr(i);
      input1 <= (others => '0');
      wait for Clk_period; 
      addr1 <= std_logic_vector(to_unsigned(to_integer(unsigned(random_addr(i)))+1, %%ADDRLENGTH+1)); 
      wait for Clk_period;
   end loop;
   for i in random_addr'range loop
      input1 <= content_test_in(i);
      addr1 <= random_addr(i);
      wait for Clk_period;
   end loop; 
   
     -- check if read2 and write1 work together correctly
     ----------------------------------------------------
    en_write2 <= '0'; 
    en_read1 <= '0';   
    en_write1 <= '1'; 
    en_read2 <= '1';
     for i in 0 to 7 loop
        addr1 <= random_addr(i);  
        addr2 <= random_addr(15-i);  
        input1 <= content_in(i);
        input2 <= content_test_in(i);
        wait for Clk_period;
        -- check read2 is done correctly
        if (output2/=content_test_out(15-i)) then
           report " In your code, the data is not read correctly from address addr2 of the RAM when en_write1 and en_read2 are both enabled and operating on two different addresses at the same time." severity failure;
        end if; 
        
       if (output1/=Z_out) then
           report " In your code, output1 is not high impedance (Z) when en_write1 and en_read2 are both enabled and operating on two different addresses at the same time." severity failure;
       end if;
    end loop;
    
    --check both writing operations 
    en_write1 <= '0'; 
    en_read2 <= '1'; 
    for i in 0 to 7 loop
         addr2 <= random_addr(i); 
         wait for Clk_period;
         ---check write1 is done correctly 
         if (output2/=content_out(i)) then
            report " In your code, input1 is not written to the RAM correctly when en_write1 and en_read2 are both enabled and operating on two different addresses at the same time." severity failure;
         end if;    
                    
         if (%%WRITELENGTH+1)/(%%DATASIZE)=2 then     
	 if (%%READLENGTH+1)/(%%DATASIZE)=1 then         
         
             addr2 <= std_logic_vector(to_unsigned(to_integer(unsigned(random_addr(i)))+1, %%ADDRLENGTH+1));
             wait for Clk_period;   
             if (output2/=content_in(i)(%%WRITELENGTH downto %%READLENGTH+1)) then
                 report " The upper half of input1 is not written to the memory correctly when both en_write2 and en_read1 are enabled." severity failure;
             end if;        
         end if;
         end if;
         ---check write2 did not operate 
         addr2 <= random_addr(15-i); 
         wait for Clk_period;
         -- check that the data which is read is the previous one
         if (output2=content_test_out(i) and content_test_out(i)/=content_test_out(15-i)) then
            report " In your code, input2 is written to the RAM when en_write1 and en_read2 are both enabled and operating on two different addresses at the same time." severity failure;
         end if;          
     end loop;
       
     --write the rest of ram with content_test_in  
     for i in 8 to 15 loop
         en_write1 <= '1'; 
         en_read2 <= '0';
         addr1 <= random_addr(i);  
         input1 <= content_in(i);
         wait for Clk_period;
     end loop;       
     
     -- check if read1 and write2 work together correctly
     ----------------------------------------------------
     --to make output2 be non_Z
     en_write2 <= '0'; 
     en_read1 <= '0';   
     en_write1 <= '0'; 
     en_read2 <= '1';
     input2 <= content_in(0);
     wait for Clk_period;
      --
    en_write2 <= '1'; 
     en_read1 <= '1';   
     en_write1 <= '0'; 
     en_read2 <= '0';
      for i in 0 to 7 loop
         addr2 <= random_addr(i);  
         addr1 <= random_addr(15-i);  
         input2 <= content_test_in(i);
         input1 <= content_in(i);
         wait for Clk_period;
         -- check read1 is done correctly
         if (output1/=content_out(15-i)) then
            report " In your code, the data is not read correctly from address addr1 of the RAM when en_write2 and en_read1 are both enabled and operating on two different addresses at the same time." severity failure;
         end if; 
         
        if (output2/=Z_out) then
            report " In your code, output2 is not high impedance (Z) when en_write2 and en_read1 are both enabled and operating on two different addresses at the same time." severity failure;
        end if;
     end loop;
     
     --check both writing operations 
     en_write2 <= '0'; 
     en_read1 <= '1'; 
     for i in 0 to 7 loop
          addr1 <= random_addr(i); 
          wait for Clk_period;
          ---check write2 is done correctly 
          if (output1/=content_test_out(i)) then
             report " In your code, input2 is not written to the RAM correctly when en_write2 and en_read1 are both enabled and operating on two different addresses at the same time." severity failure;
          end if;      

        if (%%WRITELENGTH+1)/(%%DATASIZE)=2 then    
	 if (%%READLENGTH+1)/(%%DATASIZE)=1 then
             addr1 <= std_logic_vector(to_unsigned(to_integer(unsigned(random_addr(i)))+1, %%ADDRLENGTH+1));
             wait for Clk_period;   
             if (output1/=content_test_in(i)(%%WRITELENGTH downto %%READLENGTH+1)) then
                 report " The upper half of input2 is not written to the memory correctly when both en_write2 and en_read1 are enabled." severity failure;
             end if;        
         end if;
       end if;
       
       
         ---check write1 did not operate 
       addr1 <= random_addr(15-i); 
       wait for Clk_period;
       -- check that the data which is read is the previous one
       if (output1=content_out(i) and content_out(i)/=content_in(15-i)) then
          report " In your code, input1 is written to the RAM when en_write2 and en_read1 are both enabled and operating on two different addresses at the same time." severity failure;
       end if;          
   end loop;
     
   --write the rest of ram with content_test_in  
   for i in 8 to 15 loop
       en_write2 <= '1'; 
       en_read1 <= '0';
       addr2 <= random_addr(i);  
       input2 <= content_test_in(i);
       wait for Clk_period;
   end loop;     
                   
     -- check if both read lines work together correctly
     ---------------------------------------------------
     en_write2 <= '0';   
         -- check that the data which is read is the previous one
     for i in random_addr'range loop
         en_read1 <= '1';
         en_read2 <= '1';
         en_write1 <= '0';
         addr1 <= random_addr(i); 
         addr2 <= random_addr(15-i);
         input1 <= content_in(i);
         input2 <= content_in(15-i);
         wait for Clk_period;
         if (output1/=content_test_out(i)) then
            report " In your code, the content of RAM cannot be read correctly from address addr1 of the RAM when both reading signals are enabled at the same time." severity failure;
         end if;   
         
         if (output2/=content_test_out(15-i)) then
            report " In your code, the content of RAM cannot be read correctly from address addr2 of the RAM when both reading signals are enabled at the same time." severity failure;
         end if;         
                          
     end loop;
     
     -- check both read lines from the same address
     ----------------------------------------------
     en_write1 <= '0';
     en_write2 <= '0';
     en_read1 <= '1';
     en_read2 <= '1';
     addr1 <= random_addr(0);  
     addr2 <= random_addr(0);
     wait for Clk_period; 
     if (output1/=content_test_out(0)) then
         report " In your code, the data is not read correctly from address addr1 of the RAM when only both en_read1 and en_read2 are enabled and reading from the same address." severity failure;
     elsif (output2/=content_test_out(0)) then
         report " In your code, the data is not read correctly from address addr2 of the RAM when only both en_read1 and en_read2 are enabled and reading from the same address." severity failure;
     end if;   
          
     -- it is not possible to have two write actions in the same address
     -------------------------------------------------------------------
     en_read2 <= '0';
     for i in 0 to 5 loop
         en_write1 <= '1';
         en_write2 <= '1';
         en_read1 <= '0';
         addr1 <= random_addr(i);  
         addr2 <= random_addr(i);  
         input1 <= content_in(i); 
         input2 <= content_in(i);
         wait for Clk_period;
        if (output1/=Z_out and output2/=Z_out) then
            report " In your code, both outputs are not high impedance (Z) when both writing signals are enabled and operating on the same addresse at the same time." severity failure;
        end if;           
         -- check that the data which is read is the previous one
         en_read1 <= '1';
         en_write1 <= '0';
         en_write2 <= '0';
         wait for Clk_period;
         if (output1/=content_test_out(i)) then
            report " In your code, the inputs are written to the RAM when both writing signals are enabled and operating on the same addresse at the same time. But, the content of the RAM must not be changed and the outputs shall be high impedance (Z) in this case." severity failure;
         end if;        
     end loop;

 
      for i in 0 to 5 loop
         en_write1 <= '1';
         en_write2 <= '1';
         en_read1 <= '0';
	 addr1 <= std_logic_vector(to_unsigned(to_integer(unsigned(random_addr(i)))+1, %%ADDRLENGTH+1));  
	addr2 <= random_addr(i); 
	input1 <= content_in(i); 
	input2 <= content_in(i);
	wait for Clk_period;
	if (output1/=Z_out and output2/=Z_out) then
	    report " In your code, the output is not high impedance (Z) when both writing signals are enabled and addr1 is equal to the next higher address of addr2 (addr1=addr2+1). But, the content of the RAM must not be changed and the outputs shall be high impedance (Z) in this case." severity failure;
	end if;             
	-- check that the data which is read is the previous one
         en_read1 <= '1';
         en_write1 <= '0';
         en_write2 <= '0';
         addr1 <= random_addr(i); 
	wait for Clk_period;
	if  (%%WRITELENGTH+1)/(%%DATASIZE)=2 then  
	  if (output1/=content_test_out(i)) then
	      report " In your code, the content of RAM changes when both writing signals are enabled and addr1 is equal to the next higher address of addr2 (addr1=addr2+1). But, the content of the RAM must not be changed and the outputs shall be high impedance (Z) in this case." severity failure;
	  end if;
        elsif  (%%WRITELENGTH+1)/(%%DATASIZE)=1 then
         if (output1(%%DATASIZE-1 downto 0)/=content_out(i)(%%DATASIZE-1 downto 0)) then
            report " In your code, input2 is not written to the RAM correctly when both en_write signals are enabled and addr1 is equal to the next higher address of addr2 (addr1=addr2+1)." severity failure;
         end if;         
     end if;
   end loop;
     ----------------------
    for i in 8 to 15 loop  
	en_write1 <= '1';
	en_write2 <= '1';
	en_read1 <= '0';    
	addr1 <= random_addr(i);   
	addr2 <= std_logic_vector(to_unsigned(to_integer(unsigned(random_addr(i)))+1, %%ADDRLENGTH+1));
	input1 <= content_in(i); 
	input2 <= content_in(i);
	wait for Clk_period;
	if (output1/=Z_out and output2/=Z_out) then
	    report " In your code, the output is not high impedance (Z) when both writing signals are enabled and addr2 is equal to the next higher address of addr1 (addr2=addr1+1). But, the content of the RAM must not be changed and the outputs shall be high impedance (Z) in this case." severity failure;
	end if;             
	-- check that the data which is read is the previous one
         en_read1 <= '1';
         en_write1 <= '0';
         en_write2 <= '0';
         addr1 <= random_addr(i); 
	wait for Clk_period;
	if  (%%WRITELENGTH+1)/(%%DATASIZE)=2 then 
	  if (output1/=content_test_out(i)) then
	      report " In your code, the content of RAM changes when both writing signals are enabled and addr2 is equal to the next higher address of addr1 (addr2=addr1+1). But, the content of the RAM must not be changed and the outputs shall be high impedance (Z) in this case." severity failure;
	  end if;              
	 elsif  (%%WRITELENGTH+1)/(%%DATASIZE)=1 then
         if (output1(%%DATASIZE-1 downto 0)/=content_out(i)(%%DATASIZE-1 downto 0)) then
            report " In your code, input1 is not written to the RAM correctly when both en_write signals are enabled and addr2 is equal to the next higher address of addr1 (addr2=addr1+1)." severity failure;     
         end if;
     end if;
  end loop; 
     
   ---to have a proper data in the RAM 
   en_read1 <= '0';
   en_read2 <= '0';
   en_write2 <= '0';
   en_write1 <= '1';
   for i in random_addr'range loop
      addr1 <= random_addr(i);
      input1 <= (others => '0');
      wait for Clk_period; 
      addr1 <= std_logic_vector(to_unsigned(to_integer(unsigned(random_addr(i)))+1, %%ADDRLENGTH+1)); 
      wait for Clk_period;
   end loop;
   for i in random_addr'range loop
      input1 <= content_test_in(i);
      addr1 <= random_addr(i);
      wait for Clk_period;
   end loop; 
   
   
     -- check if both write lines work together correctly
     ----------------------------------------------------
     
     ---- to make the outputs be non_Z
     en_write1 <= '0';
     en_write2 <= '0';
     en_read1 <= '1';
     en_read2 <= '1';
     addr1 <= random_addr(0);
     addr2 <= random_addr(0);
     wait for Clk_period; 
     en_read2 <= '0';
     en_read1 <= '0';
     ---
     
     en_read2 <= '0';   
     for i in random_addr'range loop
         en_read1 <= '0';
         en_write2 <= '1';
         en_write1 <= '1';
         addr1 <= random_addr(i);  
         addr2 <= random_addr(15-i);  
         input1 <= content_in(i);
         input2 <= content_in(15-i); 
         wait for Clk_period;
         if (output1/=Z_out or output2/=Z_out) then
            report " The outputs are not high impedance (Z) when only both en_write signals are enabled." severity failure;
         end if;  
         -- check that the data which is read is the previous one
         en_read1 <= '1';
         en_write2 <= '0';
         en_write1 <= '0';
         addr1 <= random_addr(i); 
         wait for Clk_period;
         if (output1/=content_out(i)) then
            report " In your code, input1 is not written to the RAM correctly when both en_write signals are enabled and operating on two different addresses at the same time." severity failure;
         end if;
        -- check if most significant half of input is not written to the memory correctly                 
        if (%%WRITELENGTH+1)/(%%DATASIZE)=2 then
	 if (%%READLENGTH+1)/(%%DATASIZE)=1 then
             addr1 <= std_logic_vector(to_unsigned(to_integer(unsigned(random_addr(i)))+1, %%ADDRLENGTH+1));
             wait for Clk_period;   
             if (output1/=content_in(i)(%%WRITELENGTH downto %%READLENGTH+1)) then
                 report "The upper half of input1 is not written to the memory correctly using en_write1 when both en_write signals are enabled." severity failure;
             end if;
         end if;
         end if;     
              
         addr1 <= random_addr(15-i); 
         wait for Clk_period;
         if (output1/=content_out(15-i)) then
            report " In your code, the input2 is not written to the RAM correctly when both en_write signals are enabled and operating on two different addresses at the same time." severity failure;
         end if;   
        -- check if most significant half of input is not written to the memory correctly                 
        if (%%WRITELENGTH+1)/(%%DATASIZE)=2 then
	  
         if (%%READLENGTH+1)/(%%DATASIZE)=2 then
             addr1 <= std_logic_vector(to_unsigned(to_integer(unsigned(random_addr(15-i)))+1, %%ADDRLENGTH+1));
             wait for Clk_period; 
             if (output1(%%DATASIZE-1 downto 0)/=content_in(15-i)(%%WRITELENGTH downto %%DATASIZE)) then
                 report " The upper half of input2 is not written to the memory correctly using en_write2 when both en_write signals are enabled." severity failure;
             end if;              
         end if;
         
	 if (%%READLENGTH+1)/(%%DATASIZE)=1 then
             addr1 <= std_logic_vector(to_unsigned(to_integer(unsigned(random_addr(15-i)))+1, %%ADDRLENGTH+1));
             wait for Clk_period;   
             if (output1/=content_in(15-i)(%%WRITELENGTH downto %%READLENGTH+1)) then
                 report " The upper half of input2 is not written to the memory correctly using en_write2 when both en_write signals are enabled." severity failure;
             end if;
         end if; 
       end if;
     end loop;
     
     -- when read2, write1 and write2 are activ
     -----------------------------------------
     
     for i in 0 to 5 loop
         en_read2 <= '1';
         en_read1 <= '0';
         en_write2 <= '1';
         en_write1 <= '1'; 
         addr1 <= random_addr(i);  
         addr2 <= random_addr(15-i);  
         input1 <= content_test_in(i);
         input2 <= content_test_in(15-i); 
         wait for Clk_period;
         if (output1/=Z_out or output2/=Z_out) then
            report " In your code, the outputs are not high impedance (Z) when en_read2, en_write1 and en_write2 are enabled at the same time." severity failure;
         end if;           
         
         en_read1 <= '1';
         en_read2 <= '1';
         en_write2 <= '0';
         en_write1 <= '0';
         addr1 <= random_addr(i); 
         addr2 <= random_addr(15-i);
         wait for Clk_period;
         if (output1/=content_out(i)) then
            report " In your code, input1 is written to the RAM when en_read2, en_write1 and en_write2 are enabled. But, the content of the RAM must not be changed and the outputs shall be high impedance (Z) in this case." severity failure;
         end if;
                 
         if (output2/=content_out(15-i)) then
            report " In your code, input2 is written to the RAM when en_read2, en_write1 and en_write2 are enabled. But, the content of the RAM must not be changed and the outputs shall be high impedance (Z) in this case." severity failure;
         end if;             
     end loop;

     -- when read1, write1 and write2 are active
     -------------------------------------------

     for i in 0 to 5 loop
         en_read2 <= '0';
         en_read1 <= '1';
         en_write2 <= '1';
         en_write1 <= '1'; 
         addr1 <= random_addr(i);  
         addr2 <= random_addr(15-i);  
         input1 <= content_test_in(i);
         input2 <= content_test_in(15-i); 
         wait for Clk_period;
         if (output1/=Z_out or output2/=Z_out) then
            report " In your code, the outputs are not high impedance (Z) when en_read1, en_write1 and en_write2 are enabled at the same time." severity failure;
         end if;  
         
         en_read1 <= '1';
         en_read2 <= '1';
         en_write2 <= '0';
         en_write1 <= '0';
         addr1 <= random_addr(i); 
         addr2 <= random_addr(15-i);
         wait for Clk_period;
         if (output1/=content_out(i)) then
            report " In your code, input1 is written to the RAM when en_read1, en_write1 and en_write2 are enabled. But, the content of the RAM must not be changed and the outputs shall be high impedance (Z) in this case." severity failure;
         end if;
         if (output2/=content_out(15-i)) then
            report " In your code, input2 is written to the RAM when en_read1, en_write1 and en_write2 are enabled. But, the content of the RAM must not be changed and the outputs shall be high impedance (Z) in this case." severity failure;
         end if;        
            
     end loop;

     -- when read1, read2 and write2 are active
     ------------------------------------------
     for i in 0 to 5 loop
         en_read2 <= '1';
         en_read1 <= '1';
         en_write2 <= '1';
         en_write1 <= '0'; 
         addr1 <= random_addr(i);  
         addr2 <= random_addr(15-i);  
         input1 <= content_test_in(i);
         input2 <= content_test_in(15-i);  
         wait for Clk_period;
         if (output1/=Z_out or output2/=Z_out) then
            report " In your code, the outputs are not high impedance (Z) when en_read1, en_read2 and en_write2 are enabled at the same time." severity failure;
         end if;         
         
         en_read1 <= '1';
         en_read2 <= '1';
         en_write2 <= '0';
         en_write1 <= '0';
         addr1 <= random_addr(i); 
         addr2 <= random_addr(15-i);
         wait for Clk_period;
         if (output1/=content_out(i)) then
            report " In your code, input1 is written to the RAM when en_read1, en_read2 and en_write2 are enabled. But, the content of the RAM must not be changed and the outputs shall be high impedance (Z) in this case." severity failure;
         end if;   
         if (output2/=content_out(15-i)) then
            report " In your code, input2 is written to the RAM when en_read1, en_read2 and en_write2 are enabled. But, the content of the RAM must not be changed and the outputs shall be high impedance (Z) in this case." severity failure;
         end if;          
     end loop;         
     
     -- when read1, read2 and write1 are active
     ------------------------------------------
     for i in 1 to 5 loop
         en_read2 <= '1';
         en_read1 <= '1';
         en_write2 <= '0';
         en_write1 <= '1'; 
         addr1 <= random_addr(i);  
         addr2 <= random_addr(15-i);  
         input1 <= content_test_in(i);
         input2 <= content_test_in(15-i);  
         wait for Clk_period;
         if (output1/=Z_out or output2/=Z_out) then
            report " In your code, the outputs are not high impedance (Z) when en_read1, en_read2 and en_write1 are enabled at the same time." severity failure;
         end if;             
         
         en_read1 <= '1';
         en_read2 <= '1';
         en_write2 <= '0';
         en_write1 <= '0';
         addr1 <= random_addr(i); 
         addr2 <= random_addr(15-i);
         wait for Clk_period;
         if (output1/=content_out(i)) then
            report " In your code, input1 is written to the RAM when en_read1, en_read2 and en_write1 are enabled. But, the content of the RAM must not be changed and the outputs shall be high impedance (Z) in this case." severity failure;
         end if;  
         if (output2/=content_out(15-i)) then
            report " In your code, input2 is written to the RAM when en_read1, en_read2 and en_write1 are enabled. But, the content of the RAM must not be changed and the outputs shall be high impedance (Z) in this case." severity failure;
         end if;           
     end loop; 
     
     -- when all enable signals are active
     -------------------------------------
     for i in 0 to 5 loop
         en_read2 <= '1';
         en_read1 <= '1';
         en_write2 <= '1';
         en_write1 <= '1'; 
         addr1 <= random_addr(i);  
         addr2 <= random_addr(15-i);  
         input1 <= content_test_in(i);
         input2 <= content_test_in(15-i); 
         wait for Clk_period;
         if (output1/=Z_out or output2/=Z_out) then
            report " In your code, the outputs are not high impedance (Z) when all enable signals are enabled at the same time." severity failure;
         end if;           
         
         en_read1 <= '1';
         en_read2 <= '1';
         en_write2 <= '0';
         en_write1 <= '0';
         addr1 <= random_addr(i); 
         addr2 <= random_addr(15-i);
         wait for Clk_period;
         if (output1/=content_out(i)) then
            report " In your code, input1 is written to the RAM when all enable signals are enabled. But, the content of the RAM must not be changed and the outputs shall be high impedance (Z) in this case." severity failure;
         end if;
                 
         if (output2/=content_out(15-i)) then
            report " In your code, input2 is written to the RAM when all enable signals are enabled. But, the content of the RAM must not be changed and the outputs shall be high impedance (Z) in this case." severity failure;
         end if;             
     end loop;     
 
     --check the outputs are zero when en_write1 is only enabled
     ----------------------------------------------------------- 
      -- to make the output1 be different from high impedance
     en_write1 <= '0';
      en_read2 <= '1';
      en_write2 <= '0';
      en_read1 <= '1'; 
      addr2 <= random_addr(0);        
      wait for Clk_period; 
      en_read2 <= '0';
      en_read1 <= '0'; 
     
     for i in random_addr'range loop
        en_write1 <= '1';
        en_write2 <= '0';
        en_read1 <= '0';
        en_read2 <= '0';
        addr1 <= random_addr(i);   
        addr2 <= random_addr(15-i); 
        input1 <= content_test_in(i); 
        wait for Clk_period; 
        if (output1/=Z_out or output2/=Z_out) then
            report " In your code, the outputs are not high impedance (Z) when only en_write1 is enabled." severity failure;
        end if; 
   end loop;         

     --check the outputs are zero when en_write2 is only enabled
     -----------------------------------------------------------      
     -- to make the output1 be different from high impedance
        ------- make output2 be non-Z 
     en_write1 <= '0';
     en_read2 <= '1';
     en_write2 <= '0';
     en_read1 <= '1'; 
     addr2 <= random_addr(0);        
     wait for Clk_period; 
     en_read2 <= '0';
     en_read1 <= '0'; 
     ----
  for i in random_addr'range loop
     en_write2 <= '1';
     en_read1 <= '0';
     addr1 <= random_addr(i); 
     addr2 <= random_addr(15-i);  
     input2 <= content_in(15-i);  
     wait for Clk_period; 
     if (output1/=Z_out or output2/=Z_out) then
         report " In your code, the outputs are not high impedance (Z) only en_write2 is enabled." severity failure;
     end if;  
   end loop;  
   
   
 
     report "Success" severity failure;  
    
   end process;

end Behavioral;