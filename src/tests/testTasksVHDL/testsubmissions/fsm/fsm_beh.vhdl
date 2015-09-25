library IEEE;
use IEEE.std_logic_1164.all;
use work.fsm_pkg.all;


architecture behavior of fsm is
   signal internal_state,internal_state_next : fsm_state;
   signal internal_output,internal_output_next: std_logic_vector(1 downto 0);   
begin
    --Next State Logic and Next Output Logic----
    nextState_nextOutput : process(internal_state, INPUT)
    begin
        internal_state_next<= internal_state;
        internal_output_next<=internal_output;

        case internal_state is 
           when START =>
               if INPUT = "00" then
                  internal_state_next <= S3;
                  internal_output_next <= "01";
               end if;
           when S0 =>
               if INPUT = "01" then
                  internal_state_next <= S1;
                  internal_output_next <= "01";
               end if;
           when S1 =>
               if INPUT = "10" then
                  internal_state_next <= S2;
                  internal_output_next <= "10";
               end if;
               if INPUT = "01" then
                  internal_state_next <= S1;
                  internal_output_next <= "01";
               end if;
               if INPUT = "00" then
                  internal_state_next <= S3;
                  internal_output_next <= "01";
               end if;
               if INPUT = "11" then
                  internal_state_next <= S0;
                  internal_output_next <= "10" ;
               end if;

           when S2 =>
               if INPUT = "01" then
                  internal_state_next <= S1;
                  internal_output_next <= "01" ;
               end if;
               if INPUT = "11" then
                  internal_state_next <= S3;
                  internal_output_next <= "11" ;
               end if;

           when S3 =>
               if INPUT = "11" then
                  internal_state_next <= S1;
                  internal_output_next <= "01" ;
               end if;
               if INPUT = "10" then
                  internal_state_next <= S2;
                  internal_output_next <= "01" ;
               end if;

           when others=>
               null;
       end case;
    end process nextState_nextOutput;

    --Sync and Reset Logic--  
    sync_proc : process(clk, rst)
    begin
        if(rising_edge(CLK)) then
            if RST = '1' then
               internal_state  <= START;
	       internal_output <= "00";
            else 
	       internal_state <= internal_state_next;
	       internal_output <= internal_output_next;
            end if;
        end if;
    end process sync_proc;

    OUTPUT <= internal_output;
    STATE <= internal_state;
    
end behavior;
