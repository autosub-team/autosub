LIBRARY IEEE;
USE IEEE.std_logic_1164.ALL;
USE IEEE.numeric_std.ALL;

ENTITY ALU_tb IS
END ALU_tb;

ARCHITECTURE behavior OF ALU_tb IS

   signal Clk,enable : std_logic := '0'; --clock signal and enable
   signal A,B : unsigned(3 downto 0) := (others => '0'); --input operands
   signal slc : std_logic_vector(1 downto 0) := (others => '0'); --Operation to be performed
   signal R : unsigned(3 downto 0) := (others => '0');  --output of ALU
   signal flag : std_logic := '0'; --flag (carry,sign,zero or parity)
   constant Clk_period : time := 10 ns;

BEGIN

    -- Instantiate the Unit Under Test (UUT)
   UUT: entity work.ALU port map (
          Clk => Clk, enable => enable, slc => slc, A => A, B => B, flag => flag, R => R);

   -- Clock process definitions
   Clk_process :process
   begin
        Clk <= '0';
        wait for Clk_period/2;
        Clk <= '1';
        wait for Clk_period/2;
   end process;
   
   -- Stimulus process
   stim_proc: process
                                
            --selector
            type selector is array (0 to 3) of std_logic_vector(1 downto 0);
            constant slcr : selector :=("00","01","10","11");
            --inputs
            type input_array is array (0 to 15) of unsigned(3 downto 0);
            constant input : input_array :=("0000","0001","0010","0011",
                                            "0100","0101","0110","0111",
                                            "1000","1001","1010","1011",
                                            "1100","1101","1110","1111");
                       
   begin

      -------------------check specification-----------------------
      enable <= '1';
      --wait for Clk_period;
      for l in slcr'range loop
         slc <= slcr(l);   
        --wait for Clk_period*2; --add A and B
             
        for i in input'range loop
            A <= input(i);         
            
            for j in input'range loop 
                B <= input(j);
                wait for Clk_period;
            end loop; 
         end loop;
      end loop;     
      wait;
   end process;

END;