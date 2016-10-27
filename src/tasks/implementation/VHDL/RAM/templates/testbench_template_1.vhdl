LIBRARY IEEE;
USE IEEE.std_logic_1164.ALL;
USE IEEE.numeric_std.ALL;


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
      
    --------------------check the RAM------------------------
    -- the output should be "ZZZ.." when control signals are zero
    en_read <= '0';
    wait for Clk_period;
     if (output/=Z_out and output/=U_out) then
        report " The ouput is '" & to_string(std_logic_vector(output)) & "'. However, the output should be high impedance (Z) when nothing is read from the memory." severity failure;
     elsif (output/=Z_out and output=U_out) then
        report " The output should be high impedance (Z) when nothing is read from the memory." severity failure;
     end if; 
    
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
    
    
     -- check en_write1 only
     -----------------------
     en_write2 <= '0';
     for i in 0 to 7 loop
        en_write1 <= '1';
	en_read <= '0';
        addr1 <= random_addr(i); 
        addr2 <= random_addr(15-i);
        input1 <= content_in(i);
        input2 <= content_test_in(i);
        wait for Clk_period;
        if (output/=Z_out) then
            report " In your code, the output is not high impedance (Z) when only en_write1 is enabled." severity failure;
        end if;   
      
        -- check if the data has been written in the memory
	en_write1 <= '0';
	en_read <= '1';
            
        ---check write2 did not operate 
        addr1 <= random_addr(15-i);   
         wait for Clk_period;
         if (output=content_test_out(i) and content_test_out(i)/=content_out(15-i) and content_test_out(i)/=zero_out) then
            report " In your code, input2 is written to the RAM when only en_write1 is enabled." severity failure;
         end if;  
         
        addr1 <= random_addr(i);   
        wait for Clk_period;      
        if (output/=content_out(i)) then
            report " The data cannot be written to the memory correctly when en_write1 is enabled, or the content of memory cannot be read when en_read is enabled." severity failure;
        end if;  
        -- check if higher significant half of input is not written to the memory correctly                 
        if (%%WRITELENGTH+1)/(%%DATASIZE)=2 then
	  
         if (%%READLENGTH+1)/(%%DATASIZE)=2 then
             addr1 <= std_logic_vector(to_unsigned(to_integer(unsigned(random_addr(i)))+1, %%ADDRLENGTH+1));
             wait for Clk_period; 
             if (output(%%DATASIZE-1 downto 0)/=content_in(i)(%%WRITELENGTH downto %%DATASIZE)) then
                 report " The upper half of input1 is not written to the memory correctly when en_write1 is only enabled. Note that the length of input is twice the length of each memory location." severity failure;
             end if;              
         end if;
         
	 if (%%READLENGTH+1)/(%%DATASIZE)=1 then
            addr1 <= std_logic_vector(to_unsigned(to_integer(unsigned(random_addr(i)))+1, %%ADDRLENGTH+1));		     
            wait for Clk_period;   
            if (output/=content_in(i)(%%WRITELENGTH downto %%READLENGTH+1)) then
                report " The upper half of input1 is not written to the memory correctly when en_write1 is only enabled or when only en_read is enabled." severity failure;
            end if;
        end if;
        end if;
        
    end loop;
    
     --write the rest of ram with content_in  
    en_write1 <= '1';
    en_read <= '0';
    for i in 8 to 15 loop
        addr1 <= random_addr(i); 
        input1 <= content_in(i);
        wait for Clk_period;
        if (output/=Z_out) then
            report " In your code, the output is not high impedance (Z) when only en_write1 is enabled." severity failure;
        end if;                   
     end loop;
     
     
     --check reading operation in order not to perform both writing operations as well
     ---------------------------------------------------------------------------------
        en_write1 <= '0';
        en_write2 <= '0';
        en_read <= '1';
      for i in 0 to 7 loop
        addr1 <= random_addr(i); 
        addr2 <= random_addr(15-i);
        input1 <= content_test_in(i);
        input2 <= content_test_in(15-i);
        wait for Clk_period;  
     end loop;
     
     for i in 0 to 7 loop        
        addr1 <= random_addr(i); 
        wait for Clk_period; 
        if (output/=content_out(i)) then
            report " In your code, input1 is written to the RAM when only en_read is enabled." severity failure;
        end if;  

        addr1 <= random_addr(15-i);
         wait for Clk_period;  
        if (output/=content_out(15-i)) then
            report " In your code, input2 is written to the RAM when only en_read is enabled." severity failure;
        end if;  
     end loop;
     
     -- check en_write2 only
     ----------------------
     en_write1 <= '0';
     for i in random_addr'range loop
        en_write2 <= '1';
        en_read <= '0';
        addr2 <= random_addr(i);   
        input2 <= content_test_in(i); 
        addr1 <= random_addr(15-i); 
        input1 <= content_test_in(15-i); 
        wait for Clk_period; 
        if (output/=Z_out) then
            report " In your code, the output is not high impedance (Z) when only en_write2 is enabled." severity failure;
        end if;            
        -- check if the data has been written in the memory
        en_read <= '1';
        en_write2 <= '0';
        addr1 <= random_addr(i);   
        wait for Clk_period; 
        if (output/=content_test_out(i)) then
            report " input2 cannot be written to the memory correctly when en_write2 is enabled, or the content of memory cannot be read when en_read is enabled." severity failure;
        end if;  
        -- check if higher significant half of input is not written in the memory correctly                 
        if (%%WRITELENGTH+1)/(%%DATASIZE)=2 then
	 if (%%READLENGTH+1)/(%%DATASIZE)=1 then
            addr1 <= std_logic_vector(to_unsigned(to_integer(unsigned(random_addr(i)))+1, %%ADDRLENGTH+1));
            wait for Clk_period;   
            if (output/=content_test_in(i)(%%WRITELENGTH downto %%READLENGTH+1)) then
                report " The upper half of input2 is not written to the memory correctly when en_write2 is enabled." severity failure;
            end if;
        end if; 
      end if;
      
        --check write2 operation in order not to operate write1
        if (i<6) then
        en_write2 <= '0';
        en_read <= '1';
        addr1 <= random_addr(15-i);
        wait for Clk_period;      
        if (output=content_test_out(15-i) and content_test_out(15-i)/=content_out(15-i)) then
            report " In your code, input1 is written to the RAM when only en_write2 is enabled." severity failure;
        end if; 
        end if;
     end loop;
  
     -- read and write1 should not be active at the same time 
     --------------------------------------------------------
     en_write2 <= '0';
     en_read <= '1';
     for i in random_addr'range loop
         en_write1 <= '1';
         addr1 <= random_addr(i);   
         input1 <= content_in(i);
         addr2 <= random_addr(15-i);  
         input2 <= content_in(15-i);
         wait for Clk_period;
         if (output/=Z_out) then
            report " In your code, the output is not high impedance (Z) when en_write1 and en_read signals are both enabled." severity failure;
         end if;  
         -- check that the data which is read is the previous one
         en_write1 <= '0';
         addr1 <= random_addr(i); 
         wait for Clk_period;
         if (output/=content_test_out(i)) then
            report " In your code, input1 is written to the RAM when en_write1 and en_read signals are both enabled." severity failure;
         end if;        
         
         en_write1 <= '0';
         addr1 <= random_addr(15-i); 
         wait for Clk_period;
         if (output/=content_test_out(15-i)) then
            report " In your code, input2 is written to the RAM when en_write1 and en_read signals are both enabled." severity failure;
         end if;        
         
     end loop;

     
     -- it is not possible to have two write actions in the same address
     -------------------------------------------------------------------
     for i in random_addr'range loop
     	 en_write1 <= '1';
     	 en_write2 <= '1';
         en_read <= '0';
         addr1 <= random_addr(i);  
         addr2 <= random_addr(i);  
         input1 <= content_in(i); 
         input2 <= content_in(i);
         wait for Clk_period;
         if (output/=Z_out) then
            report " In your code, the output is not high impedance (Z) when en_read is not enabled and both writing operations have the same address." severity failure;
         end if;             
         -- check that the data which is read is the previous one
         en_read <= '1';
     	    en_write1 <= '0';
     	    en_write2 <= '0';
         wait for Clk_period;
         if (output/=content_test_out(i)) then
            report " In your code, the content of RAM changes when both writing operations have the same address." severity failure;
         end if;        
     end loop;
     


   for i in 0 to 5 loop
      en_write1 <= '1';
      en_write2 <= '1';
     en_read <= '0';
     addr1 <= std_logic_vector(to_unsigned(to_integer(unsigned(random_addr(i)))+1, %%ADDRLENGTH+1));  
     addr2 <= random_addr(i); 
     input1 <= content_in(i); 
     input2 <= content_in(i);
     wait for Clk_period;
     if (output/=Z_out) then
        report " In your code, the output is not high impedance (Z) when only both en_write signals are enabled and addr1 is equal to the next higher address of addr2 (addr1=addr2+1)." severity failure;
     end if;             
     -- check that the data which is read is the previous one
     en_read <= '1';
     en_write1 <= '0';
     en_write2 <= '0';
     addr1 <= random_addr(i); 
     wait for Clk_period;
     if  (%%WRITELENGTH+1)/(%%DATASIZE)=2 then   
      if (output/=content_test_out(i)) then
        report " In your code, the content of RAM changes when both en_write signals are enabled and addr1 is equal to the next higher address of addr2 (addr1=addr2+1)." severity failure;
      end if;
      
     elsif  (%%WRITELENGTH+1)/(%%DATASIZE)=1 then
         if (output(%%DATASIZE-1 downto 0)/=content_out(i)(%%DATASIZE-1 downto 0)) then
            report " In your code, input2 is not written to the RAM correctly when both en_write signals are enabled and addr1 is equal to the next higher address of addr2 (addr1=addr2+1)." severity failure;
         end if;
     end if;
   end loop;
     ----------------------
   for i in 8 to 15 loop     
     en_write1 <= '1';
     en_write2 <= '1';
     en_read <= '0';     
     addr1 <= random_addr(i);   
     addr2 <= std_logic_vector(to_unsigned(to_integer(unsigned(random_addr(i)))+1, %%ADDRLENGTH+1));
     input1 <= content_in(i); 
     input2 <= content_in(i);
     wait for Clk_period;
     if (output/=Z_out) then
        report " In your code, the output is not high impedance (Z) when only both en_write signals are enabled and addr2 is equal to the next higher address of addr1 (addr2=addr1+1)." severity failure;
     end if;             
     -- check that the data which is read is the previous one
     en_read <= '1';
     en_write1 <= '0';
     en_write2 <= '0';
     addr1 <= random_addr(i);
     wait for Clk_period;
     if  (%%WRITELENGTH+1)/(%%DATASIZE)=2 then   
     if (output/=content_test_out(i)) then
        report " In your code, the content of RAM changes when only both en_write signals are enabled and addr2 is equal to the next higher address of addr1 (addr2=addr1+1)." severity failure;
     end if;              
     elsif  (%%WRITELENGTH+1)/(%%DATASIZE)=1 then
         if (output(%%DATASIZE-1 downto 0)/=content_out(i)(%%DATASIZE-1 downto 0)) then
            report " In your code, input1 is not written to the RAM correctly when both en_write signals are enabled and addr2 is equal to the next higher address of addr1 (addr2=addr1+1)." severity failure;
         end if;
     end if;
  end loop;     
 
     ---to have a proper data in the RAM 
   en_read <= '0';
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
     for i in random_addr'range loop
         en_read <= '0';
         en_write2 <= '1';
         en_write1 <= '1';
         addr1 <= random_addr(i);  
         addr2 <= random_addr(15-i);  
         input1 <= content_in(i);
         input2 <= content_in(15-i); 
         wait for Clk_period;
         if (output/=Z_out) then
            report " In your code, the output is not high impedance (Z) when en_read is not enabled and both writing operations have different addresses." severity failure;
         end if;             
         -- check that the data which is read is the previous one
         en_read <= '1';
         en_write2 <= '0';
         en_write1 <= '0';
         addr1 <= random_addr(i); 
         wait for Clk_period;
         if (output/=content_out(i)) then
            report " In your code, input1 is not written to the RAM correctly when both en_write signals are enabled and operating on two different addresses." severity failure;
         end if;
        -- check if higher significant half of input is not written in the memory correctly                 
         
        if (%%WRITELENGTH+1)/(%%DATASIZE)=2 then
         
	 if (%%READLENGTH+1)/(%%DATASIZE)=1 then
            addr1 <= std_logic_vector(to_unsigned(to_integer(unsigned(random_addr(i)))+1, %%ADDRLENGTH+1));
            wait for Clk_period;   
            if (output/=content_in(i)(%%WRITELENGTH downto %%READLENGTH+1)) then
                report " The upper half of input1 is not written in the memory correctly when both en_write signals are enabled." severity failure;
            end if;
        end if;
        end if;
        
         addr1 <= random_addr(15-i); 
         wait for Clk_period;
         if (output/=content_out(15-i)) then
            report " In your code, the input2 is not written to the RAM correctly when both en_write signals are enabled and operating on two different addresses." severity failure;
         end if;  
        -- check if higher significant half of input is not written in the memory correctly                 
        if (%%WRITELENGTH+1)/(%%DATASIZE)=2 then
	 if (%%READLENGTH+1)/(%%DATASIZE)=1 then
            addr1 <= std_logic_vector(to_unsigned(to_integer(unsigned(random_addr(15-i)))+1, %%ADDRLENGTH+1));
            wait for Clk_period;   
            if (output/=content_in(15-i)(%%WRITELENGTH downto %%READLENGTH+1)) then
                report " The upper half of input2 is not written in the memory correctly when both en_write signals are enabled." severity failure;
            end if;
        end if; 
      end if; 
     end loop;

     -- it is not possible to have write2 and read actions in the same address
     -------------------------------------------------------------------------
     en_write1 <= '0';
     for i in 0 to 5 loop
     	 en_write2 <= '1';
         en_read <= '1';
         addr1 <= random_addr(i);  
         addr2 <= random_addr(i);  
         input2 <= content_test_in(i);
         wait for Clk_period;
         -- check that the data which is read is the previous one
         if (output/=Z_out) then
            report " In your code, output is not high impedance (Z) when en_read and en_write2 are both enabled at the same time." severity failure;
         end if;
         
         en_read <= '1';
         en_write2 <= '0';
         wait for Clk_period;
         if (output/=content_out(i)) then
            report " In your code, input2 is written to the RAM when en_read and en_write2 are both enabled and operating on the same address. But, it is not possible to read from and write to the same address at the same time." severity failure;
         end if;           
         
     end loop;
  
      for i in 0 to 5 loop
     	 en_write2 <= '1';
         en_read <= '1';
	addr1 <= random_addr(i);  
	addr2 <= std_logic_vector(to_unsigned(to_integer(unsigned(random_addr(i)))+1, %%ADDRLENGTH+1));  
	input2 <= content_test_in(i);
	wait for Clk_period;
             
	-- check that the data which is read is the previous one
         en_read <= '1';
         en_write2 <= '0';
         addr1 <= random_addr(i); 
	wait for Clk_period;
	if  (%%READLENGTH+1)/(%%DATASIZE)=2 then 
	  if (output/=content_out(i)) then
	    report " In your code, the content of RAM changes when en_read and en_write2 are both enabled and addr2 is equal to the next higher address of addr1 (addr2=addr1+1)." severity failure;
	  end if; 
	elsif  (%%READLENGTH+1)/(%%DATASIZE)=1 then
	  addr1 <= std_logic_vector(to_unsigned(to_integer(unsigned(random_addr(i)))+1, %%ADDRLENGTH+1)); 
	  wait for Clk_period;
	  if (output/=content_test_in(i)(%%DATASIZE-1 downto 0)) then
            report " In your code, input2 is not written to the RAM correctly when only en_write2 and en_read are both enabled and addr2 is equal to the next higher address of addr1 (addr2=addr1+1)." severity failure;
	  end if; 
        end if;
      end loop;
      
     ------------------
      
      for i in 8 to 15 loop
     	 en_write2 <= '1';
         en_read <= '1';
	addr1 <= std_logic_vector(to_unsigned(to_integer(unsigned(random_addr(i)))+1, %%ADDRLENGTH+1));  
	addr2 <= random_addr(i); 
	input2 <= content_test_in(i);
	wait for Clk_period;
            
	-- check that the data which is read is the previous one
         en_read <= '1';
         en_write2 <= '0';
         addr1 <= random_addr(i); 
	wait for Clk_period;
	if (%%WRITELENGTH+1)/(%%DATASIZE)=2 then 
	  if (output/=content_out(i)) then
	      report " In your code, the content of RAM changes when en_read and en_write2 are both enabled and addr1 is equal to the next higher address of addr2 (addr1=addr2+1)." severity failure;
	  end if;  
	elsif (%%WRITELENGTH+1)/(%%DATASIZE)=1 then 
	  if (output/=content_test_out(i)) then
            report " In your code, input2 is not written to the RAM correctly when only en_write2 and en_read are both enabled and addr1 is equal to the next higher address of addr2 (addr1=addr2+1)." severity failure;
	  end if; 
        end if;
      end loop; 

     ---to have a proper data in the RAM 
   en_read <= '0';
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
      input1 <= content_in(i);
      addr1 <= random_addr(i);
      wait for Clk_period;
   end loop; 
   
     -- check if both write2 and read work together correctly to different addresses
     -------------------------------------------------------------------------------
     en_write2 <= '1';
     en_write1 <= '0';
     en_read <= '1';
     for i in 0 to 7 loop
        addr1 <= random_addr(15-i); 
        addr2 <= random_addr(i);
        input1 <= content_in(i);
        input2 <= content_test_in(i);
        wait for Clk_period;
        if (output/=content_out(15-i)) then
            report " In your code, the content of memory cannot be read correctly when only en_write2 and en_read are both enabled." severity failure;
        end if;   
     end loop;       
        -- check if the data has been written in the memory
    en_write2 <= '0';
    en_read <= '1';
    for i in 0 to 7 loop

        ---check write2 did not operate 
        addr1 <= random_addr(15-i);   
         wait for Clk_period;
         if (output=content_out(i) and content_out(i)/=content_out(15-i)) then
            report " In your code, input1 is written to the RAM when only en_write2 and en_read are both enabled." severity failure;
         end if; 
         
        addr1 <= random_addr(i);   
        wait for Clk_period;      
        if (output/=content_test_out(i)) then
            report " In your code, input2 is not written to the RAM correctly when only en_write2 and en_read are both enabled." severity failure;
        end if;                
        
        -- check if higher significant half of input is not written in the memory correctly                 
         
        if (%%WRITELENGTH+1)/(%%DATASIZE)=2 then	  
	 if (%%READLENGTH+1)/(%%DATASIZE)=1 then
            addr1 <= std_logic_vector(to_unsigned(to_integer(unsigned(random_addr(i)))+1, %%ADDRLENGTH+1));
            wait for Clk_period;   
            if (output/=content_test_in(i)(%%WRITELENGTH downto %%READLENGTH+1)) then
                report " The upper half of input1 is not written to the memory correctly when en_write2 and en_read are both enabled." severity failure;
            end if;
	  end if;   
        end if; 
       
    end loop;
    
     --write the rest of ram with content_in  
    en_write2 <= '1';
    en_read <= '0';
    for i in 8 to 15 loop
        addr2 <= random_addr(i); 
        input2 <= content_test_in(i);
        wait for Clk_period;                 
     end loop;
     
     
     
     -- when all enable signals are active
     -------------------------------------
     
     for i in 0 to 5 loop
         en_read <= '1';
         en_write2 <= '1';
         en_write1 <= '1'; 
         addr1 <= random_addr(i);  
         addr2 <= random_addr(15-i);  
         input1 <= content_in(i);
         input2 <= content_in(15-i); 
         wait for Clk_period;
         if (output/=Z_out) then
            report " In your code, the output is not high impedance (Z) when all enable signals are enabled at the same time." severity failure;
         end if;           
         
         en_read <= '1';
         en_write2 <= '0';
         en_write1 <= '0';
         addr1 <= random_addr(i); 
         wait for Clk_period;
         if (output/=content_test_out(i)) then
            report " In your code, input1 is written to the RAM when all enable signals are enabled. But, the content of the RAM must not be changed and the outputs shall be high impedance (Z) in this case." severity failure;
         end if;
         
         en_read <= '1';
         en_write2 <= '0';
         en_write1 <= '0';
         addr1 <= random_addr(15-i);
         wait for Clk_period;
         if (output/=content_test_out(15-i)) then
            report " In your code, input2 is written to the RAM when all enable signals are enabled. But, the content of the RAM must not be changed and the outputs shall be high impedance (Z) in this case." severity failure;
         end if;             
     end loop;          
     
    
     report "Success" severity failure;  
    
   end process;

end Behavioral;