library IEEE;
use IEEE.STD_LOGIC_1164.all;
use IEEE.NUMERIC_STD.all;
 
entity register_file_tb is
end register_file_tb;
 
architecture Behavioral of register_file_tb is
 
    -- Component Declaration for the Unit Under Test (UUT)
 
    component register_file
    port(
         IN1    : in  std_logic_vector((%%n - 1) downto 0);
         WA1    : in  std_logic_vector((%%address_width_n - 1) downto 0);
         WE1    : in  std_logic;
         
         IN2    : in  std_logic;
         WA2    : in  std_logic_vector((%%address_width_reg0 - 1) downto 0);
         WE2    : in  std_logic;
         
         RA1    : in  std_logic_vector((%%address_width_n - 1) downto 0);
         
         CLK    : in  std_logic;
         
         Output : out std_logic_vector((%%n - 1) downto 0)
        );
    end component;
    

   -- Inputs
   signal CLK : std_logic := '0';
   signal IN1 : std_logic_vector((%%n - 1) downto 0) := (others => '0');
   signal RA1 : std_logic_vector((%%address_width_n - 1) downto 0) := (others => '0');
   signal WA1 : std_logic_vector((%%address_width_n - 1) downto 0) := (others => '0');
   signal WE1 : std_logic := '0';
   signal IN2 : std_logic := '0';
   signal WA2 : std_logic_vector((%%address_width_reg0 - 1) downto 0) := (others => '0');
   signal WE2 : std_logic := '0';

   -- Outputs
   signal Output : std_logic_vector((%%n - 1) downto 0);

   -- Clock period definitions
   constant CLK_period : time := 20 ns;
   
   -- number of n bit wide registers:
   constant N_n : integer := %%N_n;
   
   -- number of flags to store in special reg 0:
   constant special_reg0_size : integer := %%special_reg0_size;
   
   -- number of addresses we need for testing:
   constant address_array_size: integer := %%address_array_size;
   
   -- bit width of the addresses for register with width n
   constant address_width_n : integer := %%address_width_n;
   
   -- bit width of the addresses for the special register 0
   constant address_width_reg0:integer:= %%address_width_reg0;
   
   -- if 0: bypass, if 1: read priority  on simultaneous read and write from the same register
   constant n_bypass_or_read_priority : std_logic := '%%n_bypass_or_read_priority';
   
   -- if 0: bypass, if 1: read priority  on simultaneous read and write from the same register
   constant reg0_bypass_or_read_priority : std_logic := '%%reg0_bypass_or_read_priority';
   
   -- test vectors for n bit wide register bank:
   type type_n_test_data_array is array(0 to ((2 * N_n) - 1)) of std_logic_vector((%%n - 1) downto 0);
   signal data_n_test_array : type_n_test_data_array := (%%data_n_test_array);
      
   -- test vectors for the special register 0:
   signal reg0_test_vector_1 : std_logic_vector(((special_reg0_size)-1) downto 0) := "%%reg0_test_vector_1";
   signal reg0_test_vector_2 : std_logic_vector(((special_reg0_size)-1) downto 0) := "%%reg0_test_vector_2";
   
   -- array containing the addresses needed for testing:
   type type_test_address_array is array(0 to (address_array_size - 1)) of std_logic_vector((%%address_array_width - 1) downto 0);
   signal address_test_array : type_test_address_array := (%%address_test_array);
 
begin
 
   -- Instantiate the Unit Under Test (UUT)
   uut: register_file port map (
          IN1 => IN1,
          WA1 => WA1,
          WE1 => WE1,
          IN2 => IN2,
          WA2 => WA2,
          WE2 => WE2,
          RA1 => RA1,
          CLK => CLK,
          Output => Output
        );
        
        
   test_register_bank_beh: process
   
   begin
   
   --------------------------------------
   -- Check general-purpose registers: --
   --------------------------------------
   WE2 <= '0';

      -- write:
      WE1 <= '1';
      for i in 0 to (N_n - 1) loop
         IN1 <= data_n_test_array(i);
         WA1 <= address_test_array(i)((address_width_n - 1) downto 0);
         RA1 <= address_test_array(N_n - 1)((address_width_n - 1) downto 0);
         
         if i = N_n - 1 then  -- avoid writing to currently output register address
            RA1 <= (others => '0');
         end if;
         
         wait for CLK_period;
         
      end loop;
      report "Writing n bit first test data... done";
   
   
      -- read:
      WE1 <= '0';
      for i in 0 to (N_n - 1) loop
         RA1 <= address_test_array(i)((address_width_n - 1) downto 0);
         
         wait for CLK_period;
         
         if i = 0 then
            if Output /= data_n_test_array(i) then  -- there should be no senseful data in register 0 for now
               report "good";
            else
               report "Data was written to register 0 using IN1 as input. This should not be possible." severity failure;
            end if;
         else
            if Output = data_n_test_array(i) then
               report "good";
            else
               report "The data written to the registers did not match the read data." severity failure;
            end if;
         end if;
         
      end loop;
      
      
      -- write without enabling write:
      WE1 <= '0';
      for i in 0 to (N_n - 1) loop
         IN1 <= data_n_test_array(i + N_n);
         WA1 <= address_test_array(i)((address_width_n - 1) downto 0);
         
         wait for CLK_period;
         
      end loop;
      report "Writing n bit second test data... done";
   
   
      -- read from writes which were not enabled:
      WE1 <= '0';
      for i in 0 to (N_n - 1) loop
         RA1 <= address_test_array(i)((address_width_n - 1) downto 0);
         
         wait for CLK_period;
         
         if Output /= data_n_test_array(i + N_n) then  -- there should be no new data
            report "good";
         else
            report "Data was written although the WE1 bit was not set." severity failure;
         end if;
         
      end loop;
      
   
      -- write & read simultaneously
      WE1 <= '1';
      for i in 0 to (N_n - 1) loop
         IN1 <= data_n_test_array(i + N_n);
         WA1 <= address_test_array(i)((address_width_n - 1) downto 0);
         RA1 <= address_test_array(i)((address_width_n - 1) downto 0);
         
         wait for CLK_period;
         
         if n_bypass_or_read_priority = '0' then    -- bypass check
            if i = 0 then
               if Output /= data_n_test_array(i + N_n) then  -- there should be no senseful data in register 0 for now
                  report "good";
               else
                  report "Data was written to register 0 using IN1 as input. This should not be possible." severity failure;
               end if;
            else
               if Output = data_n_test_array(i + N_n) then
                  report "good";
               else
                  report "On a simultaneous read and write from the same register, the input IN1 was not bypassed immediately to the Output." severity failure;
               end if;
            end if;
         elsif n_bypass_or_read_priority = '1' then    -- read priority check
            if i = 0 then
               if Output /= data_n_test_array(i) then  -- there should be no senseful data in register 0 for now
                  report "good";
               else
                  report "Data was written to register 0 using IN1 as input. This should not be possible." severity failure;
               end if;
            else
               if Output = data_n_test_array(i) then
                  report "good";
               else
                  report "On a simultaneous read and write from the same register, the input IN1 was not passed through at the next rising edge of the CLK signal to the Output." severity failure;
               end if;
            end if;
         end if;
            
      end loop;
      WE1 <= '0';
      
      
      -- read again:
      WE1 <= '0';
      for i in 0 to (N_n - 1) loop
         RA1 <= address_test_array(i)((address_width_n - 1) downto 0);
         
         wait for CLK_period;
         
         if i = 0 then
            if Output /= data_n_test_array(i + N_n) then  -- there should be no senseful data in register 0 for now
               report "good";
            else
               report "Data was written to register 0 using IN1 as input. This should not be possible." severity failure;
            end if;
         else
            if Output = data_n_test_array(i + N_n) then
               report "good";
            else
               report "After a simultaneous read and write from the same register, the written data could not be read out." severity failure;
            end if;
         end if;
         
      end loop;
      
   ------------------------------
   -- Check special register 0 --
   ------------------------------
   WE1 <= '0';
   
      -- write:
      WE2 <= '1';
      for i in 0 to (special_reg0_size - 1) loop
         IN2 <= reg0_test_vector_1(i);
         WA2 <= address_test_array(i)((address_width_reg0 - 1) downto 0);
         
         wait for CLK_period;
         
      end loop;
      report "Writing reg 0 first test data... done";
      
      
      -- read:
      WE2 <= '0';
      RA1 <= (others => '0');
         
      wait for CLK_period;
         
      if Output((special_reg0_size - 1) downto 0) = reg0_test_vector_1 then
         report "good";
      else
         report "The data written to the special register 0 did not match the read out data." severity failure;
      end if;
      
      
      RA1 <= std_logic_vector(to_unsigned(1, RA1'length)); -- set read address not to 0 so that the following write test is no read & write test  
   
   
      -- write without enabling write:
      WE2 <= '0';
      for i in 0 to (special_reg0_size - 1) loop
         IN2 <= reg0_test_vector_2(i);
         WA2 <= address_test_array(i)((address_width_reg0 - 1) downto 0);
         
         wait for CLK_period;
         
      end loop;
      report "Writing reg 0 second test data... done";

      
      -- read from writes which were not enabled:
      WE2 <= '0';
      
      RA1 <= (others => '0');
      
      wait for CLK_period;
      
      if Output((special_reg0_size - 1) downto 0) /= reg0_test_vector_2 then  -- there should be no new data
         report "good";
      else
         report "Data was written to register 0 although the WE2 bit was not set." severity failure;
      end if;  
      
      
      -- write & read simultaneously:
      WE2 <= '1';
      for i in 0 to (special_reg0_size - 1) loop
         IN2 <= reg0_test_vector_2(i); -- "+special_reg0_size" to use the unique second half of the test data
         WA2 <= address_test_array(i)((address_width_reg0-1) downto 0);
         RA1 <= (others => '0');
         
         wait for CLK_period;
         
         if reg0_bypass_or_read_priority = '0' then    -- bypass check
            if Output(i) = reg0_test_vector_2(i) then
               report "good";
            else
               report "On a simultaneous read and write from the special register 0, the input IN2 was not bypassed immediately to the Output." severity failure;
            end if;
         elsif reg0_bypass_or_read_priority= '1' then    -- read priority check
            if Output(i) = reg0_test_vector_1(i) then
               report "good";
            else
               report "On a simultaneous read and write from the special register 0, the input IN2 was not passed through at the next rising edge of the CLK signal to the Output." severity failure;
            end if;
         end if;
      
      end loop;
      
      
      -- read again:
      WE2 <= '0';
      RA1 <= (others => '0');
         
      wait for CLK_period;
      
      if Output((special_reg0_size - 1) downto 0) = reg0_test_vector_2 then
         report "good";
      else
         report "After a simultaneous read and write from special register 0, the written data could not be read out again." severity failure;
      end if;
      
      
      
      report "Success" severity failure;
   end process test_register_bank_beh;

   -- Clock process definitions
   CLK_process :process
   begin
      CLK <= '0';
      wait for CLK_period/2;
      CLK <= '1';
      wait for CLK_period/2;
   end process;
 
end;

