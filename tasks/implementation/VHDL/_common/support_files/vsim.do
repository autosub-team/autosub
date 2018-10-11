onerror {vcd dumpportsflush; quit -f}
vcd file signals.vcd
vcd add */UUT
run -all
vcd dumpportsflush
quit -f
