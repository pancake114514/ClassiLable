from PyQt5 import QtCore, QtGui, QtWidgets


class merge_hint(QtWidgets.QDialog):
    signal_yes_or_no = QtCore.pyqtSignal(bool)

    def __init__(self, parent=None):
        super(merge_hint, self).__init__(parent)
        self.setupUi()

    def setupUi(self):
        self.setObjectName("hint")
        self.resize(326, 177)
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        self.really = QtWidgets.QLabel(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.really.sizePolicy().hasHeightForWidth())
        self.really.setSizePolicy(sizePolicy)
        self.really.setMinimumSize(QtCore.QSize(0, 128))
        self.really.setMaximumSize(QtCore.QSize(16777215, 128))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.really.setFont(font)
        self.really.setAlignment(QtCore.Qt.AlignCenter)
        self.really.setObjectName("really")
        self.verticalLayout.addWidget(self.really)
        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.buttonBox.setFont(font)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi()
        self.buttonBox.accepted.connect(self.accept)  # type: ignore
        self.buttonBox.rejected.connect(self.reject)  # type: ignore
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("hint", "Really?"))
        self.really.setText(_translate("hint", "真的要合并伪标签与有标签数据吗？"))

    def accept(self):
        self.close()
        self.signal_yes_or_no.emit(True)
