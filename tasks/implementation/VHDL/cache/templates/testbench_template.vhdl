library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;
use std.textio.all;
use IEEE.std_logic_textio.all;

entity cache_tb is
end cache_tb;

architecture behavior of cache_tb is

    -- Clock period definitions:
    constant CLK_period : time := 20 ns;

    -- function to converte std_logic_vectors to string
    function slv_image(in_image : std_logic_vector) return string is
        variable L : Line;  -- access type
        variable W : String(1 to in_image'length) := (others => ' ');
    begin
        WRITE(L, in_image);
        W(L.all'range) := L.all;
        Deallocate(L);
        return W;
    end slv_image;

    --UUT component
    component cache
        port(
            clk      : in  std_logic;
            en_read  : in  std_logic;
            addr     : in  std_logic_vector(({{addr_length}} - 1) downto 0);
            ch_cm    : out std_logic;
            data      : out std_logic_vector(({{data_length}} - 1) downto 0)
        );
    end component cache;

    -- signals to connect UUT
    signal clk         : std_logic;
    signal en_read     : std_logic;
    signal addr     : std_logic_vector(({{addr_length}} - 1) downto 0);
    signal ch_cm     : std_logic;
    signal data         : std_logic_vector(({{data_length}} - 1) downto 0);


    -- arrays with 3 correct addresses (with cache hit) and corresponding data
    type correct_addr_t is array (0 to 2) of std_logic_vector(({{addr_length}}-1) downto 0);
    type correct_data_t is array (0 to 2) of std_logic_vector(({{data_length}}-1) downto 0);
    constant correct_addr_set: correct_addr_t := ({{correct_addr_set}});
    constant correct_data_set: correct_data_t := ({{correct_data_set}});
    
    
    -- arrays with cache content (same as given to the user)
    type cache_tag_t is array (0 to {{cache_size}}-1) of std_logic_vector(({{tag_length}}-1) downto 0);
    type cache_data_t is array (0 to {{cache_size}}-1) of std_logic_vector(({{data_length}}-1) downto 0);

    constant cache_tag : cache_tag_t := ( 
                                          {% for i in range(cache_size|int -1) %}
                                          "{{tag_values[i]}}", 
                                          {% endfor %}
                                          "{{tag_values[cache_size|int -1]}}" );
                
    constant cache_data : cache_data_t := ( 
                                            {% for i in range(cache_size|int -1) %}
                                            "{{data_values[i]}}", 
                                            {% endfor %}
                                            "{{data_values[cache_size|int -1]}}" );

begin
    
    --map UUT
    UUT: cache
        port map(
                    clk => clk,
                    en_read => en_read,
                    addr => addr,
                    ch_cm => ch_cm,
                    data => data
        );

    -- clock generator
    clk_generator : process
    begin
        clk <= '0';
        wait for CLK_period/2;
        clk <= '1';
        wait for CLK_period/2;
    end process;


    -- Test process
    test_process: process is

        -- variables for old UUT outputs (to check correct clock edge)
        variable old_data: std_logic_vector( ({{data_length}}-1) downto 0);
        variable old_ch_cm: std_logic;
        
        -- variables for expected UUT outputs
        variable correct_data: std_logic_vector( ({{data_length}}-1) downto 0);
        variable correct_ch_cm: std_logic;
            
    begin

        -- TEST 1)
        -- apply a correct address with cache hit and enable cache
        -- wait two clock edges and check if outputs are correct
        -- depending on user's task parameter, right_edge is the falling or rising edge 
        -- (e.g. if cache should only work on rising_edge: right_edge=rising_edge, wrong_edge = falling_Edge)

        en_read <= '1';
        addr <= correct_addr_set(1);

        wait until {{right_edge}}(clk);
        wait until {{right_edge}}(clk);
        wait for 1 ns;

        if(data /= correct_data_set(1) or ch_cm /= '1') then
            report "§{For en_read = '1' and addr = """ & slv_image(addr) & """ the outputs should be data = """&slv_image(correct_data_set(1)) & """ and ch_cm = '1' at the next {{right_edge}} but your cache returns data = """& slv_image(data) & """ and ch_cm = " & std_logic'image(ch_cm) &".}§" severity failure;
        end if;

        --Test 2a)
        -- now set enable to '0'
        -- check if output does not chance before right edge of cache    

        wait until {{right_edge}}(clk);
        wait for 1 ns;        

        en_read <= '0';
        
        wait until {{wrong_edge}}(clk);
        wait for 1 ns;
            
        if(data /= correct_data_set(1) or ch_cm /= '1') then
            report "§{Input en_read was set to '0', so the outputs should change to data = """ & slv_image((data'range => 'Z')) & """ and ch_cm = '0' at the next {{right_edge}}, but your outputs changed before the next {{right_edge}}.}§" severity failure;
        end if; 

        -- Test 2b)
        -- now apply different correct addresses with cache hits and check if output stays disabled

        for i in correct_addr_set'range loop

            addr <= correct_addr_set(i);
            wait until {{right_edge}}(clk);
            wait for 1 ns;

            if(data /= (data'range => 'Z') or ch_cm /= '0') then
                report "§{Input en_read was set to '0', so the outputs should change to data = """ & slv_image((data'range => 'Z')) & """ and ch_cm = '0' at the next {{right_edge}}, but your outputs at the next {{right_edge}} are data = """ & slv_image(data) & """ and ch_cm = "& std_logic'image(ch_cm) &".}§" severity failure;
            end if;              
           
        end loop;

        -- Test 3a)
        -- enable chache and apply address with cache hit
        -- check if outputs do not change before next right edge

        wait until {{right_edge}}(clk);
        wait for 1 ns;

        en_read <= '1';
        addr <= correct_addr_set(0);

        wait until {{wrong_edge}}(clk);
        wait for 1 ns;
        
        if(data /= (data'range => 'Z') or ch_cm /= '0') then
            report "§{Output of your cache changed before next {{right_edge}} (With inputs: en_read ='1' and addr = """ & slv_image(addr) & """).}§" severity failure;
         end if;  

        -- Test 3b)
        -- now wait until right edge and check if correct outputs are set

        wait until {{right_edge}}(clk);
        wait for 1 ns;

        if(data /= correct_data_set(0) or ch_cm /= '1') then
            report "§{For en_read = '1' and addr= """  & slv_image(addr) & """ the outputs should be data = """ & slv_image(correct_data_set(0)) & """ and ch_cm = '1' at the next {{right_edge}}, but your cache returns data = """ & slv_image(data) & """ and ch_cm = " & std_logic'image(ch_cm) &" at the next {{right_edge}}.}§" severity failure;
        end if;  

        -- Test 4)
        -- now apply all possible address inputs (2**addr_length addresses)
        -- check for each address if outputs do not change before next right edge (compare with old outputs)
        -- then check if outputs are correct at next right edge
        -- output should be either a cache miss or cache hit with correct output, depending on cache content

        old_data := data;
        old_ch_cm := ch_cm;

        for i in 0 to (2**{{addr_length}})-1 loop 
            
            wait until {{right_edge}}(clk);
            wait for 1 ns;

            en_read <= '1';
            addr <= std_logic_vector(to_unsigned(i,{{addr_length}}));

            wait until {{wrong_edge}}(clk);
            wait for 1 ns;

            if(data /= (old_data) or ch_cm /= old_ch_cm) then
                report "§{The outputs of your cache changed before the next {{right_edge}} (With inputs: en_read ='1' and addr = """ & slv_image(addr) & """).}§" severity failure; 
            end if;  

            wait until {{right_edge}}(clk);
            wait for 1 ns;

            -- check if address is a cache hit by comparing its tag with the cache content
            -- only do this, if cache index is not out of range 
            if(to_integer(unsigned(addr(({{block_length}}-1) downto 0))) < {{cache_size}}) then            

                if( addr(({{addr_length}}-1) downto {{block_length}}) = cache_tag(to_integer(unsigned(addr(({{block_length}}-1) downto 0)))) ) then
                    correct_data:= cache_data(to_integer(unsigned(addr(({{block_length}}-1) downto 0))));
                    correct_ch_cm:= '1';
                else
                    correct_data:= (data'range => 'Z');
                    correct_ch_cm:= '0';
                end if;
            else
                correct_data:= (data'range => 'Z');
                correct_ch_cm:= '0';
            end if;
                
            if(data /= correct_data or ch_cm /= correct_ch_cm) then
                report "§{For en_read = '1' and addr = """ & slv_image(addr) & """ the outputs should be data = """& slv_image(correct_data) & """ and ch_cm = " & std_logic'image(correct_ch_cm) & " at the next {{right_edge}} but your cache returns data = """& slv_image(data) & """ and ch_cm = " & std_logic'image(ch_cm) &" at the next {{right_edge}}.}§" severity failure;
            end if; 
             
            old_data := data;
            old_ch_cm := ch_cm;
 
        end loop;
           
        -- if all tests are passed -> solution is correct
        report "Success" severity failure;
        
    end process;
             
end architecture behavior;
