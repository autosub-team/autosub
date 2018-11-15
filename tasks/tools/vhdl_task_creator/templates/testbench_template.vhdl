library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;
use std.textio.all;
use IEEE.std_logic_textio.all;

entity {{ task_name }}_tb is
end {{ task_name }}_tb;

architecture behavior of {{ task_name }}_tb is

    -- function to converte std_logic_vectors to string
    function slv_image(in_image : std_logic_vector) return string is
        variable L : Line;  -- access type
        variable W : String(1 to in_image'length) := (others => ' ');
    begin
        WRITE(L, in_image);
        W(L.all'range) := L.all;
        Deallocate(L);
        return W;
    end slv_image;

    --components
    {% for comp in components %}
    component {{ comp.entity_name }}
        port(
	{% for input in comp.inputs %}
            {{ input.name }}  : in   {{ input.type }};
	{% endfor %}
	{% for output in comp.outputs %}
	    {{ output.name }}  : out  {{ output.type }}{{ ";" if not loop.last }}
	{% endfor %}
	);
    end component;

    {% endfor %}

    --put your code here

begin

    -- clock generator
    clk_generator : process
        constant clk_period : time := 20 ns;
    begin
        clk_uut <= '0';
        wait for clk_period/2;
        clk_uut <= '1';
        wait for clk_period/2;
    end process;

    --put your code here
end behavior;
