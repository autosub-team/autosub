library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;
use std.textio.ALL;
use IEEE.std_logic_textio.all;

entity arithmetic_tb is
end arithmetic_tb;

library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;
use std.textio.ALL;
use IEEE.std_logic_textio.all;

architecture behavior of arithmetic_tb is
    subtype I1_TYPE is std_logic_vector(%%I1-1 downto 0);
    subtype I2_TYPE is std_logic_vector(%%I2-1 downto 0);
    subtype O_TYPE  is std_logic_vector(%%O-1 downto 0); 
    constant operation :string(1 to 3) := "%%OPERATION"; -- ADD or SUB
    constant N : integer :=%%O; --Nubmer of bits for operarion 

    component arithmetic
        port(  I1     :in    I1_TYPE;    -- Operand 1
               I2     :in    I2_TYPE;    -- Operand 2
               O      :out   O_TYPE;     -- Output
               C      :out   std_logic;  -- Carry Flag
               V      :out   std_logic;  -- Overflow Flag
               VALID  :out   std_logic); -- Flag to indicate if the solution is valid or not);
    end component;

    signal I1_UUT  :I1_TYPE;
    signal I2_UUT  :I2_TYPE;
    signal O_UUT   :O_TYPE;
    signal C_UUT   :std_logic;
    signal V_UUT   :std_logic;
    signal VALID_UUT   :std_logic;


    type pattern_type is record
        --The inputs 
        I1  :I1_TYPE;
        I2  :I2_TYPE;
    end record;

    type solution is record
        --Tsolution container
        O: O_TYPE;
        C: std_logic;
        V: std_logic;
        VALID: std_logic;
    end record;

    
    function Image(In_Image : Std_Logic_Vector) return String is
        variable L : Line;  -- access type
        variable W : String(1 to In_Image'length) := (others => ' ');  
    begin
         WRITE(L, In_Image);
         W(L.all'range) := L.all;
         Deallocate(L);
         return W;
    end Image;


    impure function do_operation_comp2(dummy:std_logic) return solution is
        variable sol: solution;
        subtype EXT_TYPE is signed(N-1 downto 0);
        variable I1_EXT :EXT_TYPE:= RESIZE(signed(I1_UUT),N); 
        variable I2_EXT :EXT_TYPE := RESIZE(signed(I2_UUT),N);
        variable O_EXT  :EXT_TYPE;
        variable SIGNS : std_logic_vector(2 downto 0);
        variable CARIES : std_logic_vector(1 downto 0); -- CIN, COUT
        variable I1_SIGN : std_logic ;
        variable I2_SIGN : std_logic ;
        variable O_SIGN : std_logic ;
        variable CF :std_logic;
        variable VF :std_logic;
        variable one :EXT_TYPE := (0=>'1',others=>'0');
    begin
        if(operation="SUB") then
            I2_EXT := not(I2_EXT)+ one;
        end if;

        
        O_EXT := I1_EXT+I2_EXT; 

        I1_SIGN := I1_EXT(N-1);
        I2_SIGN := I2_EXT(N-1);
        O_SIGN := O_EXT(N-1);


        SIGNS := (O_SIGN, I1_SIGN, I2_SIGN);
        case SIGNS is
            when "001" =>  CARIES := "11";
            when "010" =>  CARIES := "11";
            when "011" =>  CARIES := "10";
            when "100" =>  CARIES := "01";
            when "111" =>  CARIES := "11";
            when others => CARIES := "00";
        end case;

        if (operation="ADD") then
           CF := CARIES(1); --COUT
        elsif (operation="SUB") then
            if( (unsigned(std_logic_vector(I2_EXT))) < (unsigned(std_logic_vector(I1_EXT))) ) then
                CF := '1';
            else
                CF := '0';
            end if;
        end if;

        VF := CARIES(1) xor CARIES(0);--last two caries not same -> overflow
       

        sol.O := std_logic_vector(O_EXT);
        sol.C := CF;
        sol.V := VF;
        sol.VALID := not VF; 

        return sol;
    
    end do_operation_comp2;

    impure function do_operation_comp1(dummy:std_logic) return solution is
        variable sol: solution;
        subtype EXT_TYPE is signed(N-1 downto 0);
        variable I1_EXT :EXT_TYPE:= RESIZE(signed(I1_UUT),N); 
        variable I2_EXT :EXT_TYPE := RESIZE(signed(I2_UUT),N);
        variable O_EXT  :EXT_TYPE;
        variable SIGNS : std_logic_vector(2 downto 0);
        variable CARIES : std_logic_vector(1 downto 0); -- CIN, COUT
        variable I1_SIGN : std_logic ;
        variable I2_SIGN : std_logic ;
        variable O_SIGN : std_logic ;
        variable CF :std_logic;
        variable VF :std_logic;
        variable one :EXT_TYPE := (0=>'1',others=>'0');
    begin
        if(operation="SUB") then
            I2_EXT := not(I2_EXT);
        end if;

        
        O_EXT := I1_EXT+I2_EXT; 

        I1_SIGN := I1_EXT(N-1);
        I2_SIGN := I2_EXT(N-1);
        O_SIGN := O_EXT(N-1);


        SIGNS := (O_SIGN, I1_SIGN, I2_SIGN);
        case SIGNS is
            when "001" =>  CARIES := "11";
            when "010" =>  CARIES := "11";
            when "011" =>  CARIES := "10";
            when "100" =>  CARIES := "01";
            when "111" =>  CARIES := "11";
            when others => CARIES := "00";
        end case;

        if (CARIES(1) ='1') then
           O_EXT := O_EXT + one; --end around carry
        end if;


        if (operation="ADD") then
            CF := CARIES(1); --COUT
        elsif (operation="SUB") then
             if( (unsigned(std_logic_vector(I2_EXT))) < (unsigned(std_logic_vector(I1_EXT))) ) then
                CF := '1';
            else
                CF := '0';
            end if;
        end if;

        --to decide overflow we have to consider the possibly new output sign
        O_SIGN := O_EXT(N-1);

        SIGNS := (O_SIGN, I1_SIGN, I2_SIGN);
        case SIGNS is
            when "011" =>  VF := '1';
            when "100" =>  VF := '1';
            when others => VF := '0';
        end case;

        sol.O := std_logic_vector(O_EXT);
        sol.C := CF;
        sol.V := VF;
        sol.VALID := not VF; 

        return sol;
     end do_operation_comp1;    

    impure function do_operation_unsigned(dummy:std_logic) return solution is
        variable sol: solution;
        subtype EXT_TYPE is unsigned(N-1 downto 0);
        variable I1_EXT :EXT_TYPE := RESIZE(unsigned(I1_UUT),N); 
        variable I2_EXT :EXT_TYPE := RESIZE(unsigned(I2_UUT),N);
        variable O_EXT  :EXT_TYPE;
        variable SIGNS : std_logic_vector(2 downto 0);
        variable CARIES : std_logic_vector(1 downto 0); -- CIN, COUT
        variable I1_SIGN : std_logic ;
        variable I2_SIGN : std_logic ;
        variable O_SIGN : std_logic ;
        variable CF :std_logic;
        variable VF :std_logic;
        variable one :EXT_TYPE := (0=>'1',others=>'0');
    begin
        if(operation="SUB") then
            I2_EXT := not(I2_EXT)+ one;
        end if;


        O_EXT := I1_EXT+I2_EXT; 

        I1_SIGN := I1_EXT(N-1);
        I2_SIGN := I2_EXT(N-1);
        O_SIGN := O_EXT(N-1);

        SIGNS := (O_SIGN, I1_SIGN, I2_SIGN);
        case SIGNS is
            when "001" =>  CARIES := "11";
            when "010" =>  CARIES := "11";
            when "011" =>  CARIES := "10";
            when "100" =>  CARIES := "01";
            when "111" =>  CARIES := "11";
            when others => CARIES := "00";
        end case;

        if (operation="ADD") then
           CF := CARIES(1); --COUT
        elsif (operation="SUB") then
            if( (unsigned(std_logic_vector(I2_EXT))) < (unsigned(std_logic_vector(I1_EXT))) ) then
                CF := '1';
            else
                CF := '0';
            end if;
        end if;

        VF := CARIES(1) xor CARIES(0);--last two caries not same -> overflow

        sol.O := std_logic_vector(O_EXT);
        sol.C := CF;
        sol.V := VF;
        sol.VALID := not CF;

        return sol;

    end do_operation_unsigned;



begin
    UUT:arithmetic 
        port map
        (
            I1=>I1_UUT,
            I2=>I2_UUT,
            O=>O_UUT,
            C=>C_UUT,
            V=>V_UUT,
            VALID=>VALID_UUT
        ); 
    process
        type pattern_array is array (natural range <>) of pattern_type;

        constant patterns : pattern_array:=(%%TESTPATTERN);
        variable sol_cal:solution;
    begin
        for i in patterns'range loop
            -- Set the inputs   
            I1_UUT <= patterns(i).I1;
            I2_UUT <= patterns(i).I2;
            --Wait for the results.
            wait for 10 ns;
            -- Calculate proper outputs
            sol_cal :=do_operation_%%OPSTYLE('1');
            -- Compare UUT output with proper output
            if((O_UUT/= sol_cal.O) or (C_UUT /= sol_cal.C) or (V_UUT /= sol_cal.V) or (VALID_UUT /= sol_cal.VALID)) then
                write(OUTPUT,string'("Error for:"));
                write(OUTPUT,string'("\n"));
                write(OUTPUT,string'("   %%OPSTYLE,%%OPERATION")); --for debug!!
                write(OUTPUT,string'("\n")); 
                write(OUTPUT,string'("   I1= ")&Image(patterns(i).I1));
                write(OUTPUT,string'("\n"));
                write(OUTPUT,string'("   I2= ")&Image(patterns(i).I2)); 
                write(OUTPUT,string'("\n"));
                

                write(OUTPUT,string'("Expected:"));
                write(OUTPUT,string'("\n"));
                write(OUTPUT,string'("   O=  ")&Image(sol_cal.O));
                write(OUTPUT,string'("\n"));
                write(OUTPUT,string'("   C= ")&std_logic'image(sol_cal.C));
                write(OUTPUT,string'("\n"));
                write(OUTPUT,string'("   V= ")&std_logic'image(sol_cal.V));
                write(OUTPUT,string'("\n"));
                write(OUTPUT,string'("   VALID= ")&std_logic'image(sol_cal.VALID));
                write(OUTPUT,string'("\n"));

                write(OUTPUT,string'("Received: "));
                write(OUTPUT,string'("\n"));
                write(OUTPUT,string'("   O=  ")&Image(O_UUT));
                write(OUTPUT,string'("\n"));
                write(OUTPUT,string'("   C= ") & std_logic'image(C_UUT));
                write(OUTPUT,string'("\n"));
                write(OUTPUT,string'("   V= ")&std_logic'image(V_UUT));
                write(OUTPUT,string'("\n"));
                write(OUTPUT,string'("   VALID= ")&std_logic'image(VALID_UUT));
                write(OUTPUT,string'("\n"));
                write(OUTPUT,string'("\n"));
                write(OUTPUT,string'("\n"));

                report "Simulation error" severity failure;
            end if;
        end loop;
        report "Success" severity failure;
    end process;
end behavior;
