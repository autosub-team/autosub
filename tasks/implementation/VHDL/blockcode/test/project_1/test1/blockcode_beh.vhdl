library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

architecture behavior of blockcode is
	constant fifo_length : integer := 4;

	constant code_width : integer := 8;
	constant data_width : integer := 5;

	type memory_type is array (fifo_length-1 downto 0) of std_logic_vector(0 to code_width-1);

	type fifo_state is record
		data				: memory_type;
		read_ptr, write_ptr : integer range 0 to fifo_length-1;
		looped				: boolean;
	end record fifo_state;

	type output_type is record
		code			: std_logic_vector(0 to code_width-1);
		code_valid		: std_logic;
	end record output_type;

	signal output, output_next : output_type;
	signal fifo_sig : fifo_state;
	signal place_sig : boolean;
	signal code_available_sig : boolean;

begin

	encode_buffer: process (rst, data_valid, data, sink_ready, output)
		variable fifo : fifo_state;
		variable sending : boolean;
		variable transmission_success : boolean;
		variable code_available : boolean;
		variable place_left: boolean;
	begin
		if rst = '1' then
			fifo.data := (others => (others => '0'));
			fifo.write_ptr := 0;
			fifo.read_ptr := 0;
			fifo.looped := false;

			output_next.code <= (others => '0');
            output_next.code_valid <= '0';

			sending := false;
			code_available := false;
			transmission_success := false;
			place_left := true;
		else
			
			output_next	<= output;

			sending := output.code_valid = '1';
			transmission_success := sending and (sink_ready = '1');

			place_left := (fifo.looped = false) or (fifo.write_ptr /= fifo.read_ptr);
			place_sig <= place_left;
			
			if data_valid = '1' and (place_left = true) then    
                fifo.data(fifo.write_ptr)(0) := data(0);
                fifo.data(fifo.write_ptr)(1) := data(1);
                fifo.data(fifo.write_ptr)(2) := data(2);
                fifo.data(fifo.write_ptr)(3) := data(3);
                fifo.data(fifo.write_ptr)(4) := data(4);
                fifo.data(fifo.write_ptr)(5) := data(0) xor data(1) xor data(2);
                fifo.data(fifo.write_ptr)(6) := data(2) xor data(4);
            fifo.data(fifo.write_ptr)(7) := data(1) xor data(3);

				
				if fifo.write_ptr = fifo_length-1 then
					fifo.write_ptr := 0;
					fifo.looped := true;
				else
					fifo.write_ptr := fifo.write_ptr + 1;
				end if;
			end if; 

			code_available := (fifo.looped = true) or (fifo.write_ptr /= fifo.read_ptr);
			code_available_sig <= code_available;

			if (not sending or transmission_success) and (code_available = true) then
				output_next.code <= fifo.data(fifo.read_ptr);
				output_next.code_valid <= '1';

				if fifo.read_ptr = fifo_length-1 then
					fifo.read_ptr := 0;
					fifo.looped := false;
				else
					fifo.read_ptr := fifo.read_ptr + 1;
				end if;
			elsif sending and not transmission_success then
				
			else
				output_next.code_valid <= '0';
			end if; 
		end if; 
		
		fifo_sig <= fifo;

	end process encode_buffer;

	synch: process (rst, clk)
	begin
		if rising_edge(clk) then
			output <= output_next;
		end if;

	end process synch;

	
	code_valid	<= output.code_valid;
	code		<= output.code;

end behavior;
