LIBRARY IEEE;
USE IEEE.std_logic_1164.ALL;
USE IEEE.numeric_std.ALL;

ENTITY ALU_tb IS
END ALU_tb;

ARCHITECTURE behavior OF ALU_tb IS
    component ALU port(Clk,enable : in std_logic; --clock signal and enable
			A,B : in std_logic_vector(3 downto 0); --input operands
			slc : in std_logic_vector(1 downto 0); --Operation to be performed
			R : out std_logic_vector(3 downto 0);  --output of ALU
			flag : out std_logic); --clock signal;
    end component;

   signal Clk,enable : std_logic := '0'; --clock signal and enable
   signal A,B : std_logic_vector(3 downto 0) := (others => '0'); --input operands
   signal slc : std_logic_vector(1 downto 0) := (others => '0'); --Operation to be performed
   signal R : std_logic_vector(3 downto 0) := (others => '0');  --output of ALU
   signal flag : std_logic := '0'; --flag (carry,sign,zero or parity)
   constant Clk_period : time := 10 ns;

BEGIN

    -- Instantiate the Unit Under Test (UUT)
   UUT: ALU port map (
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
	    variable count : std_logic :='0';
	    variable out_1,out_2,out_3 : std_logic_vector(3 downto 0);
           --to_string function for report
           function to_string ( a: std_logic_vector) return string is
                    variable b : string (a'length downto 1) := (others => '0');
            begin
                    for i in a'length downto 1 loop
                    b(i) := std_logic'image(a((i-1)))(2);
                    end loop;
                return b;
            end function;         
            
            --result of ADD, SUB, AND, OR, XOR and comparator
            type pattern_type_add is record
                     O1,O2,O3 : std_logic_vector(3 downto 0);
                     end record;        
            type out_add_array is array (0 to 255) of pattern_type_add;
            constant out_add : out_add_array :=(
                    		                  %%RESULT1);
            --result of flag for ADD, SUB, AND, OR, XOR and comparator
            type pattern_type_flag is record
                     F1,F2,F3 : std_logic;
                     end record;
            type flag_array is array (0 to 255) of pattern_type_flag;
            constant out_flag : flag_array :=(
                                          %%FLAG); 
            --result of Shift instructions         
            type out_shift_array is array (0 to 15) of std_logic_vector(3 downto 0);
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
            type input_array is array (0 to 15) of std_logic_vector(3 downto 0);
            constant input : input_array :=("0000","0001","0010","0011",
                                            "0100","0101","0110","0111",
                                            "1000","1001","1010","1011",
                                            "1100","1101","1110","1111");
                       
   begin
              
      -------------------check specification-----------------------
      enable <= '1';
      fail :='0';
      ----- first instruction
      slc <= "00"; 
      count := '0';      
             
      for i in input'range loop
	    A <= input(i);         
            
        for j in input'range loop 
	      B <= input(j);
          wait for Clk_period*2;
          wait for Clk_period/10;
          if count = '0' then           
            --first instruction
             if (R = "UUUU" or flag ='U') then
                report "§{The output is 'UUUU'. Probably, you have not correctly assigned output signal 'R' or 'flag' or enable signal.}§" severity failure;
                      
	         elsif (((R /= out_add(16*i+j).O1) or (flag /=out_flag(16*i+j).F1))) then
	            report "§{Error for %%INST1 instruction: " &
                "A=" & to_string(input(i)) & ", B=" & to_string(input(j)) &                                 
                "; expected R=" & to_string(out_add(16*i+j).O1) &  ", expected flag=" & std_logic'image(out_flag(16*i+j).F1) &
                ", received R=" & to_string(R) & ", received flag=" & std_logic'image(flag) & "}§"
              severity error;
              fail :='1';
              count := '1';
             end if;
            end if;
         end loop;
       end loop;
               
       ----- second instruction       
       slc <= "01"; 
       count := '0';      
             
       for i in input'range loop
	A <= input(i);         
            
        for j in input'range loop 
	  B <= input(j);
          wait for Clk_period*2;
          wait for Clk_period/10;
          if count = '0' then 
              if (R = "UUUU" or flag ='U') then
                 report "§{Probably, you have not correctly assigned output signal 'R' or 'flag' or other variables.}§" severity failure;
                                                
              elsif (((R /= out_add(16*i+j).O2) or (flag /=out_flag(16*i+j).F2))) then
                 report "§{Error for %%INST2 instruction: " &
                 "A=" & to_string(input(i)) & ", B=" & to_string(input(j)) &                                 
                 "; expected R=" & to_string(out_add(16*i+j).O2) &  ", expected flag=" & std_logic'image(out_flag(16*i+j).F2) &
                 ", received R=" & to_string(R) & ", received flag=" & std_logic'image(flag) & "}§"
              severity error;
              fail :='1';
              count := '1';
             end if;
            end if;
         end loop;
       end loop;
                
      ----- third instruction          
      slc <= "10"; 
      count := '0';      
             
       for i in input'range loop
	A <= input(i);         
            
        for j in input'range loop 
	  B <= input(j);
          wait for Clk_period*2;
          wait for Clk_period/10;
          if count = '0' then  
              if (R = "UUUU" or flag ='U') then
                  report "§{Probably, you have not correctly assigned output signal 'R' or 'flag' or other variables.}§" severity failure;
               
              elsif ((R /= out_add(16*i+j).O3) or (flag /=out_flag(16*i+j).F3))  then
                  report "§{Error for %%INST3 instruction: " &
                  "A=" & to_string(input(i)) & ", B=" & to_string(input(j)) &                                                           
                  "; expected R=" & to_string(out_add(16*i+j).O3) &  ", expected flag=" & std_logic'image(out_flag(16*i+j).F3) &
                  ", received R=" & to_string(R) & ", received flag=" & std_logic'image(flag) & "}§"
              severity error;
              fail :='1';
              count := '1';
             end if;
            end if;
         end loop;
       end loop;
       
       ----- fourth instruction
       slc <= "11";  
      count := '0';      
             
       for i in input'range loop
	  A <= input(i);         
          wait for Clk_period*2;
          wait for Clk_period/10;
          if count = '0' then 
              if (R = "UUUU" or flag ='U') then
                    report "§{Probably, you have not correctly assigned output signal 'R' or 'flag' or other variables.}§" severity failure;
     
              elsif ((R /= out_shift(i)) or (flag /=out_carry(i))) then
                    report "§{Error for %%INST4 instruction: " & "A=" & to_string(input(i)) &
                    "; expected R=" & to_string(out_shift(i)) &  ", expected flag=" & std_logic'image(out_carry(i)) &
                    ", received R=" & to_string(R) & ", received flag=" & std_logic'image(flag) & "}§"
              severity error;
              fail :='1';
              count := '1';
             end if;
          end if;
       end loop;

         
      if fail='1' then
          report  "" severity failure;
          wait;
      end if;



-------------------- clock cycle check ------------------------
   --When ALU is enabled and the input changes on the falling edge, 
   --the output should not change.
   
   enable <= '1'; 
   wait for Clk_period;
   for s in slcr'range loop
   slc <= slcr(s);
   A <= "0000";
   B <= "0000";
   wait for Clk_period;
   wait until rising_edge(Clk);
   out_1 :=R;
   A <= "0101"; 
   B <= "0111";
   wait until falling_edge(Clk); 
   wait for Clk_period/10;
   out_2 :=R;
   
   if (out_1/=out_2) then
          report "§{ALU is operating on falling edge of the clock signal, but it should not.}§" severity failure;
   end if;
   
   wait until rising_edge(Clk);
   wait for Clk_period/10;
   
   out_3 :=R;
   
   if (out_1=out_3) then
       wait until falling_edge(Clk); 
       wait for Clk_period/10;
       out_2 :=R;
       
       if (out_3/=out_2) then
          report "§{ALU is operating on falling edge of the clock signal, but it should not.}§" severity failure;
       end if;
       
       wait until rising_edge(Clk);
       wait for Clk_period/10;    
       out_3 :=R;
       
       if (out_3=out_2) then  
           report "§{ALU is not operating on rising edge of the clock signal.}§" severity failure;
       end if;
   end if;
   
   end loop;

      ----------------- enable check -----------------------
      --When ALU is disabled and the input changes on the falling edge, 
      --the output should not change on the next rising edge.
      slc <= "11";
      A <= "1001";
      B <= "0011";
      wait for Clk_period*2;   
      enable <= '0'; 
      fail :='0';
      for k in slcr'range loop
	slc <= slcr(k);  
        A <= "1001";
        B <= "0011";
        wait for Clk_period/0.9;
        if (R /= "0000") or (flag /='0') then
	  fail :='1';
        end if;             
      end loop; 
      if fail='1' then 
             
	if (R /= "0000" and flag ='0') then       
	  report "§{The output 'R' is not zero when the enable signal is zero.}§" severity failure;
               
        elsif (R = "0000" and flag /='0') then       
          report "§{The output 'flag' is not zero when the enable signal is zero.}§" severity failure;

         else    
          report "§{The outputs are not zero when the enable signal is zero.}§" severity failure;
                   
         end if;
       end if;
         

       report "Success" severity failure;
       wait;

      
   end process;

END behavior;