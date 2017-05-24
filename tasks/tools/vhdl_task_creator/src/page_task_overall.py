#!/usr/bin/env python3
import os

from PyQt5 import QtCore, QtGui, QtWidgets
from python_ui.ui_page_task_overall import Ui_PageTaskOverall
from entity_config import EntityConfig

class PageTaskOverall(QtWidgets.QWizardPage):

    def __init__(self, wizard, base_object):
        super().__init__(wizard)

        self.next_id = 0
        self.wizard = wizard
        self.base_object = base_object
        self.entity_configs = base_object.entity_configs

        self.ui = Ui_PageTaskOverall()
        self.ui.setupUi(self)

        # register fields, set mandatories
        self.registerField("task_name*", self.ui.task_name)
        self.registerField("directory*", self.ui.directory)
        self.registerField("user_entities*", self.ui.list_user_entities)
        self.registerField("checkbox_constraint_script", self.ui.checkbox_constraint_script)
        self.registerField("checkbox_attach_wavefile", self.ui.checkbox_attach_wavefile)
        self.registerField("timeout", self.ui.timeout)

        # signals and slots
        self.ui.button_directory.clicked.connect(self.button_directory_clicked)
        self.ui.button_user_entities_plus.clicked.connect(self.button_user_entities_plus_clicked)
        self.ui.button_user_entities_minus.clicked.connect(self.button_user_entities_minus_clicked)
        self.ui.button_extra_files_plus.clicked.connect(self.button_extra_files_plus_clicked)
        self.ui.button_extra_files_minus.clicked.connect(self.button_extra_files_minus_clicked)

    def nextId(self):
        return self.next_id

    def validatePage(self):
        # save extra_files
        self.base_object.extra_files = []
        for i in range(0, self.ui.list_extra_files.count()):
            self.base_object.extra_files.append(self.ui.list_extra_files.item(i).text())

        QtCore.qDebug(str(self.base_object.extra_files))

        # get the in the gui specified entity names
        entity_names = []
        for i in range(0, self.ui.list_user_entities.count()):
            entity_names.append(self.ui.list_user_entities.item(i).text())

        # delete now unneeded entity_configs
        to_delete = []

        for key, value in self.entity_configs.items():
            if key not in entity_names:
                self.wizard.removePage(value.page_id)
                to_delete.append(key)

        for key in to_delete:
            self.entity_configs.remove(key)

        # add new for new entity
        for entity_name in entity_names:
            if entity_name not in self.base_object.entity_configs:
                entity_config = EntityConfig(entity_name)
                self.entity_configs[entity_name] = entity_config
                page_id = self.wizard.addPage(entity_config.page)
                entity_config.page_id = page_id

        # fix the order #
        keys = list(self.entity_configs.keys())
        num_entities = len(self.entity_configs)

        # self to first
        self.next_id = self.entity_configs[keys[0]].page_id

        # entity_config to next entity_config
        for i in range(0,num_entities-1):
            self.entity_configs[keys[i]].page.next_id = self.entity_configs[keys[i+1]].page_id

        #last to summary
        self.entity_configs[keys[-1]].page.next_id = self.base_object.page_summary.page_id

        return True

    def button_directory_clicked(self):
        if os.path.isdir(self.ui.directory.text()):
            dirname = QtWidgets.QFileDialog.getExistingDirectory(self, \
                          "Choose a location", self.ui.directory.text())
        else:
            dirname = QtWidgets.QFileDialog.getExistingDirectory(self,"Choose a location")

        if dirname:
            self.ui.directory.setText(dirname)

    def button_user_entities_plus_clicked(self):
        item = QtWidgets.QListWidgetItem("ChangeMeByDoubleClick")
        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
        self.ui.list_user_entities.addItem(item)

    def button_user_entities_minus_clicked(self):
        for item in self.ui.list_user_entities.selectedItems():
            self.ui.list_user_entities.takeItem(self.ui.list_user_entities.row(item))

    def button_extra_files_plus_clicked(self):
        item = QtWidgets.QListWidgetItem("ChangeMeByDoubleClick")
        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
        self.ui.list_extra_files.addItem(item)

    def button_extra_files_minus_clicked(self):
        for item in self.ui.list_extra_files.selectedItems():
            self.ui.list_extra_files.takeItem(self.ui.list_extra_files.row(item))

