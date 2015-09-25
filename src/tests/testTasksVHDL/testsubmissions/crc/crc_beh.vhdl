library IEEE;
use IEEE.std_logic_1164.all;

architecture behavior of crc is

    constant msg_len :integer := 21;
    constant gen_degree : integer := 8;

    type crc_state is 
    (
       PREPARE,
       CALC,
       FINISH,
       IDLE      
    );
    
    signal state,state_next : crc_state;
    signal EN_next, RST_next,CRC_VALID_next: std_logic;
    signal bit_nr,bit_nr_next:integer;
    signal DATA_IN_next: std_logic;

    component fsr is
        port 
        (
            EN      : in std_logic;
            RST     : in std_logic; -- rising edge of RST should reset the content of the shift register to all 0
            CLK     : in std_logic; -- shift and feedback operations should be done on rising edge of CLK
            DATA_IN : in std_logic; -- the bit which shall be shifted in
            DATA    : out std_logic_vector(gen_degree-1 downto 0) -- the current content  of the feedback shift register
        );
    end component;
    
    signal EN,RST,CLK_UUT,DATA_In : std_logic;
    signal DATA: std_logic_vector(gen_degree-1 downto 0);

begin
    CLK_UUT<=CLK;
    UUT:fsr
        port map
        (
            EN=>EN,
            RST=>RST,
            CLK=>CLK_UUT,
            DATA_IN=>DATA_IN,
            DATA=>DATA
        );
       

 --Next State Logic and communication with FSR----
    nextState : process(state,bit_nr)
    constant top_bit :integer:= msg_len-1;
    
    begin
        case state is 
           when PREPARE =>
                CRC_VALID_next<='0';
                EN_next<='1';
                RST_next<='1';
                bit_nr_next<=top_bit;
                state_next<=CALC;

           when CALC =>
                RST_next<='0';
                DATA_IN_next<=MSG(bit_nr);

                if(bit_nr=0) then
                    state_next<=FINISH;
                else
                    state_next<=CALC;
                    bit_nr_next<=bit_nr-1;
                end if;
                           
            when FINISH =>
                EN_next<='0';
                
                CRC_VALID_next<='1';
                
                state_next<=IDLE;
           
            when IDLE =>
                 CRC <= DATA;
                 state_next <= IDLE;
                
            when others=>
               null;
       end case;
    end process nextState;


--Sync and Reset Logic--  
    sync_proc : process(clk, NEW_MSG)
    begin
        if rising_edge(NEW_MSG) then
            state  <= PREPARE;
        elsif(rising_edge(CLK)) then 
	    state <= state_next;
            EN <= EN_next;
            RST <= RST_next;
            CRC_VALID <= CRC_VALID_next;
            bit_nr <=bit_nr_next;
            DATA_in<=DATA_IN_next;
        end if;        
    end process sync_proc;
end behavior;         
