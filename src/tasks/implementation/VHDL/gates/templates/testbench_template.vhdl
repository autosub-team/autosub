library IEEE;
use IEEE.std_logic_1164.all;


entity gates_tb is
end gates_tb;

architecture behavior of gates_tb is
    component gates
         port(  A,B,C,D : in    std_logic;
                O       : out   std_logic);
    end component;

    signal A_UUT,B_UUT,C_UUT,D_UUT,O_UUT : std_logic;
    
    type pattern_type is record
            --The inputs 
            D,C,B,A : std_logic; 
    end record;

    function calcFromFormula(inputs:pattern_type) return std_logic is
        variable A :std_logic;
        variable B :std_logic;
        variable C :std_logic;
        variable D :std_logic;
        variable O :std_logic;
    begin
       A := inputs.A;
       B := inputs.B;
       C := inputs.C;
       D := inputs.D;
       O := %%FORMULA;
       return O;
    end calcFromFormula;

begin

    UUT: gates 
        port map
        (
            A=>A_UUT,
            B=>B_UUT,
            C=>C_UUT,
            D=>D_UUT,
            O=>O_UUT
        );

    process           
        --The patterns to apply.
        type pattern_array is array (natural range <>) of pattern_type;
       
        constant patterns : pattern_array:=(
            %%TESTPATTERN);   
        variable O_calculated : std_logic;

    begin
        --Check each pattern.
        for i in patterns'range loop
            --Set the inputs.
            A_UUT <= patterns(i).A;
            B_UUT <= patterns(i).B;
            C_UUT <= patterns(i).C;
            D_UUT <= patterns(i).D;
            --Wait for the results.
            wait for 10 ns;
            --Calculate proper output
            O_calculated := calcFromFormula(patterns(i));
            -- Compare UUT output with proper output
            if O_UUT /= O_calculated then
                report  "Error for" & 
                        " D=" & std_logic'image(patterns(i).D) &
                        " C=" & std_logic'image(patterns(i).C) & 
                        " B=" & std_logic'image(patterns(i).B) &
                        " A=" & std_logic'image(patterns(i).A) & 
                        "; expected O=" & std_logic'image(O_calculated) &
                        ", received O=" & std_logic'image(O_UUT) 
                severity failure;
                exit;
            end if;
        end loop;
        report "Success";
        wait;
    end process; 

end behavior;
