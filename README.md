# What is autosub? #
Autosub is an email based system for generating, submitting and automatically
testing student assignments in courses.

It includes VELS (VHDL E-Learning System) for supporting VHDL
training courses. Students receive individual tasks and submit VHDL
models by email, which are in succession automatically simulated
and tested by testbenches on the server. Students receive email responses
about the success or failure of the test within seconds or minutes.
VELS comes with a set of VHDL assignments for VHDL beginners.

# How to get it #
To get autosub clone this repository

	git clone https://github.com/autosub-team/autosub.git

To fetch the existing VHDL tasks use the update_tasks.sh script in the root
folder. In order to fetch the task you need to have the program rsync installed!

# Documentation #

For documenation, please refer to our user manual
(https://github.com/autosub-team/autosub/blob/master/doc/doc_pdf/usermanual.pdf)
and the specification of the existing VHDL tasks
(https://github.com/autosub-team/autosub/blob/master/doc/doc_pdf/tasks-specification.pdf)

# How to Contribute #

If you want to contribute to the autosub development, have a look at CONTRIBUTE.md

# Concerning the C tasks #
The C example tasks given in this repository are not meant for usage, as they
impose a severe security threat if used unchanged -- it means you allow everyone
who submitts to the task to execute arbitraty code on YOUR machine. These are really
just for testing.
