library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

entity MC_CU is
	port(
		CLK         : in   std_logic;
		Opcode      : in   std_logic_vector(6-1 downto 0);
		Funct       : in   std_logic_vector(6-1 downto 0);
		Zero        : in   std_logic;
		IRWrite     : out  std_logic;
		MemWrite    : out  std_logic;
		IorD        : out  std_logic;
		PCWrite     : out  std_logic;
		PCSrc       : out  std_logic_vector(2-1 downto 0);
		ALUControl  : out  std_logic_vector(3-1 downto 0);
		ALUSrcB     : out  std_logic_vector(2-1 downto 0);
		ALUSrcA     : out  std_logic;
		RegWrite    : out  std_logic;
		MemtoReg    : out  std_logic;
		RegDst      : out  std_logic
	);
end MC_CU;