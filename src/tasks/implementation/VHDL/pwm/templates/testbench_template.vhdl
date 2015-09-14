-- natural is from 0 to integer'high

library IEEE;
use IEEE.std_logic_1164.all;

entity pwm_tb is
end pwm_tb;

architecture behavior of pwm_tb is
    component pwm
         port(  CLK     : in    std_logic;
                O       : out   std_logic);
    end component;

    constant clk_period : time := 20 ns; -- for 50MHz -> 20 ns
 
    constant desired_period_clks: natural := %%PERIODCLKS;
    constant desired_duty_cycle_clks : natural:= %%DUTYCLKS;

    constant desired_period: time := desired_period_clks*clk_period;
    constant desired_duty_cycle : natural:= desired_duty_cycle_clks*100 / desired_period_clks ;
    
    constant simulation_cycles : natural := %%SIMCYCLES;
 
    signal CLK_UUT,O_UUT: std_logic;

    signal clk_cnt: natural :=0; 
    
    type clk_cnts_array is array (simulation_cycles downto 0) of natural;
    signal pulse_starts : clk_cnts_array;
    signal pulse_ends : clk_cnts_array;

    procedure evaluate_PWM is 
        type periods_array is array ( (simulation_cycles-1) downto 0) of time;
        subtype percentage is natural range 0 to 100;
        type duties_array is array ( (simulation_cycles-1) downto 0) of percentage;

        variable periods: periods_array;
        variable duty_cycles : duties_array;

        variable duty_cycle_clks: clk_cnts_array;
        variable period_clks: clk_cnts_array;
    begin
        -- calculate period,duty,frequency
        for i in 0 to (simulation_cycles-1) loop
            if(pulse_starts(i+1) < pulse_starts(i)) then --overflow of clk_cnt happened happened
                -- max - begin + 1(for max to 0) + end 
                period_clks(i) := integer'high-pulse_starts(i)+1+pulse_starts(i+1);
            else
                period_clks(i) := pulse_starts(i+1) - pulse_starts(i);            
            end if;

            if(pulse_ends(i) < pulse_starts(i)) then --overflow of clk_cnt happened
                -- max - begin + 1(for max to 0) + end 
                duty_cycle_clks(i) := integer'high - pulse_starts(i) + 1 + pulse_ends(i);
            else
                duty_cycle_clks(i) := pulse_ends(i) - pulse_starts(i);
            end if;

            duty_cycles(i) := duty_cycle_clks(i)*100/period_clks(i);
            periods(i) := period_clks(i) * clk_period;
        end loop;

        -- check the frequency by comparing clk counts
        -- +-1 clk is okay
        for i in 0 to (simulation_cycles-1) loop
            if( ( (desired_period_clks-1)<=period_clks(i) ) and (desired_period_clks+1)>=period_clks(i) ) then
                next;
            else
            report  "Period not right (Should be " & natural'image(desired_period/(1 ns)) & "ns);First 5 measured Periods:" &
                    natural'image(periods(0)/(1 ns)) & "ns, " & 
                    natural'image(periods(1)/(1 ns)) & "ns, " & 
                    natural'image(periods(2)/(1 ns)) & "ns, " & 
                    natural'image(periods(3)/(1 ns)) & "ns, " & 
                    natural'image(periods(4)/(1 ns)) & "ns"
                severity failure;
            end if;
        end loop;

        -- check the duty cycles by comparing clk counts
        -- +-1 clk is okay
        for i in 0 to (simulation_cycles-1) loop
            if( ( (desired_duty_cycle_clks-1)<=duty_cycle_clks(i) ) and ( (desired_duty_cycle_clks+1)>=duty_cycle_clks(i) ) ) then
                next;
            else
            report  "Duty cycle not right (Should be " & natural'image(desired_duty_cycle) & "%); First 5 measured duties:" & 
                    natural'image(duty_cycles(0)) & "%, " & 
                    natural'image(duty_cycles(1)) & "%, " & 
                    natural'image(duty_cycles(2)) & "%, " & 
                    natural'image(duty_cycles(3)) & "%, " & 
                    natural'image(duty_cycles(4)) & "%"
                severity failure;
            end if;
        end loop;
        report "Success" severity failure;
        
   end procedure;
    

begin

    UUT: pwm
        port map
        (
            CLK=>CLK_UUT,
            O=>O_UUT
        );

    --generates the global clock cycles 
    clk_generator : process
    begin
        CLK_UUT <= '0';
        wait for clk_period/2;  
        CLK_UUT <= '1';
        wait for clk_period/2; 
    end process;

    --counts the global clock cycles
    clk_count : process (CLK_UUT)
    begin
        if(rising_edge(CLK_UUT)) then
            clk_cnt <= clk_cnt+1;
        end if;  
    end process;     

   -- process to find output pulse begins and pulse ends

    findParams: process
        variable cur_sim_cycle: integer := 0;
    begin 
        wait until rising_edge(O_UUT);
        pulse_starts(cur_sim_cycle) <= clk_cnt;
        wait until falling_edge(O_UUT);
        pulse_ends(cur_sim_cycle) <= clk_cnt;
        cur_sim_cycle := cur_sim_cycle +1;
        if(cur_sim_cycle = (simulation_cycles+1) ) then
            evaluate_PWM;
            wait; 
        end if;
        
    end process;


end behavior;
