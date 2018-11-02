library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use std.textio.all;
use ieee.std_logic_textio.all;

entity demux_tb is
end demux_tb;

architecture Behavioral of demux_tb is

   component demux is
       port ( IN1  : in   std_logic_vector(({{IN1_width}} - 1) downto 0);
              SEL  : in   std_logic_vector(({{SEL_width}} - 1) downto 0);
              {{outputs_component}}
   end component;

   signal IN1 : std_logic_vector(({{IN1_width}} - 1) downto 0);
   signal SEL : std_logic_vector(({{SEL_width}} - 1) downto 0);
   {{output_signals}}

   type type_outputs_test_array is array(0 to ({{num_out}} - 1)) of std_logic_vector(({{IN1_width}} - 1) downto 0);
   signal outputs_test_array : type_outputs_test_array;

   type type_input_test_array is array(0 to (3 - 1)) of std_logic_vector(({{IN1_width}} - 1) downto 0);
   signal input_test_array : type_input_test_array := ({{input_test_array}});

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

   UUT: demux
      port map
      (   IN1 => IN1,
         SEL => SEL,
         {{outputs_port_map}} );

   {{outputs_test_array}}

   feed_demux_beh: process
      variable i : integer := 0;
   begin
      -- loop over three test vectors for IN1:
      for k in 0 to 2 loop
         IN1 <= input_test_array(k);
         -- loop over all possible values of SEL:
         for i in 0 to ({{SEL_max}} - 1) loop
            wait for 1 ns;
            SEL <= std_logic_vector(to_unsigned(i, SEL'length));
               -- loop over all outputs:
               for j in 0 to ({{num_out}} -1) loop
                  wait for 1 ns;
                  if j = i then
                     if (outputs_test_array(j) /= IN1) then
                        report "§{OUT" & integer'image(j+1) & " was "& image(outputs_test_array(j)) & " for SEL=" & image(SEL) & " and IN1=" & image(IN1) & ". Expected OUT" & integer'image(j+1) & " to be " & image(IN1) & ".}§" severity failure;
                     end if;
                  elsif j /= i then
                     if outputs_test_array(j) /= (IN1'range => '0') then
                        report "§{OUT" & integer'image(j+1) & " was "& image(outputs_test_array(j)) & " for SEL=" & image(SEL) & ". Expected OUT" & integer'image(j+1) & " to be " & image((IN1'range => '0')) & ".}§" severity failure;
                     end if;
                  end if;
               end loop;
         end loop;
      end loop;

    -- Now apply SEL = 0 and vary IN1 (to check if user has used correct sensitivity list with both IN1 and SEL)
    wait for 1 ns;
    SEL <= std_logic_vector(to_unsigned(0, SEL'length));

    for k in 0 to 2 loop
        IN1 <= input_test_array(k);
        wait for 1 ns;
        if (outputs_test_array(0) /= IN1) then
            report "§{OUT" & integer'image(0+1) & " was "& image(outputs_test_array(0)) & " for SEL=" & image(SEL) & " and IN1=" & image(IN1) & ". Expected OUT" & integer'image(0+1) & " to be " & image(IN1) & ".}§" severity failure;
        end if;
    end loop;

      report "Success" severity failure;

   end process feed_demux_beh;

end Behavioral;

