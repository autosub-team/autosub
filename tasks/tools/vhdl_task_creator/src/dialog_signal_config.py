#!/usr/bin/env python3

from PyQt5 import QtCore, QtGui, QtWidgets
from python_ui.ui_dialog_signal_config import Ui_DialogSignalConfig

class DialogSignalConfig(QtWidgets.QDialog):

    def __init__(self, parent, values = {}):
        super().__init__(parent)

        # set up the ui
        self.ui = Ui_DialogSignalConfig()
        self.ui.setupUi(self)

        #Signal & Slots connections
        self.ui.signal_type.currentTextChanged.connect(self.on_signal_type_change)
        self.ui.option_fixed_length.toggled.connect(self.option_fixed_length_changed)
        self.ui.option_variable_length.toggled.connect(self.option_variable_length_changed)
        self.ui.option_single.toggled.connect(self.option_single_changed)
        self.ui.length_placeholder.textChanged.connect(self.create_resulting_definition)
        self.ui.signal_name.textChanged.connect(self.create_resulting_definition)
        self.ui.custom_signal_type.textChanged.connect(self.create_resulting_definition)

        if not values:
            return

        # set fields to given values (if given)
        if 'signal_name' in values:
            self.ui.signal_name.setText(values['signal_name'])

        if 'signal_type' in values:
            self.ui.signal_type.setCurrentText(values['signal_type'])

            if values['signal_type'] == 'custom':
                self.ui.custom_signal_type.setEnabled(True)

            elif values['signal_type'] == 'std_logic':
                self.ui.option_fixed_length.setEnabled(False)
                self.ui.option_variable_length.setEnabled(False)
                self.ui.option_single.setEnabled(False)
            else:
                self.ui.option_fixed_length.setEnabled(True)
                self.ui.option_variable_length.setEnabled(True)
                self.ui.custom_signal_type.setEnabled(False)
                self.ui.option_single.setEnabled(False)

            if 'custom_signal_type' in values:
                self.ui.custom_signal_type.setText(values['custom_signal_type'])

        if 'length_type' in values:
            self.ui.length_type = values ['length_type']

            if values['length_type'] == 'fixed':
                self.ui.option_fixed_length.setChecked(True)
                self.ui.length_placeholder.setEnabled(True)
                self.ui.label_length_placeholder.setText('Length')
            elif values['length_type'] == 'variable':
                self.ui.option_variable_length.setChecked(True)
                self.ui.length_placeholder.setEnabled(True)
                self.ui.label_length_placeholder.setText('Length Placeholder')
                self.ui.label_infolabel.setText("Use {{ ... }} as  delimiters")

            elif values['length_type'] == 'single':
                self.ui.option_single.setChecked(True)
                self.ui.length_placeholder.setEnabled(False)

            if 'length_placeholder' in values:
                self.ui.length_placeholder.setText(values['length_placeholder'])

        self.create_resulting_definition()

    def done(self, status):
        if(status == QtWidgets.QDialog.Accepted):
            # check if the input makes sense
            if not self.ui.signal_name.text():
                return

            if self.ui.option_variable_length.isChecked():
               text = self.ui.length_placeholder.text()
               if not text:
                   return

            if self.ui.option_fixed_length.isChecked():
               text = self.ui.length_placeholder.text()
               if not text.isdigit():
                   return

            if self.ui.signal_type.currentText() == "custom":
                text = self.ui.custom_signal_type.text()
                if not text:
                    return

            # all passed
            super().done(status)
            return

        else:
            super().done(status)
            return

    def option_variable_length_changed(self, new_state):
        if new_state : #checked
            self.ui.label_length_placeholder.setText('Length Placeholder')
            self.ui.length_placeholder.setEnabled(True)
            self.ui.length_placeholder.setText("")
            self.ui.label_infolabel.setText("Use {{ ... }} as  delimiters")
            self.create_resulting_definition()

    def option_fixed_length_changed(self, new_state):
        if new_state: #checked
            self.ui.label_length_placeholder.setText('Length')
            self.ui.length_placeholder.setEnabled(True)
            self.ui.length_placeholder.setText("")
            self.ui.label_infolabel.setText("")
            self.create_resulting_definition()

    def option_single_changed(self, new_state):
        if new_state: #checked
            self.ui.length_placeholder.setEnabled(False)
            self.ui.length_placeholder.setText("")
            self.ui.label_infolabel.setText("")
            self.create_resulting_definition()

    def on_signal_type_change(self, new_signal_type):
        if new_signal_type == 'std_logic':
            self.ui.option_fixed_length.setEnabled(False)
            self.ui.option_variable_length.setEnabled(False)
            self.ui.length_placeholder.setEnabled(False)
            self.ui.custom_signal_type.setEnabled(False)
            self.ui.length_placeholder.setText("")
            self.ui.option_variable_length.setEnabled(False)
            self.ui.option_fixed_length.setEnabled(False)
            self.ui.option_single.setEnabled(False)
            self.ui.custom_signal_type.setText("")
            self.ui.option_single.setChecked(True)

        elif new_signal_type == 'custom':
            self.ui.option_fixed_length.setEnabled(True)
            self.ui.option_variable_length.setEnabled(True)
            self.ui.length_placeholder.setEnabled(True)
            self.ui.custom_signal_type.setEnabled(True)
            self.ui.option_single.setEnabled(True)
        else:
            self.ui.option_fixed_length.setEnabled(True)
            self.ui.option_variable_length.setEnabled(True)
            self.ui.length_placeholder.setEnabled(True)
            self.ui.custom_signal_type.setEnabled(False)
            self.ui.option_single.setEnabled(False)
            self.ui.custom_signal_type.setText("")

            if self.ui.option_single.isChecked():
                self.ui.option_fixed_length.setChecked(True)
                self.ui.option_single.setChecked(False)

        self.create_resulting_definition()


    def create_resulting_definition(self):
        result = self.ui.signal_name.text() + ' : '

        if self.ui.signal_type.currentText() == 'custom':
            result += self.ui.custom_signal_type.text()

            if not self.ui.option_single.isChecked():
                result += "(" + self.ui.length_placeholder.text() +"-1 downto 0)"

        elif self.ui.signal_type.currentText() == 'std_logic':
            result += self.ui.signal_type.currentText()
        else:
            result += self.ui.signal_type.currentText()
            result += "(" + self.ui.length_placeholder.text() +"-1 downto 0)"

        self.ui.resulting_definition.setText(result)
        return result

    def get_infos(self):
        signal_infos = {'signal_name'        : self.ui.signal_name.text(), \
                        'signal_type'        : self.ui.signal_type.currentText(), \
                        'length_placeholder' : self.ui.length_placeholder.text(), \
                        'custom_signal_type' : self.ui.custom_signal_type.text(), \
                        'definition'         : self.create_resulting_definition()}

        if self.ui.option_single.isChecked():
            signal_infos['length_type'] = "single"
        elif self.ui.option_fixed_length.isChecked():
            signal_infos['length_type'] = "fixed"
        elif self.ui.option_variable_length.isChecked():
            signal_infos['length_type'] = "variable"

        return signal_infos
