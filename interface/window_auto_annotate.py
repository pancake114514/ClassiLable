from PyQt5 import QtCore, QtGui, QtWidgets


class annotate_select(QtWidgets.QDialog):
    signal_annotate_method = QtCore.pyqtSignal(tuple)

    def __init__(self, parent=None):
        super(annotate_select, self).__init__(parent)
        self.selected_method = "hard"
        self.setupUi()

    def setupUi(self):
        self.setObjectName("select_label_method")
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint, True)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.resize(420, 200)
        self.setFixedSize(420,200)
        self.setMaximumSize(QtCore.QSize(600, 480))
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")

        self.use_hard = QtWidgets.QRadioButton(self)
        self.use_hard.setMaximumSize(QtCore.QSize(512, 16))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.use_hard.setFont(font)
        self.use_hard.setObjectName("hard")
        self.verticalLayout.addWidget(self.use_hard)

        self.use_soft = QtWidgets.QRadioButton(self)
        self.use_soft.setMaximumSize(QtCore.QSize(512, 16))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.use_soft.setFont(font)
        self.use_soft.setObjectName("soft")
        self.verticalLayout.addWidget(self.use_soft)

        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.radio_group = QtWidgets.QButtonGroup(self)
        self.radio_group.addButton(self.use_hard)
        self.radio_group.addButton(self.use_soft)
        self.use_hard.setChecked(True)
        self.radio_group.buttonToggled.connect(self.on_button_toggled)

        self.groupBox = QtWidgets.QGroupBox(self)
        self.groupBox.setMaximumSize(QtCore.QSize(16777215, 144))
        self.groupBox.setFont(font)
        self.groupBox.setStyleSheet("QGroupBox { border: 0px;}")
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setMaximumSize(QtCore.QSize(16777215, 16))
        self.label.setObjectName("label")
        self.label.setFont(font)
        self.verticalLayout_2.addWidget(self.label)
        self.spin_box = QtWidgets.QSpinBox(self)
        self.spin_box.setMinimum(1)
        self.spin_box.setMaximum(10)
        self.spin_box.setObjectName("iter_rounds")
        self.spin_box.setFont(font)
        self.verticalLayout_2.addWidget(self.spin_box)

        self.label2 = QtWidgets.QLabel(self.groupBox)
        self.label2.setMaximumSize(QtCore.QSize(16777215, 16))
        self.label2.setObjectName("label2")
        self.label2.setFont(font)
        self.verticalLayout_2.addWidget(self.label2)
        self.spin_box2 = QtWidgets.QDoubleSpinBox(self.groupBox)
        self.spin_box2.setMinimum(0.05)
        self.spin_box2.setMaximum(0.95)
        self.spin_box2.setSingleStep(0.05)
        self.spin_box2.setObjectName("threshold")
        self.spin_box2.setFont(font)
        self.spin_box2.setValue(0.7)
        self.verticalLayout_2.addWidget(self.spin_box2)
        self.verticalLayout.addWidget(self.groupBox)

        # self.lineEdit = QtWidgets.QLineEdit(self)
        # font = QtGui.QFont()
        # font.setFamily("微软雅黑")
        # self.lineEdit.setFont(font)
        # self.lineEdit.setObjectName("iter_rounds")
        # self.verticalLayout.addWidget(self.lineEdit)

        font = QtGui.QFont()
        font.setFamily("微软雅黑")
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
        self.setWindowTitle(_translate("select_method", "选择标签方法和迭代次数"))
        self.use_hard.setText(_translate("select_method", "Hard"))
        self.use_soft.setText(_translate("select_method", "Soft"))
        self.label.setText(_translate("select_method", "迭代次数"))
        self.label2.setText(_translate("select_method", "置信度阈值"))

    def on_button_toggled(self, btn, checked):
        if checked:
            print('Selected button ID:', btn.objectName())
            self.selected_method = btn.objectName()

    def accept(self):
        method = self.selected_method
        print(method)
        iter_rounds = int(self.spin_box.text())
        print(iter_rounds)
        threshold = float(self.spin_box2.text())
        self.close()
        self.signal_annotate_method.emit((method, iter_rounds, threshold))
