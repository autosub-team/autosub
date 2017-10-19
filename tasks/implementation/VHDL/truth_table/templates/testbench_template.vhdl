library IEEE;
use IEEE.std_logic_1164.all;


entity truth_table_tb is
end truth_table_tb;

architecture behavior of truth_table_tb is
    component truth_table
         port(  A,B,C,D : in    std_logic;
                O       : out   std_logic);
    end component;

    signal A,B,C,D,O : std_logic;

begin

    UUT: truth_table port map(A=>A,B=>B,C=>C,D=>D,O=>O);

    process
        type pattern_type is record
            --The inputs
            D,C,B,A : std_logic;
            --The expected outputs
            O : std_logic;
        end record;

        --The patterns to apply.
        type pattern_array is array (natural range <>) of pattern_type;

        constant patterns : pattern_array:=(
            {{TESTPATTERN}});

    begin
        --Check each pattern.
        for i in patterns'range loop
            --Set the inputs.
            A <= patterns(i).A;
            B <= patterns(i).B;
            C <= patterns(i).C;
            D <= patterns(i).D;
            --Wait for the results.
            wait for 1 ns;
            --Check the outputs.
            if O /= patterns(i).O then
                report  "§{Error for" &
                        " D=" & std_logic'image(patterns(i).D) &
                        " C=" & std_logic'image(patterns(i).C) &
                        " B=" & std_logic'image(patterns(i).B) &
                        " A=" & std_logic'image(patterns(i).A) &
                        "; expected O=" & std_logic'image(patterns(i).O) &
                        ", received O=" & std_logic'image(O) & "}§" severity failure;
            end if;
        end loop;
        report "Success" severity failure;
        wait;
    end process;
end behavior;
