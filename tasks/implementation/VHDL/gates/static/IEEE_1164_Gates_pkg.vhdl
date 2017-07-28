library ieee;
use ieee.std_logic_1164.all;

package IEEE_1164_Gates_pkg is

--##########################
--######## AND GATES #######
--##########################    
    component AND2 is
        port
        (
            I1  :in  std_logic;
            I2  :in  std_logic;
            O   :out std_logic
        );
    end component AND2;

    component AND3 is
        port
        (
            I1  :in  std_logic;
            I2  :in  std_logic;
            I3  :in  std_logic;
            O   :out std_logic
        );
    end component AND3;

    component AND4 is
        port
        (
            I1  :in  std_logic;
            I2  :in  std_logic;
            I3  :in  std_logic;
            I4  :in  std_logic;
            O   :out std_logic
        );
    end component AND4;

--##########################
--######## NAND GATES ######
--##########################    
    component NAND2 is
        port
        (
            I1  :in  std_logic;
            I2  :in  std_logic;
            O   :out std_logic
        );
    end component NAND2;

    component NAND3 is
        port
        (
            I1  :in  std_logic;
            I2  :in  std_logic;
            I3  :in  std_logic;
            O   :out std_logic
        );
    end component NAND3;

    component NAND4 is
        port
        (
            I1  :in  std_logic;
            I2  :in  std_logic;
            I3  :in  std_logic;
            I4  :in  std_logic;
            O   :out std_logic
        );
    end component NAND4;

--##########################
--######## OR GATES ########
--##########################    
    component OR2 is
        port
        (
            I1  :in  std_logic;
            I2  :in  std_logic;
            O   :out std_logic
        );
    end component OR2;

    component OR3 is
        port
        (
            I1  :in  std_logic;
            I2  :in  std_logic;
            I3  :in  std_logic;
            O   :out std_logic
        );
    end component OR3;

    component OR4 is
        port
        (
            I1  :in  std_logic;
            I2  :in  std_logic;
            I3  :in  std_logic;
            I4  :in  std_logic;
            O   :out std_logic
        );
    end component OR4;

--##########################
--######## NOR GATES #######
--##########################    
    component NOR2 is
        port
        (
            I1  :in  std_logic;
            I2  :in  std_logic;
            O   :out std_logic
        );
    end component NOR2;

    component NOR3 is
        port
        (
            I1  :in  std_logic;
            I2  :in  std_logic;
            I3  :in  std_logic;
            O   :out std_logic
        );
    end component NOR3;

    component NOR4 is
        port
        (
            I1  :in  std_logic;
            I2  :in  std_logic;
            I3  :in  std_logic;
            I4  :in  std_logic;
            O   :out std_logic
        );
    end component NOR4;

--##########################
--######## XOR GATES #######
--##########################    
    component XOR2 is
        port
        (
            I1  :in  std_logic;
            I2  :in  std_logic;
            O   :out std_logic
        );
    end component XOR2;

    component XOR3 is
        port
        (
            I1  :in  std_logic;
            I2  :in  std_logic;
            I3  :in  std_logic;
            O   :out std_logic
        );
    end component XOR3;

    component XOR4 is
        port
        (
            I1  :in  std_logic;
            I2  :in  std_logic;
            I3  :in  std_logic;
            I4  :in  std_logic;
            O   :out std_logic
        );
    end component XOR4;

--##########################
--######## XNOR GATES ######
--##########################    
    component XNOR2 is
        port
        (
            I1  :in  std_logic;
            I2  :in  std_logic;
            O   :out std_logic
        );
    end component XNOR2;

    component XNOR3 is
        port
        (
            I1  :in  std_logic;
            I2  :in  std_logic;
            I3  :in  std_logic;
            O   :out std_logic
        );
    end component XNOR3;

    component XNOR4 is
        port
        (
            I1  :in  std_logic;
            I2  :in  std_logic;
            I3  :in  std_logic;
            I4  :in  std_logic;
            O   :out std_logic
        );
    end component XNOR4;


end IEEE_1164_Gates_pkg;
