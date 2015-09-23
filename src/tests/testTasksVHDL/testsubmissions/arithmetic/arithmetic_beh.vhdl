library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

architecture behavior of arithmetic is
 
   constant N : integer := 15; 

   type solution is record
        --The inputs 
        O: std_logic_vector(N-1 downto 0);
        C: std_logic;
        V: std_logic;
        VALID: std_logic;
    end record;

    impure function do_operation(dummy:std_logic) return solution is
        variable sol: solution;
        subtype EXT_TYPE is signed(N-1 downto 0);
        variable I1_EXT :EXT_TYPE := RESIZE(signed(I1),N); 
        variable I2_EXT :EXT_TYPE := RESIZE(signed(I2),N);
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

        --ADD
        CF := CARIES(1); --COUT        

        VF := CARIES(1) xor CARIES(0);--last two caries not same -> overflow
       
        sol.O := std_logic_vector(O_EXT);
        sol.C := CF;
        sol.V := VF;

        --comp2
        sol.VALID := not VF;

        return sol;
    
    end do_operation;

    
begin
    process (I1,I2) 
        variable solCalc : solution;        
    begin
        solCalc:= do_operation('1');
        O<=solCalc.O;
        V<=solCalc.V;
        C<=solCalc.C;
        VALID<=solCalc.VALID;
    end process;
end behavior;
