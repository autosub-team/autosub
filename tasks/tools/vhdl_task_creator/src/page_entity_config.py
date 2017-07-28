#!/usr/bin/env python3
from PyQt5 import QtCore, QtGui, QtWidgets

from python_ui.ui_page_entity_config import Ui_PageEntityConfig

from dialog_signal_config import DialogSignalConfig

class PageEntityConfig(QtWidgets.QWizardPage):

    def __init__(self, entity_name, entity_config):
        super().__init__()

        self.entity_config = entity_config
        self.next_id = 0

        self.ui = Ui_PageEntityConfig()
        self.ui.setupUi(self)
        self.ui.label_name.setText("Configuration for entity " + entity_name)

        # signal & slots
        self.ui.button_inputs_plus.clicked.connect(self.button_inputs_plus_clicked)
        self.ui.button_inputs_minus.clicked.connect(self.button_inputs_minus_clicked)
        self.ui.button_outputs_plus.clicked.connect(self.button_outputs_plus_clicked)
        self.ui.button_outputs_minus.clicked.connect(self.button_outputs_minus_clicked)

        self.ui.list_inputs.doubleClicked.connect(self.input_clicked)
        self.ui.list_outputs.doubleClicked.connect(self.output_clicked)

    def nextId(self):
        return self.next_id

    def button_inputs_plus_clicked(self):
        dialog = DialogSignalConfig(self)

        if(dialog.exec() == QtWidgets.QDialog.Accepted):
            infos = dialog.get_infos()
            self.entity_config.inputs.append(infos)
            item = QtWidgets.QListWidgetItem(infos["definition"])
            self.ui.list_inputs.addItem(item)

    def button_inputs_minus_clicked(self):
        for item in self.ui.list_inputs.selectedItems():
            row = self.ui.list_inputs.row(item)
            self.ui.list_inputs.takeItem(self.ui.list_inputs.row(item))
            del self.entity_config.inputs[row]

    def button_outputs_plus_clicked(self):
        dialog = DialogSignalConfig(self)

        if(dialog.exec() == QtWidgets.QDialog.Accepted):
            infos = dialog.get_infos()
            self.entity_config.outputs.append(infos)
            item = QtWidgets.QListWidgetItem(infos["definition"])
            self.ui.list_outputs.addItem(item)

    def button_outputs_minus_clicked(self):
        for item in self.ui.list_outputs.selectedItems():
            row = self.ui.list_outputs.row(item)
            self.ui.list_outputs.takeItem(self.ui.list_outputs.row(item))
            del self.entity_config.outputs[row]

    def input_clicked(self, pos):
        index = pos.row()
        infos = self.entity_config.inputs[index]
        dialog = DialogSignalConfig(self, infos)

        if(dialog.exec() == QtWidgets.QDialog.Accepted):
            infos = dialog.get_infos()
            self.entity_config.inputs[index] = infos
            item = self.ui.list_inputs.item(index)
            item.setText(infos["definition"])

    def output_clicked(self, pos):
        index = pos.row()
        infos = self.entity_config.outputs[index]
        dialog = DialogSignalConfig(self, infos)

        if(dialog.exec() == QtWidgets.QDialog.Accepted):
            infos = dialog.get_infos()
            self.entity_config.outputs[index] = infos
            item = self.ui.list_outputs.item(index)
            item.setText(infos["definition"])

