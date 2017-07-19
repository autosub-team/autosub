#!/usr/bin/env python3

from PyQt5 import QtCore, QtGui, QtWidgets

from python_ui.ui_page_summary import Ui_PageSummary

from jinja2 import FileSystemLoader, Environment

import os
from shutil import copyfile

class PageSummary(QtWidgets.QWizardPage):
    def __init__(self, wizard, base_object):
        super().__init__(wizard)

        self.page_id = None
        self.base_object = base_object
        self.entity_configs = base_object.entity_configs

        self.ui = Ui_PageSummary()
        self.ui.setupUi(self)

        # set up templates environment
        self.env = Environment()
        self.env.loader = FileSystemLoader('templates/')

        self.directory = ""

    def nextId(self):
        # explicitely as last page
        return -1

    def initializePage(self):
        self.directory = os.path.join(self.field("directory"), self.field("task_name"))

        text = '<h2>Task "' + self.field("task_name") + '"</h2>' + \
               '<b>Output directory:</b> <br> ' + self.directory + '<br>'

        text += '<br>'

        text += '<b>Extra files:</b><br>'
        for filename in self.base_object.extra_files:
            text += filename + '<br>'

        for key, entity_config in self.entity_configs.items():
            text += '<h3>Entity "' + entity_config.entity_name + '"</h3>'

            text += '<u>Inputs:</u> <br>'
            for inp in entity_config.inputs:
                text += inp['definition'] + '<br>'

            text += '<br>'

            text += '<u>Outputs:</u> <br>'
            for outp in entity_config.outputs:
                text += outp['definition'] + '<br>'

        self.ui.summary.setText(text)

    # called when Finish pressed
    def validatePage(self):
        os.makedirs(self.directory)

        os.makedirs(os.path.join(self.directory, "scripts"), exist_ok=True)
        os.makedirs(os.path.join(self.directory, "templates"), exist_ok=True)
        os.makedirs(os.path.join(self.directory, "static"), exist_ok=True)

        # copy the description.txt file to task folder
        copyfile("templates/description.txt", os.path.join(self.directory, "description.txt"))


        self.create_task_cfg()
        self.create_placeholder_files()
        self.create_entities()
        self.create_description_template()

        return True

    def signal_typedef(self, signal_info):
        result = ""

        if signal_info["signal_type"] == "custom":
            result += signal_info["custom_signal_type"]
        else:
            result += signal_info["signal_type"]

        if signal_info["length_type"] != "single":
            result += "(" + signal_info["length_placeholder"] + "-1 downto 0)"

        return result

    def create_description_template(self):
        task_name = self.field("task_name")

        # add latex escape character to underscores
        task_name = task_name.replace("_", "\_")

        ################################
        # task_description, _beh files #
        ################################
        entities = []

        for key, entity_config in self.entity_configs.items():
            entity = {}
            entity['name'] = entity_config.entity_name.replace("_", "\_")

            # calculate the minimum height for the tikzpicture (in mm):
            minimum_height = 6 * (1 + max(len(entity_config.inputs), len(entity_config.outputs)))

            entity['minimum_height'] = minimum_height

            entity['inputs'] = []
            for inp in entity_config.inputs:
                signal = {}
                signal['name'] = inp['signal_name'].replace("_", "\_")
                signal['type'] = inp['signal_type'].replace("_", "\_")

                if inp['length_type'] != 'single':
                    signal['type'] += " of length " + inp['length_placeholder']
                entity['inputs'].append(signal)

            entity['outputs'] = []
            for outp in entity_config.outputs:
                signal = {}
                signal['name'] = outp['signal_name'].replace("_", "\_")
                signal['type'] = outp['signal_type'].replace("_", "\_")

                if outp['length_type'] != 'single':
                    signal['type'] += " of length " + outp['length_placeholder']
                entity['outputs'].append(signal)

            entities.append(entity)

        for entity in entities:
            template = self.env.get_template('entity_beh_template.vhdl')
            data = {'entity_name' : entity['name']}
            template = template.render(data)
            path = os.path.join(self.directory, "static", entity['name'] + "_beh.vhdl")

            with open(path, "w") as fileh:
                fileh.write(template)

        # aggregate the values to be rendered in the description template
        data = {'task_name': task_name,
                'entities' : entities}

        self.env.trim_blocks = True
        self.env.lstrip_blocks = True

        template = self.env.get_template('task_description_template.tex')
        template = template.render(data)

        path = os.path.join(self.directory, "templates", "task_description_template.tex")

        with open(path, "w") as fileh:
            fileh.write(template)

    def create_entities(self):
        for key, entity_config in self.entity_configs.items():
            entity_name = entity_config.entity_name

            # find max string length of input/output width for indentation
            max_length_in = max(len(signal['signal_name']) for signal in entity_config.inputs)
            max_length_out= max(len(signal['signal_name']) for signal in entity_config.outputs)
            max_length_width = max(max_length_in, max_length_out)

            inputs = [{'name': signal['signal_name'].ljust(max_length_width), \
                       'type': self.signal_typedef(signal)} \
                      for signal in entity_config.inputs]

            outputs = [{'name': signal['signal_name'].ljust(max_length_width), \
                        'type': self.signal_typedef(signal)} \
                       for signal in entity_config.outputs]

            # do we need to put the entity file as template?
            needs_template = False

            for signal in entity_config.inputs:
                if signal['length_type'] == "variable":
                    needs_template  = True

            for signal in entity_config.outputs:
                if signal['length_type'] == "variable":
                    needs_template  = True

            if needs_template:
                path = os.path.join(self.directory, "templates", entity_name + "_template.vhdl")
            else:
                path = os.path.join(self.directory, "static", entity_name + ".vhdl")

            self.env.trim_blocks = True
            self.env.lstrip_blocks = True

            # load the template file
            template = self.env.get_template('entity_template.vhdl')

            # aggregate the values to be rendered in the template
            data = {'entity_name': entity_name,
                    'inputs' : inputs,
                    'outputs' : outputs}

            # render the template
            template = template.render(data)

            # save the rendered template
            with open(path, "w") as fileh:
                fileh.write(template)

    def create_placeholder_files(self):
        task_name = self.field("task_name")

        ###############
        ## testbench ##
        ###############
        template = self.env.get_template('testbench_template.vhdl')

        path = os.path.join(self.directory, "templates", "testbench_template.vhdl")

        data = {'task_name': task_name}
        template = template.render(data)
        with open(path, "w") as fileh:
            fileh.write(template)

        #####################
        # generateTestbench #
        #####################
        data = {'task_name': task_name}

        template = self.env.get_template('generateTestBench_template.py')
        template = template.render(data)

        path = os.path.join(self.directory, "scripts", "generateTestBench.py")

        with open(path, "w") as fileh:
            fileh.write(template)

        ################
        # generateTask #
        ################
        data = {'task_name': task_name}

        template = self.env.get_template('generateTask_template.py')
        template = template.render(data)

        path = os.path.join(self.directory, "scripts", "generateTask.py")

        with open(path, "w") as fileh:
            fileh.write(template)

        ######################
        # tester & generator #
        ######################
        copyfile("templates/generator.sh", os.path.join(self.directory, "generator.sh"))
        copyfile("templates/tester.sh", os.path.join(self.directory, "tester.sh"))

        if self.field("checkbox_constraint_script"):
            copyfile("templates/check.sh", os.path.join(self.directory, "scripts/check.sh"))


    def create_task_cfg(self):
        task_name = self.field("task_name")
        userfiles = " ".join([name + "_beh.vhdl" for name, config in self.entity_configs.items()])
        entityfiles = " ".join([name + ".vhdl" for name, config in self.entity_configs.items()])
        extrafiles = " ".join([name for name in self.base_object.extra_files])

        if self.field("checkbox_constraint_script"):
            constraintfile = "scripts/check.sh"
        else:
            constraintfile = ""

        if self.field("checkbox_attach_wavefile"):
            attach_wave_file = "1"
        else:
            attach_wave_file = "0"

        simulation_timeout = self.field("timeout")

        template = self.env.get_template('task_template.cfg')
        data = {'task_name': task_name,
                'userfiles':  userfiles,
                'entityfiles': entityfiles,
                'extrafiles': extrafiles,
                'constraintfile': constraintfile,
                'simulation_timeout': simulation_timeout,
                'attach_wave_file': attach_wave_file}

        path = os.path.join(self.directory, "task.cfg")

        # render the template
        template = template.render(data)

        # save the rendered template
        with open(path, "w") as fileh:
            fileh.write(template)
