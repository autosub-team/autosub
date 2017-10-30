LIBRARY IEEE;
USE IEEE.std_logic_1164.ALL;
USE IEEE.numeric_std.ALL;

entity RAM_tb is
end RAM_tb;

architecture Behavioral of RAM_tb is
    component RAM port(Clk : in std_logic;
                       addr1 : in std_logic_vector({{ADDRLENGTH}}  downto 0); --address
                       addr2 : in std_logic_vector({{ADDRLENGTH}}  downto 0); --address
                       en_read : in std_logic; -- read-enable
                       en_write : in std_logic; -- write-enable
                       input : in std_logic_vector({{WRITELENGTH}} downto 0);  --input
                       output : out std_logic_vector({{READLENGTH}} downto 0));  --output
    end component;

    signal Clk : std_logic := '0'; --clock signal
    signal addr1 : std_logic_vector({{ADDRLENGTH}}  downto 0) := (others => '0'); --address
    signal addr2 : std_logic_vector({{ADDRLENGTH}}  downto 0) := (others => '0'); --address

    signal en_read : std_logic := '0'; -- read-enable
    signal en_write : std_logic := '0'; -- write-enable
    signal input : std_logic_vector({{WRITELENGTH}} downto 0) := (others => '0');  --input
    signal output : std_logic_vector({{READLENGTH}} downto 0) := (others => '0');  --output
    constant Clk_period : time := 10 ns;

begin
  -- Instantiate the Unit Under Test (UUT)
 UUT: RAM port map (
        Clk => Clk,
        addr1 => addr1,
        addr2 => addr2,
        en_read => en_read,
        en_write => en_write,
        input => input,
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


    -- 'Z' display on the output
    ----------------------------
    en_read <= '0';
    wait for Clk_period;
     if (output/=Z_out and output/=U_out) then
        report "§{The ouput is '" & to_string(std_logic_vector(output)) & "'. However, the output should be high impedance (Z) when nothing is read from the memory.}§" severity failure;
     elsif (output/=Z_out and output=U_out) then
        report "'" & to_string(std_logic_vector(Z_out)) & "' should be on the output when nothing is read from the memory.}§" severity failure;
     end if;
    --check the size of RAM
     en_write <= '1';
     en_read <= '0';
     if ({{WRITELENGTH}}+1)/({{DATASIZE}})=2 then
        addr1 <= std_logic_vector(to_unsigned((2**({{ADDRLENGTH}}+1)-2),{{ADDRLENGTH}}+1));
     else
        addr1 <= std_logic_vector(to_unsigned((2**({{ADDRLENGTH}}+1)-1),{{ADDRLENGTH}}+1));
     end if;
     input <= content_in(1);
     wait for Clk_period;


    -- first: writing data in the memory
    ------------------------------------
     for i in random_addr'range loop
         en_write <= '1';
         en_read <= '0';
         addr1 <= random_addr(i);
         input <= content_in(i);
         wait for Clk_period;
          if (output/=Z_out) then
             report "§{In your code, the output is not high impedance (Z) when en_read is not enabled.}§" severity failure;
         end if;
     -- check if the data has been written in the memory
         en_write <= '0';
         en_read <= '1';
         addr2 <= random_addr(i);
         wait for Clk_period;

         if (output/=content_out(i)) then
             report "§{The data cannot be written to the memory correctly when only en_write is enabled, or the content of memory cannot be read.}§" severity failure;
         end if;

        if ({{WRITELENGTH}}+1)/({{DATASIZE}})=2 then

         if ({{READLENGTH}}+1)/({{DATASIZE}})=2 then
             addr2 <= std_logic_vector(to_unsigned(to_integer(unsigned(random_addr(i)))+1, {{ADDRLENGTH}}+1));
             wait for Clk_period;
             if (output({{DATASIZE}}-1 downto 0)/=content_in(i)({{WRITELENGTH}} downto {{DATASIZE}})) then
                 report "§{The upper half of input is not written to the memory correctly when en_write is only enabled. Note that the length of input is twice the length of each memory cell.}§" severity failure;
             end if;
         end if;

	 if ({{READLENGTH}}+1)/({{DATASIZE}})=1 then
             addr2 <= std_logic_vector(to_unsigned(to_integer(unsigned(random_addr(i)))+1, {{ADDRLENGTH}}+1));
             wait for Clk_period;
             if (output/=content_in(i)({{WRITELENGTH}} downto {{READLENGTH}}+1)) then
                 report "§{The upper half of input is not written to the memory correctly when en_write is only enabled.}§" severity failure;
             end if;
         end if;

        end if;

     end loop;


     --check read only
     -----------------
      for i in random_addr'range loop
         en_write <= '0';
         en_read <= '1';
         addr1 <= random_addr(i);
         addr2 <= random_addr(i);
         input <= content_test_in(i);
         wait for Clk_period;

     end loop;

      en_write <= '0';
      en_read <= '1';
     for i in random_addr'range loop
         addr2 <= random_addr(i);
         wait for Clk_period;
         if (output=content_test_out(i)) then
             report "§{The input is written to the memory when only en_read is enabled.}§" severity failure;
         end if;
     end loop;
     -- check if read and write can happen at the same time to the same address
     --------------------------------------------------------------------------
     en_write <= '1';
     en_read <= '1';
     for i in random_addr'range loop
         input <= content_test_in(i);
         addr2 <= random_addr(i);
         addr1 <= random_addr(i);
         wait for Clk_period;

         -- check that the data which is read is the previous one

         if (output/=content_out(i)) then
            report "§{In your code, the output is not the previous content of the RAM when both en_read and en_write are enabled.}§" severity failure;
         end if;
         if (output=content_test_out(i)) then
            report "§{In your code, the writing operation is done before the reading operation when both en_read and en_write are enabled.}§" severity failure;
         end if;

     end loop;

    -- now the data which is read should be the new one
     en_write <= '0';
     en_read <= '1';
     for i in random_addr'range loop
         addr2 <= random_addr(i);
         wait for Clk_period;

         if (output/=content_test_out(i)) then
            report "§{In your code, the input is not written to the RAM correctly when both en_read and en_write are enabled.}§" severity failure;
         end if;

        if ({{WRITELENGTH}}+1)/({{DATASIZE}})=2 then

         if ({{READLENGTH}}+1)/({{DATASIZE}})=2 then
             addr2 <= std_logic_vector(to_unsigned(to_integer(unsigned(random_addr(i)))+1, {{ADDRLENGTH}}+1));
             wait for Clk_period;
             if (output({{DATASIZE}}-1 downto 0)/=content_test_in(i)({{WRITELENGTH}} downto {{DATASIZE}})) then
                 report "§{The upper half of input is not written to the memory correctly when both en_read and en_write are enabled.}§" severity failure;
             end if;
         end if;

         if ({{READLENGTH}}+1)/({{DATASIZE}})=1 then
             addr2 <= std_logic_vector(to_unsigned(to_integer(unsigned(random_addr(i)))+1, {{ADDRLENGTH}}+1));
             wait for Clk_period;
             if (output/=content_test_in(i)({{WRITELENGTH}} downto {{READLENGTH}}+1)) then
                 report "§{The upper half of input is not written to the memory correctly when both en_read and en_write are enabled.}§" severity failure;
             end if;
         end if;

       end if;

     end loop;

    -- check if read and write can happen at the same time to different addresses
    -----------------------------------------------------------------------------

    --to make the output be Z
    en_write <= '0';
    en_read <= '0';
    wait for Clk_period;
    ---

    en_read <= '1';
    en_write <= '1';
    for i in 1 to 15 loop

        addr2 <= random_addr(i);
        addr1 <= random_addr(i-1);
        input <= content_in(i-1);
        wait for Clk_period;
        -- check that the data which is read is the previous one
        if (output/=content_test_out(i)) then
           report "§{In your code, the content of RAM is not the value before the writing operation or cannot be read correctly when both en_read and en_write are enabled.}§" severity failure;
        end if;

    end loop;
    en_read <= '0';
    en_write <= '1';

    addr1 <= random_addr(15);
    input <= content_in(15);
    wait for Clk_period;

     -- check if higher significant half of input is not written to the memory correctly
     en_write <= '0';
     en_read <= '1';
     for i in random_addr'range loop

        addr2 <= random_addr(i);
        wait for Clk_period;
        -- check that the data which is read is the previous one
        if (output/=content_out(i)) then
           report "§{In your code, the input is not written to the RAM correctly when both en_read and en_write are enabled and operating on two different addresses at the same time.}§" severity failure;
        end if;

        if ({{WRITELENGTH}}+1)/({{DATASIZE}})=2 then

         if ({{READLENGTH}}+1)/({{DATASIZE}})=2 then
            addr2 <= std_logic_vector(to_unsigned(to_integer(unsigned(random_addr(i)))+1, {{ADDRLENGTH}}+1));
            wait for Clk_period;
            if (output({{DATASIZE}}-1 downto 0)/=content_in(i)({{WRITELENGTH}} downto {{DATASIZE}})) then
                report "§{The upper half of input is not written to the memory correctly when both en_read and en_write are enabled. " severity failure;
            end if;
        end if;

     if ({{READLENGTH}}+1)/({{DATASIZE}})=1 then
            addr2 <= std_logic_vector(to_unsigned(to_integer(unsigned(random_addr(i)))+1, {{ADDRLENGTH}}+1));
            wait for Clk_period;
            if (output/=content_in(i)({{WRITELENGTH}} downto {{READLENGTH}}+1)) then
                report "§{The upper half of input is not written to the memory correctly when both en_read and en_write are enabled.}§" severity failure;
            end if;
        end if;
      end if;
     end loop;


     report "Success" severity failure;

   end process;

end Behavioral;
