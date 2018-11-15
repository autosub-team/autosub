# Makefile for LaTeX documents

# TEXFILES = $(wildcard *.tex)

#TEXFILES contains usually only the header file
#The pdf file will be called header_docu.pdf, so you better give
#a suitable name for your header file
TEXFILES = usermanual.tex
PROJECTNAME = usermanual

DEPS = usermanual.tex sections/appendix.tex sections/system_interaction.tex \
       sections/tasks_system.tex sections/autosub_system.tex \
       sections/system_prerequisites.tex sections/webinterface.tex \
       sections/overview.tex sections/system_setup.tex \
       sections/create_new_task.tex sections/backends.tex


DIRS=. sections images

include latex/Makefile

