#!/bin/bash

# this script fetches the tasks from defined repos
# by default no files are deleted when updating
# to force a full refetch use:
# ./update_tasks.sh refetch

# this array can be extended to include your own task repo
# ("repo1" "repo2")
task_repos_VHDL=("https://github.com/autosub-team/VHDL_Tasks")

if [ ! -z $1 ]
then
    if [ $1 = "refetch" ]
    then
    	echo "Deleting all content first to do total refetch"
    	echo "----------------------------------------------"
    	cd tasks/implementation/VHDL
		#delete all ignoring the README.txt
		GLOBIGNORE="README.txt"
		rm -rf *
		unset GLOBIGNORE
    	cd - > /dev/null
		echo -e "Done\n"
    fi
fi

echo -e "Updating all tasks\n------------------\n"

for task_repo in ${task_repos_VHDL[@]}; do
    git clone $task_repo temp
	rm -rf temp/.git
	rm -f temp/.gitignore
	rsync -avh temp/ tasks/implementation/VHDL/
	rm -rf temp
	echo -e "\n============================\n"
done
