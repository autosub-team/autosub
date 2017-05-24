onerror {quit -f}
wave add /pwm_tb/CLK_UUT
wave add /pwm_tb/O_UUT
run 150ms;
quit -f
