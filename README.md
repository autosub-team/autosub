# What is autosub? #
Autosub is an email based system for generating, submitting and automatically
testing student assignments in courses.

VELS (VHDL E-Learning System) uses autosub for supporting VHDL
training courses. Students receive individual tasks and submit VHDL
models by email, which are in succession automatically simulated
and tested by testbenches on the server. Students receive email responses
about the success or failure of the test within seconds or minutes.
VELS comes with a set of VHDL assignments for VHDL beginners and offers a
web based configuration interface (VELS\_WEB).

# How to get it #
To get autosub clone this repository

	git clone https://github.com/autosub-team/autosub.git

To fetch the existing VHDL tasks use the 

	update_tasks.sh 

script in the root folder. In order to fetch the task you need to have the program rsync installed!

# Documentation #

For documenation, please refer to our [user manual](https://github.com/autosub-team/autosub/blob/master/doc/doc_pdf/usermanual.pdf)
and the [specification of the existing VHDL tasks](https://github.com/autosub-team/autosub/blob/master/doc/doc_pdf/tasks-specification.pdf)

# How to Contribute #

If you want to contribute to the autosub development, have a look at [CONTRIBUTE.md](CONTRIBUTE.md) and [doc/coding_standards/lifecycle.txt](doc/coding_standards/lifecycle.txt)

# Publication & Citation #
To cite VELS you can use the following bibtex entry:


    @INPROCEEDINGS{VELS,
    author={M. Mosbeck and D. Hauer and A. Jantsch},
    booktitle={2018 IEEE Nordic Circuits and Systems Conference (NORCAS): NORCHIP and International Symposium of System-on-Chip (SoC)},
    title={VELS: VHDL E-Learning System for Automatic Generation and Evaluation of Per-Student Randomized Assignments},
    year={2018},
    volume={},
    number={},
    pages={1-7},
    doi={10.1109/NORCHIP.2018.8573455},
    ISSN={},
    month={Oct},}


The full paper can be found at: https://ieeexplore.ieee.org/document/8573455

# Credits #

Autosub received funding as an VHDL E-Learning Platform(VELS) from the

  Institute of Computer Technology, University of Technology Vienna, Austria
https://www.ict.tuwien.ac.at/en

 Many Thanks!

--

Autosub received funding as an E-Learning Best Practice Project from the

  FH Campus Wien Teaching Support Center
https://www.fh-campuswien.ac.at/fh-campus-wien/kontakt-serviceeinrichtungen/teaching-support-center.html

Many Thanks!

--
