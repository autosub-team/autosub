######################################################################################
# Common file for all testers using ISIM from Xilinx ISE 14.7
#
# Copyright (C) 2017 Martin  Mosbeck   <martin.mosbeck@gmx.at>
#                    Gilbert Markum    < >
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
######################################################################################

######################################
#               SET UP               #
######################################

zero=0
one=1

#path to support files for common scripts
support_files_path=$common_path/support_files

#path to autosub
autosub_path=$(pwd)

# path for all the files that describe the created task
desc_path="$autosub_path/users/${user_id}/Task${task_nr}/desc"

#path where the testing takes place
user_task_path="$autosub_path/users/${user_id}/Task${task_nr}"

# name for the testbench
testbench=${task_name}_tb_${user_id}_Task${task_nr}.vhdl

# DEBUG OUTPUT
#echo "user_task_path= $user_task_path"
#echo "desc_path= $desc_path"
#echo "task_path= $task_path"
#echo "autosub_path= $autosub_path"
#echo "common_path= $common_path"
#echo "support_files_path=$support_files_path"
#echo "---------------------------------------"

######################################
#       FUNCTIONS FOR TESTING        #
######################################
function generate_testbench {
	cd $task_path
	#generate the testbench and move testbench to user's folder
	python3 scripts/generateTestBench.py "$task_params" > $user_task_path/$testbench

	#------ SAVE USED TESTBENCH  ------ #

	#  create directory for used testbenches if it does not exist
	if [ ! -d "$user_task_path/used_tbs" ]
	then
		mkdir $user_task_path/used_tbs
	fi

	#find last submission number
	submission_nrs=($(ls $user_task_path | grep -oP '(?<=Submission)[0-9]+' | sort -nr))
	submission_nr_last=${submission_nrs[0]}

	#copy used testbench
	src=$user_task_path/$testbench
	tgt=$user_task_path/used_tbs/${task_name}_tb_${user_id}_Task${task_nr}_Submission${submission_nr_last}.vhdl

	cp $src $tgt
}

function desccp {
	cp $desc_path/$1 $user_task_path
}

function prepare_test {
	cd $user_task_path

	# create tmp directory for user if it does not exist
	if [ ! -d "/tmp/$USER" ]
	then
   		mkdir /tmp/$USER
	fi

	# create file for error messages, which will be sent to user
	touch error_msg

	#make sure the error_attachments folder is empty
	if [ ! -d "error_attachments" ];
	then
	mkdir error_attachments
	else
	rm -r error_attachments
	mkdir error_attachments
	fi

	#------ CHECK AND PREPARE USERFILES ------
	for userfile in $userfiles
	do
		#check if the user supplied a file
		if [ ! -f $userfile ]
		then
			echo "Error with task ${task_nr}. User ${user_id} did not attach the right file."
			echo "You did not attach your solution. Please attach the file $userfile" > error_msg
			exit $FAILURE
		fi

		#delete all comments from the file
		sed -i 's:--.*$::g' $userfile
	done

	#------ COPY NEEDED FILES FOR TEST ------
	for filename in $entityfiles
	do
		desccp $filename
	done

	for filename in $extrafiles
	do
		desccp $filename
	done

	# copy the isim tcl file for testing to user's folder
	cp $support_files_path/isim.cmd $user_task_path

	# prepare ISE
	. /opt/Xilinx/14.7/ISE_DS/ISE/.settings64.sh /opt/Xilinx/14.7/ISE_DS/ISE
	unset LD_LIBRARY_PATH
}

function taskfiles_analyze {
	cd $user_task_path

	#------ ANALYZE FILES WHICH ARE NOT FROM THE USER ------#
	# Sequence: task entities - testbench - other needed files (packages etc.)

	for filename in $entityfiles
	do
		vhpcomp $filename
		RET=$?
		if [ "$RET" -ne "$zero" ]
		then
			echo "Error with task ${task_nr} for user ${user_id} while analyzing $filename"
			echo "Something went wrong with the task ${task_nr} test generation. This is not your " \
			     "fault. We are working on a solution" > error_msg
			exit $TASKERROR
		fi
	done

	vhpcomp $testbench
	RET=$?
	if [ "$RET" -ne "$zero" ]
	then
		echo "Error with task ${task_nr} for user ${user_id} while analyzing the testbench"
		echo "Something went wrong with the task ${task_nr} test generation. This is not your " \
		     "fault. We are working on a solution" > error_msg
		exit $TASKERROR
	fi

	for filename in $extrafiles
	do
		vhpcomp $filename
		RET=$?
		if [ "$RET" -ne "$zero" ]
		then
			echo "Error with task ${task_nr} for user ${user_id} while analyzing $filename"
			echo "Something went wrong with the task ${task_nr} test generation. This is not your " \
			     "fault. We are working on a solution" > error_msg
			exit $TASKERROR
		fi
	done
}

function userfiles_analyze {
	cd $user_task_path

	#------ ANALYZE FILES FROM THE USER ------#
	for filename in $userfiles
	do
		#this is the file from the user
		vhpcomp $filename 2> /tmp/$USER/tmp_Task${task_nr}_User${user_id}
		RET=$?

		# check for possible infinite loop warning message which crashes the simulation
		egrep -oq "Possible infinite loop" /tmp/$USER/tmp_Task${task_nr}_User${user_id}
		RET_loop=$?

		if [ "$RET_loop" -eq "$zero" ]
		then
		echo "Task ${task_nr} possible infinite loop for user ${user_id}!"
		echo "Your submitted behavior file seems to contain an infinite loop. Do all your processes have a sensitivity list?" > error_msg
		exit 1
		fi

		if [ "$RET" -eq "$zero" ]
		then
		   echo "Task ${task_nr} analyze success for user ${user_id}!"
		else
		   echo "Task ${task_nr} analyze FAILED for user ${user_id}!"
		   echo "Analyzation of your submitted behavior file failed:" > error_msg
		   cat /tmp/$USER/tmp_Task${task_nr}_User${user_id} | grep -v usenglish | grep WARNING >> error_msg # suppress warnings about non usenglish
		   cat /tmp/$USER/tmp_Task${task_nr}_User${user_id} | grep ERROR >> error_msg
		   exit $FAILURE
		fi
	done

}

function elaborate {
	cd $user_task_path

	#------ ELABORATE testbench ------#
	fuse -top ${task_name}_tb
	RET=$?

	if [ "$RET" -eq "$zero" ]
	then
		echo "Task${task_nr} elaboration success for user ${user_id}!"
	else
		echo "Task${task_nr} elaboration FAILED for user ${user_id}!"
		echo "Elaboration with your submitted behavior file failed:" > error_msg
		cat /tmp/$USER/tmp_Task${task_nr}_User${user_id} | grep -v usenglish | grep WARNING >> error_msg # suppress warnings about non usenglish
		cat fuse.log | grep WARNING >> error_msg
		cat fuse.log | grep -A 5 ERROR >> error_msg
		exit $FAILURE
	fi
}

function simulate {
	cd $user_task_path

	# set virtual memory limit to 500 MiB
	ulimit -v $((500*1024))

	# start simulation:
	timeout $simulation_timeout ./x.exe -tclbatch isim.cmd
	RET_timeout=$?

	# check if simulation timed out:
	if [ "$RET_timeout" -eq 124 ] # timeout exits 124 if it had to kill the process. Probably the simulation has crashed.
	then
		echo "Task${task_nr} simulation timeout for user ${user_id}!"
		echo "The simulation of your design timed out. This is not supposed to happen. Check your design." > error_msg
		exit $FAILURE
	fi

	# check if simulation reported "Success":
	egrep -q "Success" isim.log
	RET_success=$?
	if [ "$RET_success" -eq "$zero" ]
	then
		echo "Functionally correct for task${task_nr} for user ${user_id}!"
		exit $SUCCESS
	fi

	# attach wave file:
	if [ "$attach_wave_file" -eq "$one" ]
	then
		#compression factor is approx 10, so we dont want anything above 20MB
		head --bytes=20000K signals.vcd >signals_tmp.vcd; #first x K Bytes
		rm signals.vcd
		mv signals_tmp.vcd signals.vcd
		zip wavefile.zip signals.vcd
		mv wavefile.zip error_attachments/
		rm signals.vcd
	fi

	# check if simulation was stopped due to the "run X ms" restriction from the isim.cmd tcl script
	egrep -q "INFO: Simulator is stopped." isim.log # returns not 0 on exit due to the "run X ms" restriction
	RET_run_X_ms_restriction=$?
	if [ "$RET_run_X_ms_restriction" -ne "$zero" ]
	then
		echo "Wrong behavior for task ${task_nr} for user ${user_id}!"
		echo "Your submitted behavior file does not behave like specified in the task description:" > error_msg
		if [ "$attach_wave_file" -eq "$one" ]
		then
			echo "No continuous signal detected. Please look at the attached wave file to see what signal your entity produces." >> error_msg
		fi
		exit $FAILURE
	fi

	# check for simulation errors:
	cat isim.log | grep -v Security | egrep -q ERROR # security error messages are license errors
	RET_simulation_error=$?
	if [ "$RET_simulation_error" -eq "$zero" ]
	then
		echo "Simulation error for task ${task_nr} for user ${user_id}"
		echo "Your submitted behavior file does not behave like specified in the task description:" > error_msg
		cat /tmp/$USER/tmp_Task${task_nr}_User${user_id} | grep -v usenglish | grep WARNING >> error_msg # suppress warnings about non usenglish
		cat fuse.log | grep WARNING >> error_msg
		cat isim.log | grep -v Security | grep -A 5 ERROR >> error_msg
	exit $FAILURE
	fi

	# check for the error message from the testbench:
	egrep -q § isim.log
	RET_tb_error_message=$?
	if [ "$RET_tb_error_message" -eq "$zero" ]
	then
		echo "Wrong behavior for task ${task_nr} for user ${user_id}"
		echo "Your submitted behavior file does not behave like specified in the task description:" > error_msg
		cat /tmp/$USER/tmp_Task${task_nr}_User${user_id} | grep -v usenglish | grep WARNING >> error_msg # suppress warnings about non usenglish
		cat fuse.log | grep WARNING >> error_msg
		cat isim.log | awk '/§{/,/}§/' | sed 's/§{//g' | sed 's/}§//g' | sed 's/** Failure://g' | sed 's/\\n/\n/g' >> error_msg
		if [ "$attach_wave_file" -eq "$one" ]
		then
			echo "Please look at the attached wave file to see what signal(s) your entity produces. Use a viewer like GTKWave." >> error_msg
		fi
		exit $FAILURE
	fi

	# catch unhandled errors:
	echo "Unhandled error for task ${task_nr} for user ${user_id}!"
	echo "Your submitted behavior file does not behave like specified in the task description." > error_msg
	exit $FAILURE
}
