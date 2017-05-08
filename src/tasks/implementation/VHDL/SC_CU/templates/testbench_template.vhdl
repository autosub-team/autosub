library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity SC_CU_tb is
end SC_CU_tb;

architecture Behavioral of SC_CU_tb is

      component SC_CU_beh
            port( Opcode     : in  std_logic_vector(5 downto 0);
                  Funct      : in  std_logic_vector(5 downto 0);
                  Zero       : in  std_logic;
                
                  RegDst     : out std_logic;
                  Branch     : out std_logic;
                  Jump       : out std_logic;
                  MemRead    : out std_logic;
                  MemtoReg   : out std_logic;
                  MemWrite   : out std_logic;
                  ALUControl : out std_logic_vector(2 downto 0);
                  ALUSrc     : out std_logic;
                  RegWrite   : out std_logic);
      end component;
       
      constant clk_period : time := 20 ns;
      signal CLK : std_logic;

      constant array_size : integer := %%ARRAY_SIZE;

      signal Opcode  : std_logic_vector(5 downto 0);
      signal Funct   : std_logic_vector(5 downto 0);
      signal Zero    : std_logic;
      
      signal Controls: std_logic_vector(10 downto 0);
                  
      signal RegDst     : std_logic;
      signal Branch     : std_logic;
      signal Jump       : std_logic;
      signal MemRead    : std_logic;
      signal MemtoReg   : std_logic;
      signal MemWrite   : std_logic;
      signal ALUControl : std_logic_vector(2 downto 0);
      signal ALUSrc     : std_logic;
      signal RegWrite   : std_logic;
       
      type type_Inputs_test_array is array(0 to (array_size - 1)) of std_logic_vector(12 downto 0);
      signal Inputs_test_array : type_Inputs_test_array := (
		%%TESTPATTERN_INPUTS
             );
      
      type type_Controls_test_array is array(0 to (array_size - 1)) of std_logic_vector(10 downto 0);
      signal Controls_test_array : type_Controls_test_array := (
		%%TESTPATTERN_CONTROLS
            );
            
      type type_string_array is array(0 to (array_size - 1)) of string(1 to 3);
      signal String_array : type_string_array := (
		%%TESTPATTERN_STRINGS
            );
             
begin
	-- concatenate all control signals to one std_logic_vector:
      Controls <= RegDst & Branch & Jump & MemRead & MemtoReg & MemWrite & ALUControl & ALUSrc & RegWrite;
      
      UUT: SC_CU_beh
            port map
            (     Opcode => Opcode,
                  Funct => Funct,
                  Zero => Zero,
                  
                  RegDst => RegDst,
                  Branch => Branch,
                  Jump => Jump,
                  MemRead => MemRead,
                  MemtoReg    => MemtoReg,
                  MemWrite    => MemWrite,
                  ALUControl => ALUControl,
                  ALUSrc => ALUSrc,
                  RegWrite => RegWrite );

      feed_UUT: process(CLK)
            variable i : integer := 0;
      begin
            if(rising_edge(CLK)) then
                  if i < array_size  then
                        Opcode <= Inputs_test_array(i)(12 downto 6);
                        Funct <= Inputs_test_array(i)(6 downto 1);
                        Zero <= Inputs_test_array(i)(0);
                        i := i + 1;
                  end if;
            end if;
      end process feed_UUT;
      
      test_UUT: process(CLK)
            variable i : integer := 0;
      begin
            if(falling_edge(CLK)) then
                  if i < array_size  then
                        if(std_match(Controls, Controls_test_array(i))) then
                              report "Instruction "
                              & String_array(i)
                              & " ...done";
                              if(i = (array_size-1)) then    -- if all testet control signals match:
                                    report "Success" severity failure;
                              end if;
                        else
                              report "§{Instruction '"
                              & String_array(i)
                              & "' failed}§"
                              severity failure;
                        end if;
                        i := i + 1;
                  end if;
            end if;
      end process test_UUT;

--    generate the global clock cycles:
   clk_generator : process
      begin
            CLK <= '0';
            wait for clk_period/2;  
            CLK <= '1';
            wait for clk_period/2; 
      end process;

end Behavioral;

