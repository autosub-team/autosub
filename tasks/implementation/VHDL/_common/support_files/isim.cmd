onerror {quit -f}
vcd dumpfile signals.vcd
vcd dumpvars -m /UUT
run all;
vcd dumpflush
quit -f
