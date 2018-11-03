This repository contains the tasks developed by the TU Wien for autosub (https://github.com/autosub_team/autosub).

Each task has its own directory.

The folder "_backend_interfaces" is for scripts, that can be passed to testers (definition of
functionions that allow a tester to control a backend interface)

A task consists of multiple elements. The folders and common files are:

tmp/ --Folder to temporarily store generated files

static/ --files that are static for the task

templates/ --files from which files for each individual task are generated
--> task_description_template.tex --LaTeX template for the task description pdf
--> test_bench_template.vhdl --VHDL template file for testbench generation

scripts/
--> generateTask.py --Generates the random task, fills entity and task_description templates
--> generateTestbench.py --Generates a testbench for gien TaskParameters

exam/ --files for the exam mode

generator.sh --> executable that gets called from the generator thread

tester.sh --> executable that gets called from the worker thread
              tester.sh without prefix should be compatible to using the CommonFile API
			  other testers should have a prefix

description.txt -->message that will be sent as email text in the task description email
