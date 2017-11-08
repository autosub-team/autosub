library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity MC_CU_tb is
end MC_CU_tb;

architecture behavior of MC_CU_tb is

    component MC_CU
    port(
         CLK : in  std_logic;
         Opcode : in  std_logic_vector(5 downto 0);
         Funct : in  std_logic_vector(5 downto 0);
         Zero : in  std_logic;
         IRWrite : out  std_logic;
         MemWrite : out  std_logic;
         IorD : out  std_logic;
         PCWrite : out  std_logic;
         PCSrc : out  std_logic_vector(1 downto 0);
         ALUControl : out  std_logic_vector(2 downto 0);
         ALUSrcB : out  std_logic_vector(1 downto 0);
         ALUSrcA : out  std_logic;
         RegWrite : out  std_logic;
         MemtoReg : out  std_logic;
         RegDst : out  std_logic
        );
    end component;

   --Inputs
   signal CLK : std_logic := '0';
   signal Opcode : std_logic_vector(5 downto 0) := "000000";
   signal Funct : std_logic_vector(5 downto 0) :=  "000000";
   signal Zero : std_logic := '0';

    --Outputs
   signal IRWrite : std_logic;
   signal MemWrite : std_logic;
   signal IorD : std_logic;
   signal PCWrite : std_logic;
   signal PCSrc : std_logic_vector(1 downto 0);
   signal ALUControl : std_logic_vector(2 downto 0);
   signal ALUSrcB : std_logic_vector(1 downto 0);
   signal ALUSrcA : std_logic;
   signal RegWrite : std_logic;
   signal MemtoReg : std_logic;
   signal RegDst : std_logic;

   -- Clock period definitions
   constant CLK_period : time := 10 ns;

   signal Controls : std_logic_vector(14 downto 0);
   signal Zero_out : std_logic := '0';

begin

   Controls(14) <= IorD;
   Controls(13) <= ALUSrcA;
   Controls(12 downto 11) <= ALUSrcB;
   Controls(10 downto 8) <= ALUControl;
   Controls(7 downto 6) <= PCSrc;
   Controls(5) <= IRWrite;
   Controls(4) <= PCWrite;
   Controls(3) <= RegDst;
   Controls(2) <= MemtoReg;
   Controls(1) <= RegWrite;
   Controls(0) <= MemWrite;

   -- Instantiate the Unit Under Test (UUT)
   uut: MC_CU port map (
          CLK => CLK,
          Opcode => Opcode,
          Funct => Funct,
          Zero => Zero,
          IRWrite => IRWrite,
          MemWrite => MemWrite,
          IorD => IorD,
          PCWrite => PCWrite,
          PCSrc => PCSrc,
          ALUControl => ALUControl,
          ALUSrcB => ALUSrcB,
          ALUSrcA => ALUSrcA,
          RegWrite => RegWrite,
          MemtoReg => MemtoReg,
          RegDst => RegDst
        );

   -- Clock process definitions
   CLK_process :process
   begin
      CLK <= '0';
      wait for CLK_period/2;
      CLK <= '1';
      wait for CLK_period/2;
   end process;

   -- asynchronous control of ALU Zero output
   ALU_zero: process(Controls)
   begin
      if (std_match(Controls, "-100010010---00")) then
         Zero <= Zero_out;
      else
         Zero <= '0';
      end if;
   end process ALU_zero;

   -- Stimulus process
   stim_proc: process
   begin
      wait until rising_edge(CLK); -- wait for first rising edge

      -- instruction test 1:
      {{instruction_test_1}}

      -- instruction test 2:
      {{instruction_test_2}}

      -- instruction test 3:
      {{instruction_test_3}}

      -- instruction test 4:
      {{instruction_test_4}}

      report "Success" severity failure;
   end process;

end;
