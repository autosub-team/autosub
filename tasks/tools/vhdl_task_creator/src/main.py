#!/usr/bin/env python3
from PyQt5 import QtCore, QtGui, QtWidgets

import sys

from page_summary import PageSummary
from page_task_overall import PageTaskOverall
from dialog_signal_config import DialogSignalConfig
from page_entity_config import PageEntityConfig

class VhdlTaskCreator:
    def init(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.wizard = QtWidgets.QWizard()

        self.entity_configs = {}
        self.extra_files = []

        self.page_task_overall = PageTaskOverall(self.wizard, self)
        self.wizard.addPage(self.page_task_overall)

        self.page_summary = PageSummary(self.wizard, self)
        page_id = self.wizard.addPage(self.page_summary)
        self.page_summary.page_id = page_id

        self.wizard.setWindowTitle("VHDL Task Creator Wizard")

        self.wizard.show()

    def execute(self):
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    program = VhdlTaskCreator()
    program.init()
    program.execute()
