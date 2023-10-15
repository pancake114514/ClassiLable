from PyQt5 import QtCore, QtGui, QtWidgets
import window_input_classes
import os, json


class window_createproj(QtWidgets.QDialog):
    signal_get_projFile = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super(window_createproj, self).__init__(parent)
        self.inputclass_window = window_input_classes.window_inputClassesList(self)
        self.inputclass_window.signal_list.connect(self.get_label_list)
        self.setupUi()

    def setupUi(self):
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint, True)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setObjectName("Dialog")
        self.resize(384, 256)
        self.setFixedSize(384,256)
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        # 设置几个成员变量记录参数
        self.project_name = ''
        self.project_file_path = ''
        self.picfolder_path = ''
        self.class_num = 0
        self.label_list = []  # 从次级窗口接受标签列表

        # 输入项目名称框
        self.ProjectName = QtWidgets.QLineEdit(self)
        self.ProjectName.setMinimumSize(QtCore.QSize(256, 16))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.ProjectName.setFont(font)
        self.ProjectName.setInputMask("")
        self.ProjectName.setAlignment(QtCore.Qt.AlignCenter)
        self.ProjectName.setClearButtonEnabled(False)
        self.ProjectName.setObjectName("ProjectName")
        self.verticalLayout.addWidget(self.ProjectName)

        # 项目路径
        self.getProjectFilepath = QtWidgets.QPushButton(self)
        self.getProjectFilepath.setMinimumSize(QtCore.QSize(256, 0))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.getProjectFilepath.setFont(font)
        self.getProjectFilepath.setObjectName("ProjectFilePath")
        self.verticalLayout.addWidget(self.getProjectFilepath)
        self.getProjectFilepath.clicked.connect(self.on_button_projpath_clicked)

        # 图片文件夹
        self.getImagePath = QtWidgets.QPushButton(self)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.getImagePath.setFont(font)
        self.getImagePath.setObjectName("ImgFilePath")
        self.verticalLayout.addWidget(self.getImagePath)
        self.getImagePath.clicked.connect(self.on_button_picpath_clicked)

        # 类别数量
        self.getClassNum = QtWidgets.QLineEdit(self)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.getClassNum.setFont(font)
        self.getClassNum.setAlignment(QtCore.Qt.AlignCenter)
        self.getClassNum.setObjectName("Class_num")
        self.verticalLayout.addWidget(self.getClassNum)

        # OK和Cancel
        self.buttonBox = QtWidgets.QDialogButtonBox(self)
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
        self.setWindowTitle(_translate("Dialog", "创建标注项目"))
        self.ProjectName.setPlaceholderText(_translate("Dialog", "项目名"))
        self.getProjectFilepath.setText(_translate("Dialog", "选择项目存放路径"))
        self.getImagePath.setText(_translate("Dialog", "选择图片文件夹路径"))
        self.getClassNum.setPlaceholderText(_translate("Dialog", "分类类别数"))

    def get_label_list(self, labellist):
        self.label_list = labellist
        print(f'label list from create : {self.label_list}')

    def accept(self):
        # 读取QLineEdit对象中的文本
        proj_name_text = self.ProjectName.text()
        if not proj_name_text:
            QtWidgets.QMessageBox.warning(self, "OOps!", "项目名不能为空")
        else:
            self.project_name = proj_name_text
            print(proj_name_text)

        # 配置文件路径
        if not self.project_file_path:
            QtWidgets.QMessageBox.warning(self, "OOps!", "项目文件路径不能为空")
        else:
            print(self.project_file_path)

        # 图片文件夹路径
        if not self.picfolder_path:
            QtWidgets.QMessageBox.warning(self, "OOps!", "图片文件夹不能为空")
        else:
            print(self.picfolder_path)

        # 类型数目
        classes = self.getClassNum.text()
        if not proj_name_text:
            QtWidgets.QMessageBox.warning(self, "OOps!", "类型数不能为空")
        else:
            self.class_num = int(classes)
            print(self.class_num)

        # 此时四个关键参数齐全，开启标签内容输入
        self.inputclass_window.setupUi(self.class_num)
        self.inputclass_window.show()
        self.inputclass_window.exec_()
        print(f'in create{self.label_list}')
        # 获得了类别标签
        # 接下来创建一份配置文件
        new_filepath = os.path.join(self.project_file_path, self.project_name + '.json')
        proj_file_content = {
            "pic_path": self.picfolder_path,
            "label_list": self.label_list
        }
        if not os.path.exists(os.path.join(self.picfolder_path, 'labelled')):
            os.makedirs(os.path.join(self.picfolder_path, 'labelled'))
        if not os.path.exists(os.path.join(self.picfolder_path, 'pseudo')):
            pseudo_path = os.path.join(self.picfolder_path, 'pseudo')
            os.makedirs(pseudo_path)
            if not os.path.exists(os.path.join(pseudo_path, 'pseudo.csv')):
                with open(os.path.join(pseudo_path, 'pseudo.csv'), mode='w') as file:
                    pass
        if not os.path.exists(os.path.join(self.picfolder_path, 'models')):
            os.makedirs(os.path.join(self.picfolder_path, 'models'))
        with open(os.path.join(self.picfolder_path, 'labels.csv'), mode='w') as file:
            pass

        with open(new_filepath, 'w') as f:
            json.dump(proj_file_content, f)
        self.signal_get_projFile.emit(new_filepath)
        self.close()

    def on_button_picpath_clicked(self):
        # 显示文件选择对话框
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(self, "选择图片文件夹")
        # 如果用户选择了文件夹，则打印文件路径
        if folder_path:
            self.picfolder_path = folder_path
            print(folder_path)

    def on_button_projpath_clicked(self):
        # 显示文件选择对话框
        projfile_path = QtWidgets.QFileDialog.getExistingDirectory(self, "选择项目配置文件的存放路径")
        # 如果用户选择了文件夹，则打印文件路径
        if projfile_path:
            self.project_file_path = projfile_path
            print(projfile_path)
