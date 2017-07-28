library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

entity {{ entity_name }} is
	port(
	{% for input in inputs %}
		{{ input.name }}  : in   {{ input.type }};
	{% endfor %}
	{% for output in outputs %}
		{{ output.name }}  : out  {{ output.type }}{{ ";" if not loop.last }}
	{% endfor %}
	);
end {{ entity_name }};
