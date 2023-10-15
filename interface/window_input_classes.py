from PyQt5 import QtCore, QtGui, QtWidgets


class window_inputClassesList(QtWidgets.QDialog):
    signal_list = QtCore.pyqtSignal(list)

    def __init__(self, parent=None):
        super(window_inputClassesList, self).__init__(parent)

    def setupUi(self, classnum):
        # 类别数
        self.class_num = classnum
        print(f'in setupui classes = {self.class_num}')
        # 用于给上级窗口传递信息
        # self.send_list = QtCore.pyqtSignal(list)
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint, True)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setObjectName("InputClassesList")
        self.resize(400, 400)
        self.setFixedSize(400, 400)
        self.horizontalLayout = QtWidgets.QHBoxLayout(self)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.tableWidget = QtWidgets.QTableWidget(self)
        self.tableWidget.setObjectName("LabelTabel")
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setRowCount(self.class_num)
        self.horizontalLayout.addWidget(self.tableWidget)

        # 设置水平表头标签
        header_labels = ['类型编号', '标签值']
        self.tableWidget.setHorizontalHeaderLabels(header_labels)
        self.tableWidget.horizontalHeader().setVisible(True)
        self.tableWidget.verticalHeader().setVisible(False)

        # 设置第一列不可编辑
        for i in range(self.class_num):
            item = QtWidgets.QTableWidgetItem(str(i))
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.tableWidget.setItem(i, 0, item)

        # 设置第二列可编辑
        for i in range(self.class_num):
            item = QtWidgets.QTableWidgetItem()
            item.setFlags(QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.tableWidget.setItem(i, 1, item)

        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.buttonBox.setFont(font)
        self.buttonBox.setOrientation(QtCore.Qt.Vertical)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.horizontalLayout.addWidget(self.buttonBox)

        self.retranslateUi()
        self.buttonBox.accepted.connect(self.accept)  # type: ignore
        self.buttonBox.rejected.connect(self.reject)  # type: ignore
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("InputClassesList", f"类别={self.class_num}"))

    def accept(self):
        label_list = []
        flag = True
        for i in range(self.class_num):
            item = self.tableWidget.item(i, 1)
            text = item.text()
            if text == '':
                QtWidgets.QMessageBox.warning(self, "OOps!", "不得出现空标签")
                flag = False
                break
            else:
                label_list.append(text)
        if flag:
            print(label_list)
            self.signal_list.emit(label_list)
            self.close()
