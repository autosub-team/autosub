library IEEE;
use IEEE.std_logic_1164.all;
use std.textio.all;
use IEEE.std_logic_textio.all;

entity crc_tb is
end crc_tb;

architecture behavior of crc_tb is
    component crc is
        port
        (
            NEW_MSG   : in std_logic;
            MSG       : in std_logic_vector(%%MSGLEN-1 downto 0);
            CLK       : in std_logic;
            CRC_VALID : out std_logic;
            CRC       : out std_logic_vector(%%CRCWIDTH-1 downto 0)
        );
    end component;    

    type pattern_type is record
        MSG : std_logic_vector(%%MSGLEN-1 downto 0);
        CRC : std_logic_vector(%%CRCWIDTH-1 downto 0);
    end record;

    type pattern_array is array (natural range <>) of pattern_type;

    constant patterns : pattern_array:=(
            %%TESTPATTERN
            );

    function image(in_image : std_logic_vector) return string is
        variable L : Line;  -- access type
        variable W : String(1 to in_image'length) := (others => ' ');  
    begin
        WRITE(L, in_image);
        W(L.all'range) := L.all;
        Deallocate(L);
        return W;
    end image;
    
    signal NEW_MSG_UUT      : std_logic;
    signal MSG_UUT          : std_logic_vector(%%MSGLEN-1 downto 0);
    signal CLK_UUT          : std_logic;
    signal CRC_VALID_UUT    : std_logic;
    signal CRC_UUT          : std_logic_vector(%%CRCWIDTH-1 downto 0);
    
    signal cnt_reset : std_logic;
    signal clk_cnt: integer;

    constant clk_period : time := 20 ns;
begin

    UUT: crc
        port map
        (
            NEW_MSG    => NEW_MSG_UUT,
            MSG        => MSG_UUT,
            CLK        => CLK_UUT,
            CRC_VALID  => CRC_VALID_UUT,
            CRC        => CRC_UUT
        );
 
    clk_generator : process
    begin
        CLK_UUT <= '0';
        wait for clk_period/2;
        CLK_UUT <= '1';
        wait for clk_period/2;
    end process;
    
    clk_counter: process(CLK_UUT,cnt_reset)    
    begin
        if(rising_edge(CLK_UUT)) then
            if(cnt_reset='1') then
                clk_cnt <= 0;
            else 
                clk_cnt <= clk_cnt + 1; 
            end if;
        end if;
    end process clk_counter;

    test :process
    begin
        for i in patterns'range loop
            NEW_MSG_UUT<='0';
            wait until rising_edge(CLK_UUT);
            MSG_UUT<=patterns(i).MSG;
            NEW_MSG_UUT<='1';
            wait until rising_edge(CLK_UUT);
            NEW_MSG_UUT <= '0';
            cnt_reset <= '1';
            wait until rising_edge(CLK_UUT);
            cnt_reset <= '0';
 
            -- wait msgwidth 
            wait until (clk_cnt = %%MSGLEN+2);

            -- check the CRC_VALID
            if(CRC_VALID_UUT /= '1') then
                write(OUTPUT,string'("Error:\n"));
                write(OUTPUT,string'("   CRC_VALID is not '1'. Your design does not fullfill the calculation duration constraint or you do not set the CRC_VALID to '1'!\n"));
                write(OUTPUT,string'("\n\n"));
                report "Simulation error" severity failure;

            elsif(patterns(i).CRC /= CRC_UUT) then
                write(OUTPUT,string'("Error:\n"));
                write(OUTPUT,string'("   For MSG = ") & image(patterns(i).MSG)&string'("\n"));
                write(OUTPUT,string'("   Expected CRC = ") & image(patterns(i).CRC) & string'("\n"));
                write(OUTPUT,string'("   Received CRC = ") & image(CRC_UUT) & string'("\n"));
                write(OUTPUT,string'("\n\n"));

                report "Simulation error" severity failure;
            end if;

        end loop;

        report "Success" severity failure;
    end process test;  
end behavior;
