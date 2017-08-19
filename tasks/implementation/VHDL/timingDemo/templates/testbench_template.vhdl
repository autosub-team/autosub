
ENTITY timingDemo_tb IS END timingDemo_tb;

ARCHITECTURE tb OF timingDemo_tb IS
	signal N,O,P,E : integer;
BEGIN
   UUT: entity work.timingDemo PORT MAP(N=>N,O=>O,P=>P,E=>E);
   	process
		type result_array is array (natural range <>) of integer;
        	constant expected_result : result_array:=( --w;x;y;z
			%%TESTPATTERN
			);


	--Check the timing behavior
	  begin
	  wait for 0 ns;
	  if N /= 0 OR O /= 0 OR P /= 0  OR E /= 0 then
		report "§{Error for current time = " & time'image(now) & " (N, O, P, E)= (" & integer'image(N) & ", " & integer'image(O) & ", "
											    & integer'image(P) & ", " & integer'image(E) & ")" &
						                         " expected = (0, 0, 0, 0)§"
		severity failure;
     	   end if;

	   wait for 1 ns;
	   for i in 0 to 2 loop

	   wait for %%time_o1 ns;
		if N /= expected_result(12*i+0) OR O /= expected_result(12*i+1) OR P /= expected_result(12*i+2) OR  E /= expected_result(12*i+3) then
		report "§{Error for current time = " & time'image(now) & " (N, O, P, E)= (" & integer'image(N) & ", " & integer'image(O) & ", "
										 & integer'image(P) & ", " & integer'image(E) & ")" &
				 " expected = (" & integer'image(expected_result(12*i+0)) & ", " & integer'image(expected_result(12*i+1)) & ", "
										 & integer'image(expected_result(12*i+2)) & ", " & integer'image(expected_result(12*i+3)) & ")§"
		severity failure;
		end if;

	   wait for 1 ns;
		if N /= expected_result(12*i+4) OR O /= expected_result(12*i+5) OR P /= expected_result(12*i+6) OR  E /= expected_result(12*i+7) then
		report "§{Error for current time = " & time'image(now) & " (N, O, P, E)= (" & integer'image(N) & ", " & integer'image(O) & ", "
										 & integer'image(P) & ", " & integer'image(E) & ")" &
				 " expected = (" & integer'image(expected_result(12*i+4)) & ", " & integer'image(expected_result(12*i+5)) & ", "
										 & integer'image(expected_result(12*i+6)) & ", " & integer'image(expected_result(12*i+7)) & ")§"
		severity failure;
		end if;

  	   wait for %%time_p1 ns;
		if N /= expected_result(12*i+4) OR O /= expected_result(12*i+5) OR P /= expected_result(12*i+6) OR  E /= expected_result(12*i+7) then
		report "§{Error for current time = " & time'image(now) & " (N, O, P, E)= (" & integer'image(N) & ", " & integer'image(O) & ", "
										 & integer'image(P) & ", " & integer'image(E) & ")" &
				 " expected = (" & integer'image(expected_result(12*i+4)) & ", " & integer'image(expected_result(12*i+5)) & ", "
										 & integer'image(expected_result(12*i+6)) & ", " & integer'image(expected_result(12*i+7)) & ")§"
		severity failure;
		end if;
	   wait for 1 ns;
		if N /= expected_result(12*i+8) OR O /= expected_result(12*i+9) OR P /= expected_result(12*i+10) OR  E /= expected_result(12*i+11) then
		report "§{Error for current time = " & time'image(now) & " (N, O, P, E)= (" & integer'image(N) & ", " & integer'image(O) & ", "
										 & integer'image(P) & ", " & integer'image(E) & ")" &
				 " expected = (" & integer'image(expected_result(12*i+8)) & ", " & integer'image(expected_result(12*i+9)) & ", "
										 & integer'image(expected_result(12*i+10)) & ", " & integer'image(expected_result(12*i+11)) & ")§"
		severity failure;
		end if;

	   wait for %%time_e1 ns;
		if N /= expected_result(12*i+8) OR O /= expected_result(12*i+9) OR P /= expected_result(12*i+10) OR  E /= expected_result(12*i+11) then
		report "§{Error for current time = " & time'image(now) & " (N, O, P, E)= (" & integer'image(N) & ", " & integer'image(O) & ", "
										 & integer'image(P) & ", " & integer'image(E) & ")" &
				 " expected = (" & integer'image(expected_result(12*i+8)) & ", " & integer'image(expected_result(12*i+9)) & ", "
										 & integer'image(expected_result(12*i+10)) & ", " & integer'image(expected_result(12*i+11)) & ")§"
		severity failure;
		end if;

	   wait for 1 ns;
		if N /= expected_result(12*i+12) OR O /= expected_result(12*i+13) OR P /= expected_result(12*i+14) OR  E /= expected_result(12*i+15) then
		report "§{Error for current time = " & time'image(now) & " (N, O, P, E)= (" & integer'image(N) & ", " & integer'image(O) & ", "
										 & integer'image(P) & ", " & integer'image(E) & ")" &
				 " expected = (" & integer'image(expected_result(12*i+12)) & ", " & integer'image(expected_result(12*i+13)) & ", "
										 & integer'image(expected_result(12*i+14)) & ", " & integer'image(expected_result(12*i+15)) & ")§"
		severity failure;
		end if;
	end loop;

	report "Success" severity failure;
	wait;
	END PROCESS;
END tb;


