LIBRARY IEEE;
USE IEEE.std_logic_1164.ALL;
USE IEEE.numeric_std.ALL;

entity RAM_tb is
end RAM_tb;

architecture Behavioral of RAM_tb is
    component RAM port(Clk : in std_logic;
                       addr1 : in std_logic_vector(%%ADDRLENGTH  downto 0); --address
                       addr2 : in std_logic_vector(%%ADDRLENGTH  downto 0); --address
                       en_read : in std_logic; -- read-enable
                       en_write1 : in std_logic; -- write-enable
                       en_write2 : in std_logic; -- write-enable    
                       input1 : in std_logic_vector(%%WRITELENGTH downto 0);  --input
                       input2 : in std_logic_vector(%%WRITELENGTH downto 0);  --input 
                       output : out std_logic_vector(%%READLENGTH downto 0));  --output
    end component;

    signal Clk : std_logic := '0'; --clock signal
    signal addr1 : std_logic_vector(%%ADDRLENGTH  downto 0) := (others => '0'); --address
    signal addr2 : std_logic_vector(%%ADDRLENGTH  downto 0) := (others => '0'); --address
    signal en_read : std_logic := '0'; -- read-enable    
    signal en_write1 : std_logic := '0'; -- write-enable
    signal en_write2 : std_logic := '0'; -- write-enable    
    signal input1 : std_logic_vector(%%WRITELENGTH downto 0) := (others => '0');  --input
    signal input2 : std_logic_vector(%%WRITELENGTH downto 0) := (others => '0');  --input 
    signal output : std_logic_vector(%%READLENGTH downto 0) := (others => '0');  --output
    
     
    constant Clk_period : time := 10 ns;

begin
  -- Instantiate the Unit Under Test (UUT)
 UUT: RAM port map (
        Clk => Clk, 
        addr1 => addr1, 
        addr2 => addr2,
        en_read => en_read,
        en_write1 => en_write1,
        en_write2 => en_write2,
        input1 => input1,
        input2 => input2,
        output => output
        );

   -- Clock process definitions
   Clk_process :process
   begin
        Clk <= '0';
        wait for Clk_period/2;
        Clk <= '1';
        wait for Clk_period/2;
   end process;
  
 stim_proc: process  
           
        type random_array is array (0 to 5) of std_logic_vector(%%ADDRLENGTH downto 0);
        constant random_addr : random_array :=(
                                    %%RANDOM_ADDR);
  
        type content_array_in is array (0 to 5) of std_logic_vector(%%WRITELENGTH downto 0);
        constant content_in : content_array_in :=(
        					       %%CONTENT_IN1);
   										
        constant content_test_in : content_array_in :=(
                                                %%CONTENT_IN2);        					

                       
   begin

     -- check en_write1 only
     en_write2 <= '0';
     for i in random_addr'range loop
        en_write1 <= '1';
        en_read <= '0';
        addr1 <= random_addr(i);   
        input1 <= content_in(i); 
        wait for Clk_period;    
     end loop;
     
     -- check en_write2 only
     en_write1 <= '0';
     for i in random_addr'range loop
        en_write2 <= '1';
        en_read <= '0';
        addr2 <= random_addr(i);   
        input2 <= content_test_in(i); 
        wait for Clk_period; 
        -- check if the data has been written in the memory
        en_write2 <= '0';
        en_read <= '1';
        addr1 <= random_addr(i);   
        wait for Clk_period;          
     end loop; 
     
     for i in random_addr'range loop
         en_read <= '0';
         en_write2 <= '1';
         en_write1 <= '1';
         addr1 <= random_addr(i);  
         addr2 <= random_addr(5-i);  
         input1 <= content_in(i);
         input2 <= content_in(5-i); 
         wait for Clk_period;
         -- check that the data which is read is the previous one
         en_read <= '1';
         en_write2 <= '0';
         en_write1 <= '0';
         addr1 <= random_addr(i); 
         wait for Clk_period;
         
         addr1 <= random_addr(5-i); 
         wait for Clk_period;
     end loop;     
     
      wait;
   end process;

END;