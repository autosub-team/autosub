# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '../qt5_ui/page_summary.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_PageSummary(object):
    def setupUi(self, PageSummary):
        PageSummary.setObjectName("PageSummary")
        PageSummary.resize(838, 553)
        self.gridLayout = QtWidgets.QGridLayout(PageSummary)
        self.gridLayout.setObjectName("gridLayout")
        spacerItem = QtWidgets.QSpacerItem(20, 38, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 0, 2, 1, 1)
        self.label_summary = QtWidgets.QLabel(PageSummary)
        self.label_summary.setObjectName("label_summary")
        self.gridLayout.addWidget(self.label_summary, 1, 1, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(0, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 2, 0, 2, 1)
        self.line = QtWidgets.QFrame(PageSummary)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 2, 1, 1, 2)
        self.summary = QtWidgets.QTextEdit(PageSummary)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.summary.sizePolicy().hasHeightForWidth())
        self.summary.setSizePolicy(sizePolicy)
        self.summary.setMinimumSize(QtCore.QSize(500, 300))
        self.summary.setReadOnly(True)
        self.summary.setObjectName("summary")
        self.gridLayout.addWidget(self.summary, 3, 1, 1, 2)
        spacerItem2 = QtWidgets.QSpacerItem(1, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 3, 3, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem3, 4, 2, 1, 1)

        self.retranslateUi(PageSummary)
        QtCore.QMetaObject.connectSlotsByName(PageSummary)

    def retranslateUi(self, PageSummary):
        _translate = QtCore.QCoreApplication.translate
        PageSummary.setWindowTitle(_translate("PageSummary", "Summary"))
        self.label_summary.setText(_translate("PageSummary", "Summary for task"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    PageSummary = QtWidgets.QWizardPage()
    ui = Ui_PageSummary()
    ui.setupUi(PageSummary)
    PageSummary.show()
    sys.exit(app.exec_())

