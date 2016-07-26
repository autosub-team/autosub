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
   
	    variable fail : std_logic :='0';
           --to_string function for report
           function to_string ( a: unsigned) return string is
                    variable b : string (a'length downto 1) := (others => '0');
            begin
                    for i in a'length downto 1 loop
                    b(i) := std_logic'image(a((i-1)))(2);
                    end loop;
                return b;
            end function;
            --result of ADD, SUB, AND, OR, XOR and comparator
            type pattern_type_add is record
                     O1,O2,O3 : unsigned(3 downto 0);
                     end record;        
            type out_add_array is array (0 to 16*16-1) of pattern_type_add;
            constant out_add : out_add_array :=(
                    		                  %%RESULT1);
            --result of flag for ADD, SUB, AND, OR, XOR and comparator
            type pattern_type_flag is record
                     F1,F2,F3 : std_logic;
                     end record;
            type flag_array is array (0 to 16*16-1) of pattern_type_flag;
            constant out_flag : flag_array :=(
                                          %%FLAG); 
            --result of Shift instructions         
            type out_shift_array is array (0 to 15) of unsigned(3 downto 0);
            constant out_shift : out_shift_array :=(
                    %%RESULT2); 
            --result of flag Shift instructions 
            type carry_array is array (0 to 15) of std_logic;
            constant out_carry : carry_array :=(
								%%CARRY);                                  
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

      -----------------check enable-----------------------
      --When ALU is disabled and the input changes on the falling edge, 
      --the output should not change on the next rising edge.
   
         
       enable <= '0';        
          for k in slcr'range loop
              slc <= slcr(k);  
              A <= "0101";
              B <= "0111";
              wait for Clk_period/0.9;
              if (R /= "0000") or (flag /='0') then
		 fail :='1';
              end if;             
          end loop; 
          if fail='1' then 
            report " Probebly you did not use the enable signal properly, or there is a problem with using signals and variables" severity failure;
          end if;
          fail :='0';
              
    --------------------check clock cycle------------------------
    --When ALU is enabled and the input changes on the falling edge, 
    --the output should not change.
    enable <= '1';       
    for s in slcr'range loop
        slc <= slcr(s);
        A <= "0000";
        B <= "0000";
        wait until rising_edge(Clk);
        A <= "0101"; 
        B <= "0111";
        wait until falling_edge(Clk); 
        wait for Clk_period/10;
        if (R /="0000") then
	  fail :='1';
        end if;
    end loop;
   
      if fail='1' then 
         report " Probebly ALU is not operating on rising edge of clock cycle, or there is a problem with using signals and variables" severity failure;
      end if;
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
                wait for Clk_period*2;
                           
                --check the result for the first three instructions
                if slc="00" then 
                     if ((R /= out_add(16*i+j).O1) or (flag /=out_flag(16*i+j).F1)) then
                        report " Error for %%INST1 instruction: " &
                                "A=" & to_string(input(i)) & ", B=" & to_string(input(j)) &                                 
                                "; expected R=" & to_string(out_add(16*i+j).O1) &  ", expected flag=" & std_logic'image(out_flag(16*i+j).F1) &
                                ", received R=" & to_string(R) & ", received flag=" & std_logic'image(flag) 
                        severity failure;
                    end if;
                end if;
               
                if slc="01" then 
                   if (R /= out_add(16*i+j).O2) or (flag /=out_flag(16*i+j).F2) then
                        report " Error for %%INST2 instruction: " &
                           "A=" & to_string(input(i)) & ", B=" & to_string(input(j)) &                                 
                           "; expected R=" & to_string(out_add(16*i+j).O2) &  ", expected flag=" & std_logic'image(out_flag(16*i+j).F2) &
                           ", received R=" & to_string(R) & ", received flag=" & std_logic'image(flag) 
                        severity failure;
                    end if;
                end if;
                if slc="10" then 
                    if (R /= out_add(16*i+j).O3) or (flag /=out_flag(16*i+j).F3) then
                        report " Error for %%INST3 instruction: " &
                                "A=" & to_string(input(i)) & ", B=" & to_string(input(j)) &                                                           
                                "; expected R=" & to_string(out_add(16*i+j).O3) &  ", expected flag=" & std_logic'image(out_flag(16*i+j).F3) &
                                ", received R=" & to_string(R) & ", received flag=" & std_logic'image(flag) 
                                severity failure;
                    end if;
                end if;
                -- check result for the last instruction
                if slc="11" then  
                   assert not((R /= out_shift(i)) or (flag /=out_carry(i)))
                        report " Error for %%INST4 instruction: " & "A=" & to_string(input(i)) &
                           "; expected R=" & to_string(out_shift(i)) &  ", expected flag=" & std_logic'image(out_carry(i)) &
                           ", received R=" & to_string(R) & ", received flag=" & std_logic'image(flag) 
                           severity failure;
                end if;             
            end loop;
        end loop; 
      end loop;     
      report "Success" severity failure;
      wait;
   end process;

END;