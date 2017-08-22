#!/bin/bash

cd /home/martin/autosub/src

rounds=100
positive=0
negative=0
zero=0

for ((n=0;n<$rounds;n++))
do
	../tasks/implementation/VHDL/blockcode/tester.sh 8 1 "8|5|['00111','11010','00011']" ghdl_tester_common.sh |grep correct
	RET=$?

	if [ "$RET" -ne "$zero" ]
	then
		negative=$(( $negative + 1))
	else
		positive=$(( $positive + 1))
	fi
done

echo "positive:$positive negative: $negative"





