package fsm_pkg is
    type fsm_state is
    (
    {% for num in range(0,num_states) %}
        {%- if loop.first%}    START{% else %}    S{{num - 1}}{% endif %}
        {%- if not loop.last %},{% endif %}

    {% endfor -%}
    );
end package fsm_pkg;
