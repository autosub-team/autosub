library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity SC_CU is
    port( Opcode    : in  std_logic_vector(5 downto 0);
          Funct     : in  std_logic_vector(5 downto 0);
          Zero      : in  std_logic;

          RegDst    : out std_logic;
          Branch    : out std_logic;
          Jump      : out std_logic;
          MemRead   : out std_logic;
          MemtoReg  : out std_logic;
          MemWrite  : out std_logic;
          ALUControl: out std_logic_vector(2 downto 0);
          ALUSrc    : out std_logic;
          RegWrite  : out std_logic);
end SC_CU;
