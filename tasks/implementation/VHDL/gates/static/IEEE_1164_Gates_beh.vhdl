library ieee;
use ieee.std_logic_1164.all;

--##########################
--######## AND GATES #######
--##########################    
architecture behavior of AND2 is 
begin
    O<= I1 and I2;
end architecture behavior;

architecture behavior of AND3 is 
begin
    O<= I1 and I2 and I3;
end architecture behavior;

architecture behavior of AND4 is 
begin
    O<= I1 and I2 and I3 and I4;
end architecture behavior;

--##########################
--######## NAND GATES ######
--##########################  
architecture behavior of NAND2 is 
begin
    O<= not(I1 and I2);
end architecture behavior;

architecture behavior of NAND3 is 
begin
    O<= not(I1 and I2 and I3);
end architecture behavior;

architecture behavior of NAND4 is 
begin
    O<= not(I1 and I2 and I3 and I4);
end architecture behavior;

--##########################
--######## OR GATES ########
--########################## 
architecture behavior of OR2 is 
begin
    O<= I1 or I2;
end architecture behavior;

architecture behavior of OR3 is 
begin
    O<= I1 or I2 or I3;
end architecture behavior;

architecture behavior of OR4 is 
begin
    O<= I1 or I2 or I3 or I4;
end architecture behavior;

--##########################
--######## NOR GATES #######
--##########################  
architecture behavior of NOR2 is 
begin
    O<= not(I1 or I2);
end architecture behavior;

architecture behavior of NOR3 is 
begin
    O<= not(I1 or I2 or I3);
end architecture behavior;

architecture behavior of NOR4 is 
begin
    O<= not(I1 or I2 or I3 or I4);
end architecture behavior;

--##########################
--######## XOR GATES #######
--########################## 
architecture behavior of XOR2 is 
begin
    O<= I1 xor I2;
end architecture behavior;

architecture behavior of XOR3 is 
begin
    O<= I1 xor I2 xor I3;
end architecture behavior;

architecture behavior of XOR4 is 
begin
    O<= I1 xor I2 xor I3 xor I4;
end architecture behavior;

--##########################
--######## XNOR GATES ######
--########################## 

architecture behavior of XNOR2 is 
begin
    O<= not(I1 xor I2);
end architecture behavior;

architecture behavior of XNOR3 is 
begin
    O<= not(I1 xor I2 xor I3);
end architecture behavior;

architecture behavior of XNOR4 is 
begin
    O<= not(I1 xor I2 xor I3 xor I4);
end architecture behavior;
