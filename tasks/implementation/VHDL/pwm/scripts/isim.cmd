onerror {quit -f}
vcd dumpfile signals.vcd
vcd dumpvars -m /UUT
run 150ms;
vcd dumpflush
quit -f
