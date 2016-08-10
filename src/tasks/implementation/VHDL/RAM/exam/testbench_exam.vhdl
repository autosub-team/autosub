LIBRARY IEEE;
USE IEEE.std_logic_1164.ALL;
USE IEEE.numeric_std.ALL;

entity RAM_tb is
end RAM_tb;

architecture Behavioral of RAM_tb is
    component RAM port(Clk : in std_logic;
                       addr1 : in std_logic_vector(7  downto 0); --address
                       addr2 : in std_logic_vector(7  downto 0); --address
                       en_read1 : in std_logic; -- read-enable
                       en_read2 : in std_logic; -- read-enable
                       en_write : in std_logic; -- write-enable    
                       input : in std_logic_vector(23 downto 0);  --input
                       output1 : out  std_logic_vector(23 downto 0);  --output 
                       output2 : out std_logic_vector(23 downto 0));  --output
    end component;

    signal Clk : std_logic := '0'; --clock signal
    signal addr1 : std_logic_vector(7  downto 0) := (others => '0'); --address
    signal addr2 : std_logic_vector(7  downto 0) := (others => '0'); --address
    signal en_read1 : std_logic := '0'; -- read-enable    
    signal en_read2 : std_logic := '0'; -- read-enable
    signal en_write : std_logic := '0'; -- write-enable    
    signal input : std_logic_vector(23 downto 0) := (others => '0');  --input
    signal output1 : std_logic_vector(23 downto 0) := (others => '0');  --output 
    signal output2 : std_logic_vector(23 downto 0) := (others => '0');  --output   
    constant Clk_period : time := 10 ns;

begin
  -- Instantiate the Unit Under Test (UUT)
 UUT: RAM port map (
        Clk => Clk, 
        addr1 => addr1, 
        addr2 => addr2,
        en_read1 => en_read1,
        en_read2 => en_read2,
        en_write => en_write,
        input => input,
        output1 => output1,
        output2 => output2
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
        
        type random_array is array (0 to 5) of std_logic_vector(7 downto 0);
        constant random_addr : random_array :=(
                                    "11010110",
                         "00100000",
                         "11111100",
                         "00000000",
                         "11101000",
                         "10111010",
                         "11100010",
                         "00111010",
                         "01001110",
                         "01010110",
                         "01100100",
                         "10000110",
                         "00001110",
                         "00110000",
                         "10010110",
                         "11000100");
  
        type content_array_in is array (0 to 5) of std_logic_vector(23 downto 0);
        constant content_in : content_array_in :=(
        					"001111100000100111010100",
                         "000011100110100111001010",
                         "110111011100001010000010",
                         "011101011111001010101101",
                         "111011011100011011110000",
                         "000101111111111011010001",
                         "011100011110011001100000",
                         "110100010111111111101110",
                         "011010001110101010100010",
                         "000101111100010111111001",
                         "111100100011010000111101",
                         "110010100011000101000011",
                         "100001011111100011101000",
                         "100101000011101101110100",
                         "011011101000100011110101",
                         "101111100110001110010101");
        					
        constant content_test_in : content_array_in :=(
                                                "100000001000011001010011",
                         "101011101011001100101111",
                         "010000011011000001111000",
                         "111011000100110011000010",
                         "111101011011010110101001",
                         "101011100111010100101011",
                         "100110101110010101101011",
                         "010100001000000010011111",
                         "100101111101001000110000",
                         "100000101001110111010011",
                         "110101010010100101001101",
                         "111010110111110101011101",
                         "110000101010100011100001",
                         "010000010011110111011000",
                         "000000110111010000111100",
                         "110100111111001010100011");        					
                       
   begin

     -- check both read lines as well as write
     for i in random_addr'range loop
        en_write <= '1';
        en_read1 <= '0';
        en_read2 <= '0';
        addr1 <= random_addr(i);   
        input <= content_in(i); 
        wait for Clk_period; 
        -- check if en_write and en_read1 are working properly
        en_write <= '0';
        en_read1 <= '1';
        en_read2 <= '0';
        addr1 <= random_addr(i);   
        wait for Clk_period;      
        -- check if en_write and en_read2 are working properly
        en_read1 <= '0';
        en_read2 <= '1';
        addr2 <= random_addr(i);   
        wait for Clk_period;                 
     end loop;   
     
      -- check if both read lines work together properly   
     for i in random_addr'range loop
         en_read1 <= '0';
         en_read2 <= '0';
         en_write <= '1';
         addr1 <= random_addr(i);    
         input <= content_test_in(i);
         wait for Clk_period;
         -- check that the data which is read is the previous one
         en_read1 <= '1';
         en_read2 <= '1';
         en_write <= '0';
         addr1 <= random_addr(i); 
         addr2 <= random_addr(i);
         wait for Clk_period;     
     end loop;    
     
      wait;
   end process;

END;