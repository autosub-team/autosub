library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use std.textio.all;
use ieee.std_logic_textio.all;

entity counter_tb is
end counter_tb;

architecture Behavioral of counter_tb is
    component counter is
        port (
            CLK         : in   std_logic;
            RST         : in   std_logic;
        {% if enable %}
            Enable      : in   std_logic;
        {% endif %}
            Sync{{sync_variation}}   : in   std_logic;
            Async{{async_variation}}   : in   std_logic;
        {% if input_necessary %}
            Input       : in   std_logic_vector(({{counter_width}}-1) downto 0);
        {% endif %}
        {% if overflow %}
            Overflow    : out  std_logic;
        {% endif %}
            Output      : out  std_logic_vector(({{counter_width}}-1) downto 0)
    );
    end component;

    constant random_counter_value : integer := {{random_counter_value}};
    constant init_value : integer := {{init_value}};
    constant counter_width : integer := {{counter_width}};
    constant counter_max : integer := {{counter_max}};

    type type_input_test_array is array(0 to (3 - 1)) of std_logic_vector((counter_width-1) downto 0);
    signal input_test_array : type_input_test_array := ({{input_test_array}});

    -- signals for Inputs and Outputs:
    signal CLK : std_logic := '0';
    signal RST : std_logic := '0';
{% if enable %}
    signal Enable : std_logic := '0';
{% endif %}
    signal Sync{{sync_variation}} : std_logic := '0';
    signal Async{{async_variation}} : std_logic := '0';
{% if input_necessary %}
    signal Input  : std_logic_vector(({{counter_width}}-1) downto 0);
{% endif %}
    signal Output: std_logic_vector(({{counter_width}}-1) downto 0);
{% if overflow %}
    signal Overflow : std_logic := '0';
{% endif %}

    -- Clock period definitions:
    constant CLK_period : time := 20 ns;

    function image(in_image : std_logic_vector) return string is
        variable L : Line;  -- access type
        variable W : String(1 to in_image'length) := (others => ' ');
    begin
        WRITE(L, in_image);
        W(L.all'range) := L.all;
        Deallocate(L);
        return W;
    end image;

begin

    UUT: counter
        port map
        (    CLK => CLK,
            RST => RST,
{% if enable %}
            Enable => Enable,
{% endif %}
            Sync{{sync_variation}} => Sync{{sync_variation}},
            Async{{async_variation}} => Async{{async_variation}},
{% if input_necessary %}
            Input => Input,
{% endif %}
{% if overflow %}
            Overflow => Overflow,
{% endif %}
            Output => Output
        );

    -- Clock process definitions
       CLK_process :process
       begin
        CLK <= '0';
        wait for CLK_period/2;
        CLK <= '1';
        wait for CLK_period/2;
    end process;

    test_counter_beh: process
        variable i : integer := 0;
    begin

        -- NOTE: Value Tests are always done 1/4 period after rising_edge
        RST    <= '0';
{% if enable %}
        Enable <= '1';
{% endif %}
        -----------------------------
        -- check initial value after reset
        -----------------------------
        wait until rising_edge(CLK);
        wait until rising_edge(CLK);
        wait until falling_edge(CLK);

        RST <= '1';
        wait until rising_edge(CLK);
        wait for CLK_period/4;

        if (Output /= std_logic_vector(to_unsigned(init_value, Output'length))) then
            report "§{Initial counter value after reset not right. Received " & image(Output) & ". Expected " & image(std_logic_vector(to_unsigned(init_value, Output'length))) & ".}§" severity failure;
        end if;

        RST <= '0';

    {% if enable %}
        -----------------------------
        -- do the enable check
        -----------------------------
        RST <= '1';
        wait until rising_edge(CLK);
        wait for CLK_period/4;
        RST <= '0';

        Enable <= '0';
        for i in (init_value) to (2*counter_max) loop
            if (Output /= std_logic_vector(to_unsigned(init_value, Output'length))) then
                report "§{Counter value changed while Enable = '0'. Received " & image(Output) & ". Expected " & image(std_logic_vector(to_unsigned(init_value, Output'length))) & ".}§" severity failure;
            end if;
            wait for CLK_period;
        end loop;
        Enable <= '1';
        wait for CLK_period;
    {% endif %}

    {% if overflow %}
        -----------------------------
        -- do the overflow check
        -----------------------------

        RST <= '1';
        wait until rising_edge(CLK);
        wait for CLK_period/4;
        RST <= '0';

        for i in (init_value) to (counter_max) loop
            if (Overflow /= '0') then
                report "§{Overflow was '" & std_logic'image(Overflow) & "' when it was expected to be '0'. Current counter value is " & image(Output) & ".}§" severity failure;
            end if;
            wait for CLK_period;
        end loop;

        if (Overflow /= '1') then
            report "§{Overflow was '" & std_logic'image(Overflow) & "' when it was expected to be '1'. Current counter value is " & image(Output) & ".}§" severity failure;
        end if;

        for i in (init_value) to (counter_max-1) loop
            wait for CLK_period;
            if (Overflow /= '0') then
                report "§{Overflow was '" & std_logic'image(Overflow) & "' when it was expected to be '0'. Current counter value is " & image(Output) & ".}§" severity failure;
            end if;
        end loop;
            wait for CLK_period;
    {% endif %}

        -----------------------------
        -- check counter one full cycle:
        -----------------------------

        RST <= '1';
        wait until rising_edge(CLK);
        wait for CLK_period/4;
        RST <= '0';

        for i in (init_value) to (counter_max) loop
            if (Output /= std_logic_vector(to_unsigned(i, Output'length))) then
                report "§{Output value not right while counting up. Received " & image(Output) & ". Expected " & image(std_logic_vector(to_unsigned(i, Output'length))) & ".}§" severity failure;
            end if;
            wait for CLK_period;
        end loop;

        -----------------------------
        -- do the synchronous check:
        -----------------------------
        RST <= '1';
        wait until rising_edge(CLK);
        wait for CLK_period/4;
        RST <= '0';

        {# hack to allow right scoping #}
        {% set ns = namespace(synchronous_value_integer_vector = "L0") %}
        {% set ns = namespace(synchronous_value_integer = "L1") %}

        {% if sync_variation == "Clear" %}
            {% set ns.synchronous_value_integer_vector = "std_logic_vector(to_unsigned(0,Output'length))" %}
            {% set ns.synchronous_value_integer = "0" %}
        {% elif sync_variation ==  "LoadConstant" %}
            {% set ns.synchronous_value_integer_vector = '"' + constant_value + '"' %}
            {% set ns.synchronous_value_integer = constant_value_bin %}
        {% elif sync_variation == "LoadInput" %}
            {% set ns.synchronous_value_integer_vector = "input_test_array(j)" %}
            {% set ns.synchronous_value_integer = "to_integer(unsigned(input_test_array(j)))" %}
        {% endif %}

        {% if sync_variation == "LoadInput" %}
            for j in 0 to 2 loop
                Input <= input_test_array(j);
        {% endif %}

                for i in 1 to random_counter_value loop
                    wait for CLK_period;
                end loop;

                Sync{{sync_variation}} <= '1';
                wait for CLK_period/4;
                if (Output = {{ns.synchronous_value_integer_vector}}) then
                    report "§{Sync{{sync_variation}} not synchronous to CLK. Received " & image(Output) & ". Expected " & image(std_logic_vector(to_unsigned(random_counter_value, Output'length))) & ".}§" severity failure;
                end if;
                wait for CLK_period*3/4;
                if (Output /= {{ns.synchronous_value_integer_vector}}) then
                    report "§{Sync{{sync_variation}} not setting the right Output value. Received " & image(Output) & ". Expected " & image({{ns.synchronous_value_integer_vector}}) & ".}§" severity failure;
                end if;
                wait for CLK_period/4;
                Sync{{sync_variation}} <= '0';
                wait for CLK_period*3/4;

                for i in ({{ns.synchronous_value_integer}}+1) to (counter_max-1) loop
                    if (Output /= std_logic_vector(to_unsigned(i, Output'length))) then
                        report "§{Wrong Output value after Sync{{sync_variation}}. Received " & image(Output) & ". Expected " & image(std_logic_vector(to_unsigned(i, Output'length))) & ".}§" severity failure;
                    end if;
                    wait for CLK_period;
                end loop;

        {% if sync_variation == "LoadInput" %}
            end loop;
        {% endif %}

        -----------------------------
        -- do the asynchronous check:
        -----------------------------
        RST <= '1';
        wait until rising_edge(CLK);
        wait for CLK_period/4;
        RST <= '0';
		
        {# hack to allow right scoping #}
        {% set ns = namespace(asynchronous_value_integer_vector = "L2") %}
        {% set ns = namespace(asynchronous_value_integer = "L3") %}

        {% if async_variation == "Clear" %}
            {% set ns.asynchronous_value_integer_vector = "std_logic_vector(to_unsigned(0, Output'length))" %}
            {% set ns.asynchronous_value_integer = "0" %}
        {% elif async_variation == "LoadConstant" %}
            {% set ns.asynchronous_value_integer_vector = '"' + constant_value + '"' %}
            {% set ns.asynchronous_value_integer = constant_value_bin %}
        {% elif async_variation == "LoadInput" %}
            {% set ns.asynchronous_value_integer_vector = "input_test_array(j)" %}
            {% set ns.asynchronous_value_integer = "to_integer(unsigned(input_test_array(j)))" %}
        {% endif %}

        {% if async_variation == "LoadInput" %}
            for j in 0 to 2 loop
                Input <= input_test_array(j);
        {% endif %}

                for i in 0 to random_counter_value loop
                    wait for CLK_period;
                end loop;

                Async{{async_variation}} <= '1';
                wait for CLK_period/4;
                if (Output /= {{ns.asynchronous_value_integer_vector}} ) then
                    report "§{Async{{async_variation}} not setting the right Output value. Received " & image(Output) & ". Expected " &image({{ns.asynchronous_value_integer_vector}}) & ".}§" severity failure;
                end if;
                wait for CLK_period/4;
                Async{{async_variation}} <= '0';
                wait for CLK_period/2;

                for i in ({{ns.asynchronous_value_integer}} +1) to (counter_max-1) loop
                    if (Output /= std_logic_vector(to_unsigned(i, Output'length))) then
                        report "§{Wrong Output value after Async{{async_variation}}. Received " & image(Output) & ". Expected " & image(std_logic_vector(to_unsigned(i, Output'length))) & ".}§" severity failure;
                    end if;
                    wait for CLK_period;
                end loop;

        {% if async_variation == "LoadInput" %}
            end loop;
        {% endif %}

    report "Success" severity failure;
    end process test_counter_beh;

end Behavioral;
