# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '../qt5_ui/page_entity_config.ui'
#
# Created: Tue Jul 18 11:35:58 2017
#      by: PyQt5 UI code generator 5.3.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_PageEntityConfig(object):
    def setupUi(self, PageEntityConfig):
        PageEntityConfig.setObjectName("PageEntityConfig")
        PageEntityConfig.resize(996, 760)
        self.gridLayout = QtWidgets.QGridLayout(PageEntityConfig)
        self.gridLayout.setObjectName("gridLayout")
        spacerItem = QtWidgets.QSpacerItem(20, 77, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 0, 3, 1, 1)
        self.label_name = QtWidgets.QLabel(PageEntityConfig)
        self.label_name.setObjectName("label_name")
        self.gridLayout.addWidget(self.label_name, 1, 1, 1, 1)
        self.line = QtWidgets.QFrame(PageEntityConfig)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 2, 1, 1, 5)
        self.label_inputs = QtWidgets.QLabel(PageEntityConfig)
        self.label_inputs.setObjectName("label_inputs")
        self.gridLayout.addWidget(self.label_inputs, 3, 1, 1, 1)
        self.label_outputs = QtWidgets.QLabel(PageEntityConfig)
        self.label_outputs.setObjectName("label_outputs")
        self.gridLayout.addWidget(self.label_outputs, 3, 4, 1, 1)
        self.list_inputs = QtWidgets.QListWidget(PageEntityConfig)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.list_inputs.sizePolicy().hasHeightForWidth())
        self.list_inputs.setSizePolicy(sizePolicy)
        self.list_inputs.setMinimumSize(QtCore.QSize(300, 0))
        self.list_inputs.setObjectName("list_inputs")
        self.gridLayout.addWidget(self.list_inputs, 4, 1, 3, 1)
        self.button_inputs_plus = QtWidgets.QPushButton(PageEntityConfig)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_inputs_plus.sizePolicy().hasHeightForWidth())
        self.button_inputs_plus.setSizePolicy(sizePolicy)
        self.button_inputs_plus.setMinimumSize(QtCore.QSize(30, 30))
        self.button_inputs_plus.setMaximumSize(QtCore.QSize(30, 30))
        self.button_inputs_plus.setObjectName("button_inputs_plus")
        self.gridLayout.addWidget(self.button_inputs_plus, 4, 2, 1, 1)
        self.list_outputs = QtWidgets.QListWidget(PageEntityConfig)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.list_outputs.sizePolicy().hasHeightForWidth())
        self.list_outputs.setSizePolicy(sizePolicy)
        self.list_outputs.setMinimumSize(QtCore.QSize(300, 0))
        self.list_outputs.setObjectName("list_outputs")
        self.gridLayout.addWidget(self.list_outputs, 4, 4, 3, 1)
        self.button_outputs_plus = QtWidgets.QPushButton(PageEntityConfig)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_outputs_plus.sizePolicy().hasHeightForWidth())
        self.button_outputs_plus.setSizePolicy(sizePolicy)
        self.button_outputs_plus.setMinimumSize(QtCore.QSize(30, 30))
        self.button_outputs_plus.setMaximumSize(QtCore.QSize(30, 30))
        self.button_outputs_plus.setObjectName("button_outputs_plus")
        self.gridLayout.addWidget(self.button_outputs_plus, 4, 5, 1, 1)
        self.button_inputs_minus = QtWidgets.QPushButton(PageEntityConfig)
        self.button_inputs_minus.setMinimumSize(QtCore.QSize(30, 30))
        self.button_inputs_minus.setMaximumSize(QtCore.QSize(30, 30))
        self.button_inputs_minus.setObjectName("button_inputs_minus")
        self.gridLayout.addWidget(self.button_inputs_minus, 5, 2, 1, 1)
        self.button_outputs_minus = QtWidgets.QPushButton(PageEntityConfig)
        self.button_outputs_minus.setMinimumSize(QtCore.QSize(30, 30))
        self.button_outputs_minus.setMaximumSize(QtCore.QSize(30, 30))
        self.button_outputs_minus.setObjectName("button_outputs_minus")
        self.gridLayout.addWidget(self.button_outputs_minus, 5, 5, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(26, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 6, 0, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(26, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 6, 6, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(20, 76, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem3, 7, 3, 1, 1)

        self.retranslateUi(PageEntityConfig)
        QtCore.QMetaObject.connectSlotsByName(PageEntityConfig)

    def retranslateUi(self, PageEntityConfig):
        _translate = QtCore.QCoreApplication.translate
        PageEntityConfig.setWindowTitle(_translate("PageEntityConfig", "WizardPage"))
        self.label_name.setText(_translate("PageEntityConfig", "Signal configuration for entity "))
        self.label_inputs.setText(_translate("PageEntityConfig", "Inputs"))
        self.label_outputs.setText(_translate("PageEntityConfig", "Outputs"))
        self.button_inputs_plus.setText(_translate("PageEntityConfig", "+"))
        self.button_outputs_plus.setText(_translate("PageEntityConfig", "+"))
        self.button_inputs_minus.setText(_translate("PageEntityConfig", "-"))
        self.button_outputs_minus.setText(_translate("PageEntityConfig", "-"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    PageEntityConfig = QtWidgets.QWizardPage()
    ui = Ui_PageEntityConfig()
    ui.setupUi(PageEntityConfig)
    PageEntityConfig.show()
    sys.exit(app.exec_())

