from PyQt5 import QtCore, QtGui, QtWidgets


class detect_select(QtWidgets.QDialog):
    signal_detect_method = QtCore.pyqtSignal(tuple)

    def __init__(self, parent=None):
        super(detect_select, self).__init__(parent)
        self.selected_method = "use_lowerbound"
        self.setupUi()

    def setupUi(self):
        self.setObjectName("select_method")
        self.resize(420, 200)
        self.setFixedSize(420, 200)
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint, True)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        self.use_lowerbound = QtWidgets.QRadioButton(self)
        self.use_lowerbound.setMaximumSize(QtCore.QSize(512, 16))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.use_lowerbound.setFont(font)
        self.use_lowerbound.setObjectName("use_lowerbound")
        self.verticalLayout.addWidget(self.use_lowerbound)
        self.use_cleanlab = QtWidgets.QRadioButton(self)
        self.use_cleanlab.setMaximumSize(QtCore.QSize(512, 16))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.use_cleanlab.setFont(font)
        self.use_cleanlab.setObjectName("use_cleanlab")
        self.verticalLayout.addWidget(self.use_cleanlab)
        self.use_both = QtWidgets.QRadioButton(self)
        self.use_both.setMaximumSize(QtCore.QSize(512, 16))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.use_both.setFont(font)
        self.use_both.setObjectName("use_both")
        self.verticalLayout.addWidget(self.use_both)
        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setMaximumSize(QtCore.QSize(512, 32))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")

        self.radio_group = QtWidgets.QButtonGroup(self)
        self.radio_group.addButton(self.use_lowerbound)
        self.radio_group.addButton(self.use_cleanlab)
        self.radio_group.addButton(self.use_both)
        self.use_lowerbound.setChecked(True)
        self.radio_group.buttonToggled.connect(self.on_button_toggled)

        self.lineEdit = QtWidgets.QLineEdit(self)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.lineEdit.setFont(font)
        self.lineEdit.setObjectName("Threshold")
        self.verticalLayout.addWidget(self.lineEdit)

        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setMaximumSize(QtCore.QSize(512, 32))
        self.buttonBox.setFont(font)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi()
        self.buttonBox.accepted.connect(self.accept)  # type: ignore
        self.buttonBox.rejected.connect(self.reject)  # type: ignore
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("select_method", "选择检测方法"))
        self.use_lowerbound.setText(_translate("select_method", "阈值法"))
        self.use_cleanlab.setText(_translate("select_method", "置信学习"))
        self.use_both.setText(_translate("select_method", "以上两种"))
        self.lineEdit.setPlaceholderText(_translate("select_method", "使用的置信度阈值（0~1之间浮点数）"))

    def on_button_toggled(self, btn, checked):
        if checked:
            print('Selected button ID:', btn.objectName())
            self.selected_method = btn.objectName()
            if self.selected_method == 'use_both' or self.selected_method == 'use_lowerbound':
                self.lineEdit.setEnabled(True)
            else:
                self.lineEdit.setEnabled(False)

    def accept(self):
        threshold = 0.2
        if self.selected_method == "use_both" or self.selected_method == 'use_lowerbound':
            threshold = self.lineEdit.text()
            try:
                threshold = float(threshold)
                if threshold >= 1.0 or threshold <= 0.0:
                    QtWidgets.QMessageBox.warning(self, "OOps!", "阈值应该在0到1之间")
                else:
                    self.close()
                    self.signal_detect_method.emit((self.selected_method, threshold))

            except ValueError:
                QtWidgets.QMessageBox.warning(self, "OOps!", "非法输入")
        else:
            self.close()
            self.signal_detect_method.emit((self.selected_method, threshold))
