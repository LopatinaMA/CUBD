# Form implementation generated from reading ui file 'Dialog_comboBox.ui'
#
# Created by: PyQt6 UI code generator 6.8.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1060, 485)
        Dialog.setStyleSheet("")
        self.label = QtWidgets.QLabel(parent=Dialog)
        self.label.setGeometry(QtCore.QRect(30, 10, 600, 40))
        self.label.setStyleSheet("font: 16pt \"Segoe UI\";\n"
"")
        self.label.setObjectName("label")
        self.confirm_button = QtWidgets.QPushButton(parent=Dialog)
        self.confirm_button.setGeometry(QtCore.QRect(750, 10, 130, 40))
        self.confirm_button.setStyleSheet("font: 12pt \"Segoe UI\";\n"
"background-color: rgb(255, 255, 255);\n"
"border-style: solid;\n"
"border-width: 1px;\n"
"border-color: rgb(220, 220, 220);\n"
"border-radius: 8px;")
        self.confirm_button.setObjectName("confirm_button")
        self.cancel_button = QtWidgets.QPushButton(parent=Dialog)
        self.cancel_button.setGeometry(QtCore.QRect(900, 10, 130, 40))
        self.cancel_button.setStyleSheet("font: 12pt \"Segoe UI\";\n"
"background-color: rgb(255, 255, 255);\n"
"border-style: solid;\n"
"border-width: 1px;\n"
"border-color: rgb(220, 220, 220);\n"
"border-radius: 8px;\n"
"")
        self.cancel_button.setObjectName("cancel_button")
        self.choose_comboBox = QtWidgets.QComboBox(parent=Dialog)
        self.choose_comboBox.setGeometry(QtCore.QRect(290, 10, 370, 40))
        self.choose_comboBox.setStyleSheet("font: 12pt \"Segoe UI\";\n"
"background-color: rgb(255, 255, 255);\n"
"")
        self.choose_comboBox.setObjectName("choose_comboBox")
        self.init_table = QtWidgets.QTableView(parent=Dialog)
        self.init_table.setGeometry(QtCore.QRect(30, 64, 1000, 411))
        self.init_table.setStyleSheet("")
        self.init_table.setObjectName("init_table")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "Выберете имя группы:"))
        self.confirm_button.setText(_translate("Dialog", "Открыть"))
        self.cancel_button.setText(_translate("Dialog", "Отмена"))
