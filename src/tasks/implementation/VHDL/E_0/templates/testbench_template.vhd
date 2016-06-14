LIBRARY ieee;
USE ieee.std_logic_1164.ALL;
USE ieee.numeric_std.ALL;

ENTITY ALU_tb IS
END ALU_tb;

ARCHITECTURE behavior OF ALU_tb IS

   signal Clk : std_logic := '0';
   signal A,B,R : signed(1 downto 0) := (others => '0');
   signal Op : std_logic := '0';
   constant Clk_period : time := 10 ns;

BEGIN

    -- Instantiate the Unit Under Test (UUT)
   uut: entity work.ALU PORT MAP (
          Clk => Clk, A => A, B => B, Op => Op, R => R);

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
          
          type pattern_type is record
                  A,B,O1,O2 : signed(1 downto 0);
                  end record;
                  
          type pattern_array is array (natural range <>) of pattern_type;
          constant patterns : pattern_array :=(%%TESTPATTERN);
            type selector is array (0 to 1) of std_logic;
            constant slc : selector :=('0','1');
            
   begin
      wait for Clk_period*%%CLK;
      for i in slc'range loop
        Op <= slc(i);  
        --wait for Clk_period; --add A and B       
        for i in patterns'range loop
            A <= patterns(i).A;
            B <= patterns(i).B;
            wait for Clk_period;

            if Op='0' then 
                if R /= patterns(i).O1 then
                    report "Error for %%INST1 instruction: " & 
                            "A=" & std_logic'image(patterns(i).A(1)) &  "," & std_logic'image(patterns(i).A(0)) &  
                            " B=" & std_logic'image(patterns(i).B(1)) & "," & std_logic'image(patterns(i).B(0)) &
                            "; expected R=" & std_logic'image(patterns(i).O1(1)) & "," & std_logic'image(patterns(i).O1(0)) &
                            ", received R=" & std_logic'image(R(1)) & "," & std_logic'image(R(0));                
                    wait;
                 end if;
               end if;
               
              if Op='1' then 
                   if R /= patterns(i).O2 then
                       report "Error for %%INST2 instruction: " &
                               "A=" & std_logic'image(patterns(i).A(1)) & "," & std_logic'image(patterns(i).A(0)) & 
                               " B=" & std_logic'image(patterns(i).B(1)) & "," & std_logic'image(patterns(i).B(0)) &
                               "; expected R=" & std_logic'image(patterns(i).O2(1)) & "," & std_logic'image(patterns(i).O2(0)) &
                               ", received R=" & std_logic'image(R(1)) & "," & std_logic'image(R(0));  
                       wait;
                    end if;
                end if;           
         end loop;
      end loop;      
    
      wait;
   end process;

END;