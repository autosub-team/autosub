LIBRARY IEEE;
USE IEEE.std_logic_1164.ALL;
USE IEEE.numeric_std.ALL;

entity RAM_tb is
end RAM_tb;

architecture Behavioral of RAM_tb is
    component RAM port(Clk : in std_logic;
                       addr1 : in std_logic_vector({{ADDRLENGTH}}  downto 0); --address
                       addr2 : in std_logic_vector({{ADDRLENGTH}}  downto 0); --address
                       en_read1 : in std_logic; -- read-enable
                       en_read2 : in std_logic; -- read-enable
                       en_write : in std_logic; -- write-enable
                       input : in std_logic_vector({{WRITELENGTH}} downto 0);  --input
                       output1 : out  std_logic_vector({{READLENGTH}} downto 0);  --output
                       output2 : out std_logic_vector({{READLENGTH}} downto 0));  --output
    end component;

    signal Clk : std_logic := '0'; --clock signal
    signal addr1 : std_logic_vector({{ADDRLENGTH}}  downto 0) := (others => '0'); --address
    signal addr2 : std_logic_vector({{ADDRLENGTH}}  downto 0) := (others => '0'); --address
    signal en_read1 : std_logic := '0'; -- read-enable
    signal en_read2 : std_logic := '0'; -- read-enable
    signal en_write : std_logic := '0'; -- write-enable
    signal input : std_logic_vector({{WRITELENGTH}} downto 0) := (others => '0');  --input
    signal output1 : std_logic_vector({{READLENGTH}} downto 0) := (others => '0');  --output
    signal output2 : std_logic_vector({{READLENGTH}} downto 0) := (others => '0');  --output
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

        constant zero_out : std_logic_vector({{READLENGTH}} downto 0) := (others => '0');
        constant Z_out : std_logic_vector({{READLENGTH}} downto 0) := (others => 'Z');
        constant U_out : std_logic_vector({{READLENGTH}} downto 0) := (others => 'U');
           --to_string function for report
           function to_string ( a: std_logic_vector) return string is
                    variable b : string (a'length downto 1) := (others => '0');
            begin
                    for i in a'length downto 1 loop
                    b(i) := std_logic'image(a((i-1)))(2);
                    end loop;
                return b;
            end function;

        type random_array is array (0 to 15) of std_logic_vector({{ADDRLENGTH}} downto 0);
        constant random_addr : random_array :=(
                                    {{RANDOM_ADDR}});

        type content_array_in is array (0 to 15) of std_logic_vector({{WRITELENGTH}} downto 0);
        constant content_in : content_array_in :=(
        					       {{CONTENT_IN1}});
        type content_array_out is array (0 to 15) of std_logic_vector({{READLENGTH}} downto 0);
        constant content_out : content_array_out :=(
                                   {{CONTENT_OUT1}});

        constant content_test_in : content_array_in :=(
                                                {{CONTENT_IN2}});
        constant content_test_out : content_array_out :=(
                                                {{CONTENT_OUT2}});
begin

    --------------------check the ROM------------------------
     -- the output should be "ZZZ.." when control signals are zero
     en_read2 <= '0';
     wait for Clk_period;
     if (output2/=Z_out and output2/=U_out) then
        report "§{The ouput2 is '" & to_string(std_logic_vector(output2)) & "'. However, output2 should be high impedance (Z) when nothing is read from the memory using en_read2 operation.}§" severity failure;
     elsif (output2/=Z_out and output2=U_out) then
        report "§{Probably, you did not assign or use the output signal 'output2' correctly.}§" severity failure;
     end if;

     en_read1 <= '0';
     wait for Clk_period;
       if (output1/=Z_out and output1/=U_out) then
        report "§{The ouput1 is '" & to_string(std_logic_vector(output1)) & "'. However, However, output1 should be high impedance (Z) when nothing is read from the memory using en_read1 operation.}§" severity failure;
     elsif (output1/=Z_out and output1=U_out) then
           report "§{Probably, you did not assign or use the output signal 'output1' correctly.}§" severity failure;
     end if;

    --check the size of RAM
     en_write <= '1';
     en_read1 <= '0';
     en_read2 <= '0';
     if ({{WRITELENGTH}}+1)/({{DATASIZE}})=2 then
        addr1 <= std_logic_vector(to_unsigned((2**({{ADDRLENGTH}}+1)-2),{{ADDRLENGTH}}+1));
     else
        addr1 <= std_logic_vector(to_unsigned((2**({{ADDRLENGTH}}+1)-1),{{ADDRLENGTH}}+1));
     end if;     input <= content_in(1);
     wait for Clk_period;

     -- check both read lines

     --when write is enabled only
     ---------------------------

     for i in random_addr'range loop
        en_write <= '1';
        en_read1 <= '0';
        en_read2 <= '0';
        addr1 <= random_addr(i);
        input <= content_in(i);
        wait for Clk_period;
        if (output1/=Z_out and output2/=Z_out) then
            report "§{In your code, the outputs are not high impedance (Z) when only en_write is enabled.}§" severity failure;
        end if;


        ------- to force output2 be non-Z
        en_write <= '0';
        en_read1 <= '0';
        en_read2 <= '1';
        addr2 <= random_addr(1);
        wait for Clk_period;
        --------
        --check to see the data is written to the memory
        en_write <= '0';
        en_read1 <= '1';
        en_read2 <= '0';
        addr1 <= random_addr(i);
        addr2 <= random_addr(i);
        input <= content_test_in(i);
        wait for Clk_period;
        if (output1/=content_out(i)) then
            report "§{The data cannot be written to the memory correctly when only en_write is enabled. Or, the content of memory cannot be read when en_read1 is enabled.}§" severity failure;
        elsif (output2/=Z_out) then
            report "§{In your code, output2 is not high impedance (Z) when only en_read1 is enabled.}§" severity failure;
        end if;

        --when read1 is active, the data should not be written to the memory
        addr1 <= random_addr(i);
        wait for Clk_period;
        if (output1=content_test_out(i) and content_test_out(i)/=content_out(i)) then
            report "§{The input is written to the memory when only en_read1 is enabled.}§" severity failure;
	end if;

        -- check if en_write and en_read2 are working correctly
        en_read1 <= '0';
        en_read2 <= '1';
        addr1 <= random_addr(15-i);
        addr2 <= random_addr(i);
        input <= content_test_in(i);
        wait for Clk_period;
        if (output2/=content_out(i)) then
            report "§{The content of memory cannot be read when en_read2 is enabled.}§" severity failure;
        elsif (output1/=Z_out) then
                report "§{In your code, output1 is not high impedance (Z) when only en_read2 are enabled}§" severity failure;
        end if;

        --when read2 is active, the data should not be read from the memory
        addr2 <= random_addr(15-i);
        wait for Clk_period;
        if (output2=content_test_out(i) and content_test_out(i)/=content_out(15-i) and content_test_out(i)/=zero_out) then
            report "§{The input is written to the memory when only en_read2 is enabled.}§" severity failure;
	end if;

     end loop;


     -- check if higher significant half of input is not written in the memory correctly
     -----------------------------------------------------------------------------------
     en_read1 <= '0';
     en_write <= '0';
     en_read2 <= '1';

     for i in random_addr'range loop
        if ({{WRITELENGTH}}+1)/({{DATASIZE}})=2 then

         if ({{READLENGTH}}+1)/({{DATASIZE}})=2 then
             addr2 <= std_logic_vector(to_unsigned(to_integer(unsigned(random_addr(i)))+1, {{ADDRLENGTH}}+1));
             wait for Clk_period;
             if (output2({{DATASIZE}}-1 downto 0)/=content_in(i)({{WRITELENGTH}} downto {{DATASIZE}})) then
                 report "§{The upper half of input is not written to the memory correctly when only en_write is enabled. Note that the length of input is twice the length of each memory cell.}§" severity failure;
             end if;
         end if;

        if ({{READLENGTH}}+1)/({{DATASIZE}})=1 then
            addr2 <= std_logic_vector(to_unsigned(to_integer(unsigned(random_addr(i)))+1, {{ADDRLENGTH}}+1));
            wait for Clk_period;
            if (output2/=content_in(i)({{WRITELENGTH}} downto {{READLENGTH}}+1)) then
                report "§{The upper half of input is not written to the memory correctly when only en_write is enabled.}§" severity failure;
            end if;
        end if;
      end if;
     end loop;

     -- read 1 and write should not be active at the same time
     ---------------------------------------------------------
     en_read2 <= '0';
     for i in random_addr'range loop
         en_write <= '1';
         en_read1 <= '1';
         addr1 <= random_addr(i);
         input <= content_test_in(i);
         wait for Clk_period;

         if (output1/=Z_out) then
            report "§{The outputs of your RAM are not high impedance (Z), when en_read1 and en_write are enabled at the same time. In this case, nothing should be read from the memory.}§" severity failure;
         end if;
         -- check that the data which is read is the previous one
         en_write <= '0';
         wait for Clk_period;
         if (output1/=content_out(i)) then
            report "§{In your code, the input is written to the RAM when en_read1 and en_write are enabled. But, the content of the RAM must not be changed and the outputs shall be high impedance (Z) in this case.}§" severity failure;
         end if;
     end loop;


     -- check if both read lines work together correctly from different addresses
     ----------------------------------------------------------------------------

     ------- to make the output high impedance
     en_read1 <= '0';
     en_read2 <= '0';
     en_write <= '0';
     wait for Clk_period;
     -----

     for i in random_addr'range loop
         en_read1 <= '1';
         en_read2 <= '1';
         en_write <= '0';
         addr1 <= random_addr(i);
         addr2 <= random_addr(15-i);
         input <= content_test_in(i);
         wait for Clk_period;
         if (output1/=content_out(i)) then
            report "§{In your code, the data is not read correctly from address addr1 of the RAM when both en_read1 and en_read2 are enabled.}§" severity failure;
         elsif output2/=content_out(15-i) then
            report "§{In your code, the data is not read correctly from address addr2 of the RAM when both en_read1 and en_read2 are enabled.}§" severity failure;
         end if;

         en_read2 <= '0';
         addr1 <= random_addr(i);
         if (output2=content_test_out(i) and content_test_out(i)/=content_out(i)) then
            report "§{In your code, the input is written to the RAM when both en_read1 and en_read2 are enabled.}§" severity failure;
         end if;
     end loop;


     -- check both read lines from the same address
     en_write <= '0';
     en_read1 <= '1';
     en_read2 <= '1';
     addr1 <= random_addr(0);
     addr2 <= random_addr(0);
     wait for Clk_period;
     if (output1/=content_out(0)) then
         report "§{In your code, the data is not read correctly from address addr1 of the RAM when both en_read1 and en_read2 are enabled and reading from the same address.}§" severity failure;
     elsif (output2/=content_out(0)) then
         report "§{In your code, the data is not read correctly from address addr2 of the RAM when both en_read1 and en_read2 are enabled and reading from the same address.}§" severity failure;
     end if;


     -- it is not possible both reading to and writing from the same address
     -----------------------------------------------------------------------
     en_read1 <= '0';
     for i in 0 to 5 loop
         en_read2 <= '1';
         en_write <= '1';
         addr1 <= random_addr(i);
         addr2 <= random_addr(i);
         input <= content_test_in(i);
         wait for Clk_period;
         if (output1/=Z_out and output2/=Z_out) then
            report "§{The outputs of your RAM are not high impedance (Z), when en_read2 and en_write are enabled and operating on the same address at the same time.}§" severity failure;
         end if;
         -- check that the data which is read is the previous one
         en_write <= '0';
         wait for Clk_period;
         if (output2/=content_out(i)) then
            report "§{In your code, the input is written to the RAM when both en_read2 and en_write are enabled operating on the same address. But, the content of the RAM must not be changed and the outputs shall be high impedance (Z) in this case.}§" severity failure;
         end if;
     end loop;



      for i in 0 to 5 loop
        en_read2 <= '1';
        en_write <= '1';
	addr1 <= std_logic_vector(to_unsigned(to_integer(unsigned(random_addr(i)))+1, {{ADDRLENGTH}}+1));
	addr2 <= random_addr(i);
	input <= content_test_in(i);
	wait for Clk_period;
	if (output1/=Z_out) then
	    report "§{In your code, the output is not high impedance (Z) when en_read2 and en_write are enabled and addr1 is equal to the next higher address of addr2 (addr1=addr2+1). But, the content of the RAM must not be changed and the outputs shall be high impedance (Z) in this case.}§" severity failure;
	end if;
	-- check that the data which is read is the previous one
         en_write <= '0';
         addr2 <= random_addr(i);
	wait for Clk_period;
	if  ({{READLENGTH}}+1)/({{DATASIZE}})=1 then
	  if (output2/=content_out(i)) then
	    report "§{In your code, the content of RAM changes when en_read2 and en_write are enabled and addr1 is equal to the next higher address of addr2 (addr1=addr2+1). But, the content of the RAM must not be changed and the outputs shall be high impedance (Z) in this case.}§" severity failure;
	  end if;
	elsif ({{READLENGTH}}+1)/({{DATASIZE}})=2 then
	   en_read2 <= '1';
	   addr2 <= std_logic_vector(to_unsigned(to_integer(unsigned(random_addr(i)))+1, {{ADDRLENGTH}}+1));
	   wait for Clk_period;
	   if (output2=content_test_in(i)({{DATASIZE}}-1 downto 0)) then
	      report "§{In your code, the input is not written to the RAM correctly when both en_write and en_read2 are enabled and addr1 is equal to the next higher address of addr2 (addr1=addr2+1).}§" severity failure;
	  end if;
	end if;
      end loop;

     ---to have a proper data in the RAM
   en_read1 <= '0';
   en_read2 <= '0';
   en_write <= '1';
   for i in random_addr'range loop
      addr1 <= random_addr(i);
      input <= (others => '0');
      wait for Clk_period;
      addr1 <= std_logic_vector(to_unsigned(to_integer(unsigned(random_addr(i)))+1, {{ADDRLENGTH}}+1));
      wait for Clk_period;
   end loop;
   for i in random_addr'range loop
      addr1 <= random_addr(i);
      input <= content_in(i);
      wait for Clk_period;
   end loop;
   --------


      for i in 0 to 5 loop
         en_read2 <= '1';
         en_write <= '1';
	addr1 <= random_addr(i);
	addr2 <= std_logic_vector(to_unsigned(to_integer(unsigned(random_addr(i)))+1, {{ADDRLENGTH}}+1));
	input <= content_test_in(i);
	wait for Clk_period;
	if (output1/=Z_out) then
	  report "§{In your code, the output is not high impedance (Z) when en_read2 and en_write are enabled and addr2 is equal to the next higher address of addr1 (addr2=addr1+1). But, the content of the RAM must not be changed and the outputs shall be high impedance (Z) in this case.}§" severity failure;
	end if;
	-- check that the data which is read is the previous one
         en_write <= '0';
         addr2 <= random_addr(i);
	wait for Clk_period;
	if  ({{WRITELENGTH}}+1)/({{DATASIZE}})=2 then
	  if (output2/=content_out(i)) then
	    report "§{In your code, the content of RAM changes when en_read2 and en_write are enabled and addr2 is equal to the next higher address of addr1 (addr2=addr1+1). But, the content of the RAM must not be changed and the outputs shall be high impedance (Z) in this case.}§" severity failure;
	  end if;
	elsif  ({{WRITELENGTH}}+1)/({{DATASIZE}})=1 then
	   if (output2/=content_test_out(i)) then
            report "§{In your code, the input is not written to the RAM correctly when both en_write and en_read2 are enabled and addr2 is equal to the next higher address of addr1 (addr2=addr1+1).}§" severity failure;
	   end if;
	end if;
    end loop;

    ---to have a proper data in the RAM
   en_read1 <= '0';
   en_read2 <= '0';
   en_write <= '1';
   for i in random_addr'range loop
      addr1 <= random_addr(i);
      input <= (others => '0');
      wait for Clk_period;
      addr1 <= std_logic_vector(to_unsigned(to_integer(unsigned(random_addr(i)))+1, {{ADDRLENGTH}}+1));
      wait for Clk_period;
   end loop;
   for i in random_addr'range loop
      addr1 <= random_addr(i);
      input <= content_in(i);
      wait for Clk_period;
   end loop;

    -- check if both write and read2 work together correctly to different addresses
    -------------------------------------------------------------------------------
    en_read1 <= '0';
    en_read2 <= '0';
    en_write <= '1';
    addr1 <= random_addr(0);
    input <= content_test_in(0);
    wait for Clk_period;

    ------- to force the output1 be non-Z
    en_read1 <= '1';
    en_read2 <= '0';
    en_write <= '0';
    addr1 <= random_addr(0);
    wait for Clk_period;
    --------
    for i in 1 to 15 loop
        en_read1 <= '0';
        en_read2 <= '1';
        en_write <= '1';
        addr2 <= random_addr(i-1);
        addr1 <= random_addr(i);
        input <= content_test_in(i);
        wait for Clk_period;
        -- check that the data which is read is the previous one
        if (output2/=content_test_out(i-1)) then
           report "§{In your code, the data is not read correctly from address addr2 of the RAM when both en_write and en_read2 are enabled and operating on two different addresses at the same time.}§" severity failure;
        end if;
        if (output1/=Z_out) then
            report "§{In your code, output1 is not high impedance (Z) when en_read2 and en_write are enabled.}§" severity failure;
        end if;


	-- check if the input is written to the memory correctly or not
	en_read1 <= '0';
	en_write <= '0';
	en_read2 <= '1';
	addr2 <= random_addr(i);
	wait for Clk_period;
	if (output2/=content_test_out(i)) then
	    report "§{In your code, the input is not written to the RAM correctly when both en_write and en_read2 are enabled and operating on two different addresses at the same time.}§" severity failure;
	end if;
     end loop;
     -- check if higher significant half of input is not written in the memory correctly
     for i in random_addr'range loop
        if ({{WRITELENGTH}}+1)/({{DATASIZE}})=2 then
        if ({{READLENGTH}}+1)/({{DATASIZE}})=1 then
            addr2 <= std_logic_vector(to_unsigned(to_integer(unsigned(random_addr(i)))+1, {{ADDRLENGTH}}+1));
            wait for Clk_period;
            if (output2/=content_test_in(i)({{WRITELENGTH}} downto {{READLENGTH}}+1)) then
                report "§{The upper half of input is not written to the memory correctly when both en_write and en_read2 are enabled.}§" severity failure;
            end if;
        end if;
       end if;
     end loop;


     -- when all enable signals are active
     -------------------------------------
     for i in 0 to 5 loop
         en_read1 <= '1';
         en_read2 <= '1';
         en_write <= '1';
         addr1 <= random_addr(i);
         addr2 <= random_addr(15-i);
         input <= content_in(i);
         wait for Clk_period;
         if (output1/=Z_out or output2/=Z_out) then
            report "§{In your code, the outputs is not high impedance (Z) when all enable signals are enabled at the same time.}§" severity failure;
         end if;

         en_read1 <= '1';
         en_read2 <= '0';
         en_write <= '0';
         addr1 <= random_addr(i);
         wait for Clk_period;
         if (output1/=content_test_out(i)) then
            report "§{In your code, the input is written to the RAM when all enable signals are enabled. But, the content of the RAM must not be changed and the outputs shall be high impedance (Z) in this case.}§" severity failure;
         end if;

     end loop;

      ------- to force the output1 and output2 to be non-Z
      en_write <= '0';
      en_read1 <= '1';
      en_read2 <= '1';
      addr1 <= random_addr(0);
      addr2 <= random_addr(1);
      wait for Clk_period;
      --------

      for i in random_addr'range loop
         en_write <= '1';
         en_read1 <= '0';
         en_read2 <= '0';
         addr1 <= random_addr(i);
         input <= content_in(i);
         wait for Clk_period;
         if (output1/=Z_out or output2/=Z_out) then
             report "§{In your code, the outputs are not high impedance (Z) when only en_write is enabled.}§" severity failure;
         end if;
    end loop;


     report "Success" severity failure;

   end process;

end Behavioral;
