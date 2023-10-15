import json
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog
from window_createproj import window_createproj
import pyqtgraph as pg
from pyqtgraph import ImageView
import cv2
import glob
from del_one_pesudo import del_from_pseudo
from window_detect_select import detect_select
from window_auto_annotate import annotate_select
from thread_methods import *
from window_merge_hint import merge_hint

pg.setConfigOption('background', 'w')


class MyMainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MyMainWindow, self).__init__(parent)
        self.NextPic = None
        self.NewProjDialogWindow = window_createproj(self)
        self.project_filename = ''
        self.NewProjDialogWindow.signal_get_projFile.connect(self.get_ProjectFile)
        self.window_detect = detect_select(self)
        self.window_detect.signal_detect_method.connect(self.get_detect_method)
        self.window_autoannotate = annotate_select(self)
        self.window_autoannotate.signal_annotate_method.connect(self.get_annotate_method)
        self.merge = merge_hint(self)
        self.merge.signal_yes_or_no.connect(self.get_pseudo_merged)
        # 关键属性
        # 图像存储文件夹
        self.img_folder = ''
        # 类型标签列表
        self.label_list = []
        # 已标签图像
        self.labelled_folder = ''
        # 带伪标签的图像路径
        self.pseudo_folder = ''
        # 模型存放路径
        self.model_folder = ''
        # 标签文件
        self.label_csv = ''
        # 伪标签文件
        self.pseudo_csv = ''
        # 未标签文件列表
        self.unlabelled_filelist = []
        # 已标注文件列表
        self.labelled_filelist = []
        # 伪标签文件列表
        self.pseudo_filelist = []
        # 噪声文件列表
        self.noise_filelist = []
        # 选中样本名
        self.selected_sample = ''
        # 选中标签
        self.selected_label = ''
        # 选中列表
        self.selected_file_list = []
        # 初始化UI
        self.setupUi()

    def setupUi(self):
        self.setObjectName("LabelClass")
        main_icon = QtGui.QIcon()
        main_icon.addPixmap(QtGui.QPixmap("../icon/main/miu.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(main_icon)
        self.resize(1280, 960)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.MidGroup = QtWidgets.QGroupBox(self.centralwidget)
        self.MidGroup.setAccessibleName("")
        self.MidGroup.setStyleSheet("#MidGroup{border:none}")
        self.MidGroup.setMinimumHeight(768)
        self.MidGroup.setTitle("")
        self.MidGroup.setObjectName("MidGroup")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.MidGroup)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.graphicsView = ImageView()
        self.graphicsView.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.graphicsView.ui.histogram.hide()
        self.graphicsView.ui.menuBtn.hide()
        self.graphicsView.ui.roiBtn.hide()
        self.verticalLayout_2.addWidget(self.graphicsView)

        self.MidBottomGroup = QtWidgets.QGroupBox(self.MidGroup)
        self.MidBottomGroup.setMinimumSize(QtCore.QSize(0, 128))
        self.MidBottomGroup.setMaximumSize(QtCore.QSize(16777215, 256))
        self.MidBottomGroup.setStyleSheet("")
        self.MidBottomGroup.setTitle("")
        self.MidBottomGroup.setObjectName("MidBottomGroup")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.MidBottomGroup)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.LabelAdvice = QtWidgets.QLabel(self.MidBottomGroup)
        self.LabelAdvice.setMaximumSize(QtCore.QSize(16777215, 16))
        self.LabelAdvice.setObjectName("LabelAdvice")
        self.verticalLayout_3.addWidget(self.LabelAdvice)
        self.BottomInner = QtWidgets.QGroupBox(self.MidBottomGroup)
        self.BottomInner.setMinimumSize(QtCore.QSize(722, 218))
        self.BottomInner.setStyleSheet("QGroupBox{border:none}")
        self.BottomInner.setTitle("")
        self.BottomInner.setObjectName("BottomInner")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.BottomInner)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.LabelList_Select = QtWidgets.QListWidget(self.BottomInner)
        self.LabelList_Select.setObjectName("LabelList_Select")
        self.horizontalLayout_2.addWidget(self.LabelList_Select)
        self.LabelList_Select.currentItemChanged.connect(self.get_selected_label)
        self.installEventFilter(self)

        self.AcceptCancelBox = QtWidgets.QGroupBox(self.BottomInner)
        self.AcceptCancelBox.setTitle("")
        self.AcceptCancelBox.setObjectName("AcceptCancelBox")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.AcceptCancelBox)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.Check_Manual_annotate = QtWidgets.QPushButton(self.AcceptCancelBox)
        self.Check_Manual_annotate.setMinimumSize(QtCore.QSize(0, 36))
        self.Check_Manual_annotate.setObjectName("Check_Manual_annotate")
        self.Check_Manual_annotate.setEnabled(False)
        self.AnnotateShortcut = QtWidgets.QShortcut(QtGui.QKeySequence(Qt.Key_S), self)
        self.AnnotateShortcut.activated.connect(self.to_annotate)
        self.AnnotateShortcut.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setFamily("微软雅黑")
        self.Check_Manual_annotate.setFont(font)
        self.Check_Manual_annotate.clicked.connect(self.to_annotate)
        self.verticalLayout_4.addWidget(self.Check_Manual_annotate)
        self.horizontalLayout_2.addWidget(self.AcceptCancelBox)
        self.verticalLayout_3.addWidget(self.BottomInner)
        self.verticalLayout_2.addWidget(self.MidBottomGroup)
        self.horizontalLayout.addWidget(self.MidGroup)
        self.RightGroup = QtWidgets.QGroupBox(self.centralwidget)
        self.RightGroup.setMaximumSize(QtCore.QSize(256, 16777215))
        self.RightGroup.setStyleSheet("QGroupBox{border:none}")
        self.RightGroup.setTitle("")
        self.RightGroup.setObjectName("RightGroup")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.RightGroup)
        self.verticalLayout.setObjectName("verticalLayout")

        # 伪标签文字框
        self.label = QtWidgets.QLabel(self.RightGroup)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setFamily("微软雅黑")
        self.label.setFont(font)
        self.LabelAdvice.setFont(font)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        # 用于显示伪标签的样本
        self.ListPseudo = QtWidgets.QListWidget(self.RightGroup)
        self.ListPseudo.setObjectName("ListPseudo")
        self.verticalLayout.addWidget(self.ListPseudo)
        self.ListPseudo.currentItemChanged.connect(self.get_pseudo_fname)

        # 无标签文字框
        self.label_2 = QtWidgets.QLabel(self.RightGroup)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setFamily("微软雅黑")
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        # 用于显示无标签的样本
        self.ListUnlabel = QtWidgets.QListWidget(self.RightGroup)
        self.ListUnlabel.setObjectName("ListUnlabel")
        self.verticalLayout.addWidget(self.ListUnlabel)
        self.ListUnlabel.currentItemChanged.connect(self.get_unlabelled_fname)

        # 已标签文字框
        self.label_3 = QtWidgets.QLabel(self.RightGroup)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setFamily("微软雅黑")
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)
        # 用于显示已标签的样本
        self.ListLabelled = QtWidgets.QListWidget(self.RightGroup)
        self.ListLabelled.setObjectName("ListLabelled")
        self.verticalLayout.addWidget(self.ListLabelled)
        self.ListLabelled.currentItemChanged.connect(self.get_labelled_fname)

        # 可能的噪声样本
        self.label_4 = QtWidgets.QLabel(self.RightGroup)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setFamily("微软雅黑")
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_4)
        # 用于显示可能标错的样本
        self.ListWrongLabel = QtWidgets.QListWidget(self.RightGroup)
        self.ListWrongLabel.setObjectName("ListWrongLabel")
        self.verticalLayout.addWidget(self.ListWrongLabel)
        self.ListWrongLabel.currentItemChanged.connect(self.get_noise_fname)

        self.horizontalLayout.addWidget(self.RightGroup)
        self.setCentralWidget(self.centralwidget)
        self.Left_Toolbar = QtWidgets.QToolBar(self)
        self.Left_Toolbar.setEnabled(True)
        self.Left_Toolbar.setMaximumSize(QtCore.QSize(200, 16777215))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.Left_Toolbar.setFont(font)
        self.Left_Toolbar.setStyleSheet("QToolBar{\n"
                                        "    background-color: rgb(200,200,200);\n"
                                        "}")
        self.Left_Toolbar.setMovable(False)
        self.Left_Toolbar.setIconSize(QtCore.QSize(36, 36))
        self.Left_Toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.Left_Toolbar.setObjectName("Left_Toolbar")
        self.addToolBar(QtCore.Qt.LeftToolBarArea, self.Left_Toolbar)

        # 工具栏打开配置文件
        self.OpenProject = QtWidgets.QAction(self)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../icon/open_proj/icons8-extra-features-96.png"), QtGui.QIcon.Normal,
                       QtGui.QIcon.Off)
        self.OpenProject.setIcon(icon)
        self.OpenProject.setFont(font)
        self.OpenProject.setObjectName("OpenProject")
        self.OpenProject.triggered.connect(self.open_ProjectFile)

        # 工具栏创建配置文件
        self.NewProject = QtWidgets.QAction(self)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("../icon/new_proj/icons8-add-properties-96.png"), QtGui.QIcon.Normal,
                        QtGui.QIcon.Off)
        self.NewProject.setFont(font)
        self.NewProject.setIcon(icon1)
        self.NewProject.setObjectName("NewProject")
        self.NewProject.triggered.connect(self.create_ProjectFile)

        # 上一张图片
        self.PrevPic = QtWidgets.QAction(self)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("../icon/pic_prev/icons8-arrow-pointing-left-96.png"), QtGui.QIcon.Normal,
                        QtGui.QIcon.Off)
        self.PrevPic.setFont(font)
        self.PrevPic.setIcon(icon2)
        self.PrevPic.setEnabled(False)
        self.PrevPic.setObjectName("PrevPic")
        self.PrevPic.triggered.connect(self.point_prev_pic)

        # 下一张图片
        self.NextPic = QtWidgets.QAction(self)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("../icon/pic_next/icons8-arrow-96.png"), QtGui.QIcon.Normal,
                        QtGui.QIcon.Off)
        self.NextPic.setFont(font)
        self.NextPic.setIcon(icon3)
        self.NextPic.setEnabled(False)
        self.NextPic.setObjectName("NextPic")
        self.NextPic.triggered.connect(self.point_next_pic)

        # 执行去噪
        self.GetNoiseDetected = QtWidgets.QAction(self)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap("../icon/get_noisedetect/icons8-nothing-found-96.png"), QtGui.QIcon.Normal,
                        QtGui.QIcon.Off)
        self.GetNoiseDetected.setFont(font)
        self.GetNoiseDetected.setIcon(icon4)
        self.GetNoiseDetected.setEnabled(False)
        self.GetNoiseDetected.setObjectName("GetNoiseDetected")
        self.GetNoiseDetected.triggered.connect(self.open_window_detect)

        # 执行自动标注
        self.GetAutoAnnotate = QtWidgets.QAction(self)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap("../icon/get_auto_annotate/icons8-tick-box-96.png"), QtGui.QIcon.Normal,
                        QtGui.QIcon.Off)
        self.GetAutoAnnotate.setFont(font)
        self.GetAutoAnnotate.setIcon(icon5)
        self.GetAutoAnnotate.setEnabled(False)
        self.GetAutoAnnotate.setObjectName("GetAutoAnnotate")
        self.GetAutoAnnotate.triggered.connect(self.open_window_annotate)

        # 合并伪标签数据集
        self.GetSetMerged = QtWidgets.QAction(self)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap("../icon/merge_set/icons8-merge-git-96.png"), QtGui.QIcon.Normal,
                        QtGui.QIcon.Off)
        self.GetSetMerged.setIcon(icon7)
        self.GetSetMerged.setFont(font)
        self.GetSetMerged.setEnabled(False)
        self.GetSetMerged.setObjectName("MergeSet")
        self.GetSetMerged.triggered.connect(self.open_merge_hint)

        # 一键导出
        self.GetSetExported = QtWidgets.QAction(self)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap("../icon/export/icons8-archive-folder-96.png"), QtGui.QIcon.Normal,
                        QtGui.QIcon.Off)
        self.GetSetExported.setIcon(icon6)
        self.GetSetExported.setFont(font)
        self.GetSetExported.setEnabled(False)
        self.GetSetExported.setObjectName("ExportSet")
        self.GetSetExported.triggered.connect(self.get_dataset_exported)

        self.Left_Toolbar.addAction(self.NewProject)
        self.Left_Toolbar.addAction(self.OpenProject)
        self.Left_Toolbar.addAction(self.PrevPic)
        self.Left_Toolbar.addAction(self.NextPic)
        self.Left_Toolbar.addAction(self.GetNoiseDetected)
        self.Left_Toolbar.addAction(self.GetAutoAnnotate)
        self.Left_Toolbar.addAction(self.GetSetMerged)
        self.Left_Toolbar.addAction(self.GetSetExported)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.MouseButtonPress:
            if not source == self.LabelList_Select:
                self.Check_Manual_annotate.setEnabled(False)  # 将QButton设置为不可用
                self.AnnotateShortcut.setEnabled(False)
        return super().eventFilter(source, event)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("LabelClass", "ClassiLabel"))
        self.LabelAdvice.setText(_translate("LabelClass", "这是提示窗"))
        self.Check_Manual_annotate.setText(_translate("LabelClass", "确认(S)"))
        self.label.setText(_translate("LabelClass", "自动标注样本"))
        self.label_2.setText(_translate("LabelClass", "尚未标注"))
        self.label_3.setText(_translate("LabelClass", "已标注"))
        self.label_4.setText(_translate("LabelClass", "可能的噪声样本"))
        self.Left_Toolbar.setWindowTitle(_translate("LabelClass", "toolBar_2"))
        self.OpenProject.setText(_translate("LabelClass", "打开项目"))
        self.OpenProject.setToolTip(_translate("LabelClass", "打开已有标注项目"))
        self.NewProject.setText(_translate("LabelClass", "新建项目"))
        self.NewProject.setToolTip(_translate("LabelClass", "新建项目"))
        self.PrevPic.setText(_translate("LabelClass", "上一张"))
        self.NextPic.setText(_translate("LabelClass", "下一张"))
        self.GetNoiseDetected.setText(_translate("LabelClass", "执行噪声检测"))
        self.GetAutoAnnotate.setText(_translate("LabelClass", "执行自动标注"))
        self.GetSetMerged.setText(_translate("LabelClass", "合并伪标签"))
        self.GetSetExported.setText(_translate("LabelClass", "一键导出数据集"))

    def open_ProjectFile(self):
        # 打开项目配置文件
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        fileName, _ = QFileDialog.getOpenFileName(self, "Open Project", "", "JSON (*.json)", options=options)
        if fileName:
            print("Selected file:", fileName)
        self.get_ProjectFile(fileName)

    def create_ProjectFile(self):
        # 创建项目配置文件
        self.NewProjDialogWindow.show()
        self.NewProjDialogWindow.exec_()

    def get_ProjectFile(self, projFilename):
        self.project_filename = projFilename
        if not projFilename == '':
            with open(self.project_filename, 'r') as proj_file:
                obj = json.load(proj_file)
                try:
                    self.img_folder = obj["pic_path"]
                    self.img_folder = self.img_folder.replace('/', '\\')
                    print(self.img_folder)
                    self.label_list = obj["label_list"]
                    self.labelled_folder = os.path.join(self.img_folder, "labelled")
                    if not os.path.exists(self.labelled_folder):
                        os.makedirs(self.labelled_folder)

                    self.pseudo_folder = os.path.join(self.img_folder, "pseudo")
                    if not os.path.exists(self.pseudo_folder):
                        os.makedirs(self.pseudo_folder)
                    self.pseudo_csv = os.path.join(self.pseudo_folder, "pseudo.csv")

                    self.model_folder = os.path.join(self.img_folder, "models")
                    if not os.path.exists(self.model_folder):
                        os.makedirs(self.model_folder)

                    self.label_csv = os.path.join(self.img_folder, "labels.csv")

                    self.unlabelled_filelist = glob.glob(os.path.join(self.img_folder, '*.jpg')) + \
                                               glob.glob(os.path.join(self.img_folder, '*.bmp')) + \
                                               glob.glob(os.path.join(self.img_folder, '*.png'))
                    self.labelled_filelist = glob.glob(os.path.join(self.labelled_folder, '*.jpg')) + \
                                             glob.glob(os.path.join(self.labelled_folder, '*.bmp')) + \
                                             glob.glob(os.path.join(self.labelled_folder, '*.png'))
                    if len(self.labelled_filelist) >= 100:
                        self.GetNoiseDetected.setEnabled(True)
                        self.GetAutoAnnotate.setEnabled(True)
                    if len(self.labelled_filelist) >= 1:
                        self.GetSetExported.setEnabled(True)
                    self.pseudo_filelist = glob.glob(os.path.join(self.pseudo_folder, '*.jpg')) + \
                                           glob.glob(os.path.join(self.pseudo_folder, '*.bmp')) + \
                                           glob.glob(os.path.join(self.pseudo_folder, '*.png'))
                    self.ListPseudo.clear()
                    self.ListLabelled.clear()
                    self.ListUnlabel.clear()
                    self.ListWrongLabel.clear()
                    self.LabelList_Select.clear()
                    if len(self.pseudo_filelist) > 0:
                        self.GetSetMerged.setEnabled(True)
                    for item in self.pseudo_filelist:
                        self.ListPseudo.addItem(item)
                    for item in self.unlabelled_filelist:
                        self.ListUnlabel.addItem(item)
                    for item in self.labelled_filelist:
                        self.ListLabelled.addItem(item)
                    for item in self.label_list:
                        self.LabelList_Select.addItem(item)
                    self.PrevPic.setEnabled(True)
                    self.NextPic.setEnabled(True)

                except KeyError as E:
                    print(f"KeyError: {E}")
                    QtWidgets.QMessageBox.warning(self, "OOps!", "非法的项目配置文件")

    def point_prev_pic(self):
        for i in range(len(self.selected_file_list)):
            if self.selected_file_list[i] == self.selected_sample and i > 0:
                self.selected_sample = self.selected_file_list[i - 1]
                self.show_img(self.selected_sample)
                if self.selected_file_list == self.labelled_filelist \
                        or self.selected_file_list == self.noise_filelist:
                    # 已标签/噪声（噪声也是已标签）
                    found, label = get_label.get_label(self.label_csv, self.selected_sample)
                    text = f'文件名：{os.path.basename(self.selected_sample)}，标签为{self.label_list[label]}'
                    # 设置选中文件名
                    if found and not label == -1:
                        self.show_text(text)
                elif self.selected_file_list == self.unlabelled_filelist:
                    # 在无标签列表
                    text = f'文件名：{os.path.basename(self.selected_sample)}'
                    if os.path.exists(os.path.join(self.model_folder, 'self_training.pkl')):
                        predicted = ui_interface.interface_advice_label(len(self.label_list), self.selected_sample,
                                                                        os.path.join(self.model_folder,
                                                                                     'self_training.pkl'))
                        text = text + f'，它可能是{self.label_list[int(predicted[0])]}，概率为{predicted[1]}'
                    elif os.path.exists(os.path.join(self.model_folder, 'validation.pkl')):
                        predicted = ui_interface.interface_advice_label(len(self.label_list), self.selected_sample,
                                                                        os.path.join(self.model_folder,
                                                                                     'validation.pkl'))
                        text = text + f'，它可能是{self.label_list[int(predicted[0])]}，概率为{predicted[1]}'
                    self.show_text(text)
                elif self.selected_file_list == self.pseudo_filelist:
                    # 在伪标签列表
                    found, label = get_label.get_label(self.pseudo_csv, self.selected_sample)
                    text = f'文件名：{os.path.basename(self.selected_sample)}，标签为{self.label_list[label]}'
                    # 设置选中文件名
                    if found and not label == -1:
                        self.show_text(text)
                break

    def point_next_pic(self):
        for i in range(len(self.selected_file_list)):
            if self.selected_file_list[i] == self.selected_sample and i < len(self.selected_file_list) - 1:
                self.selected_sample = self.selected_file_list[i + 1]
                self.show_img(self.selected_sample)
                if self.selected_file_list == self.labelled_filelist \
                        or self.selected_file_list == self.noise_filelist:
                    # 已标签/噪声（噪声也是已标签）
                    found, label = get_label.get_label(self.label_csv, self.selected_sample)
                    text = f'文件名：{os.path.basename(self.selected_sample)}，标签为{self.label_list[label]}'
                    # 设置选中文件名
                    if found and not label == -1:
                        self.show_text(text)
                elif self.selected_file_list == self.unlabelled_filelist:
                    # 在无标签列表
                    text = f'文件名：{os.path.basename(self.selected_sample)}'
                    if os.path.exists(os.path.join(self.model_folder, 'self_training.pkl')):
                        predicted = ui_interface.interface_advice_label(len(self.label_list), self.selected_sample,
                                                                        os.path.join(self.model_folder,
                                                                                     'self_training.pkl'))
                        text = text + f'，它可能是{self.label_list[int(predicted[0])]}，概率为{predicted[1]}'
                    elif os.path.exists(os.path.join(self.model_folder, 'validation.pkl')):
                        predicted = ui_interface.interface_advice_label(len(self.label_list), self.selected_sample,
                                                                        os.path.join(self.model_folder,
                                                                                     'validation.pkl'))
                        text = text + f'，它可能是{self.label_list[int(predicted[0])]}，概率为{predicted[1]}'
                    self.show_text(text)
                elif self.selected_file_list == self.pseudo_filelist:
                    # 在伪标签列表
                    found, label = get_label.get_label(self.pseudo_csv, self.selected_sample)
                    text = f'文件名：{os.path.basename(self.selected_sample)}，标签为{self.label_list[label]}'
                    # 设置选中文件名
                    if found and not label == -1:
                        self.show_text(text)
                break

    def show_img(self, img_filename):
        # 图片框显示图像
        img = cv2.imread(img_filename)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        img = cv2.flip(img, 0)
        self.graphicsView.setImage(img)
        # self.show_text(img_filename)

    def show_text(self, text):
        # 给建议框设置文字
        text = str(text)
        self.LabelAdvice.setText(text)

    def get_unlabelled_fname(self, current, previous):
        # 获取当前选中项的内容
        if current is not None:
            selected_text = current.text()
            self.selected_file_list = self.unlabelled_filelist
            # 将选中项内容传递给show_img()函数
            self.show_img(selected_text)
            # 设置选中文件名
            self.selected_sample = selected_text
            text = f"文件名：{os.path.basename(selected_text)}"
            if os.path.exists(os.path.join(self.model_folder, 'self_training.pkl')):
                predicted = ui_interface.interface_advice_label(len(self.label_list), self.selected_sample,
                                                                os.path.join(self.model_folder,
                                                                             'self_training.pkl'))
                text = text + f'，它可能是{self.label_list[int(predicted[0])]}，概率为{predicted[1]}'
            elif os.path.exists(os.path.join(self.model_folder, 'validation.pkl')):
                predicted = ui_interface.interface_advice_label(len(self.label_list), self.selected_sample,
                                                                os.path.join(self.model_folder,
                                                                             'validation.pkl'))
                text = text + f'，它可能是{self.label_list[int(predicted[0])]}，概率为{predicted[1]}'
            self.show_text(text)

    def get_labelled_fname(self, current, previous):
        if current is not None:
            selected_text = current.text()
            self.selected_file_list = self.labelled_filelist
            # 将选中项内容传递给show_img()函数
            self.show_img(selected_text)
            found, label = get_label.get_label(self.label_csv, selected_text)
            text = f'文件名：{os.path.basename(selected_text)}，标签为{self.label_list[label]}'
            # 设置选中文件名
            self.selected_sample = selected_text
            if found and not label == -1:
                self.show_text(text)

    def get_pseudo_fname(self, current, previous):
        if current is not None:
            selected_text = current.text()
            self.selected_file_list = self.pseudo_filelist
            # 将选中项内容传递给show_img()函数
            self.show_img(selected_text)
            found, label = get_label.get_label(self.pseudo_csv, selected_text)
            text = f'文件名：{os.path.basename(selected_text)}，伪标签为{self.label_list[label]}'
            # 设置选中文件名
            self.selected_sample = selected_text
            if found and not label == -1:
                self.show_text(text)

    def get_noise_fname(self, current, previous):
        if current is not None:
            selected_text = current.text()
            self.selected_file_list = self.noise_filelist
            # 将选中项内容传递给show_img()函数
            self.show_img(selected_text)
            self.selected_sample = selected_text
            found, label = get_label.get_label(self.label_csv, selected_text)
            text = f'文件名：{os.path.basename(selected_text)}，标记为{self.label_list[label]}'
            if os.path.exists(os.path.join(self.model_folder, 'self_training.pkl')):
                predicted = ui_interface.interface_advice_label(len(self.label_list), self.selected_sample,
                                                                os.path.join(self.model_folder,
                                                                             'self_training.pkl'))
                text = text + f'，它可能是{self.label_list[int(predicted[0])]}，概率为{predicted[1]}'
            elif os.path.exists(os.path.join(self.model_folder, 'validation.pkl')):
                predicted = ui_interface.interface_advice_label(len(self.label_list), self.selected_sample,
                                                                os.path.join(self.model_folder,
                                                                             'validation.pkl'))
                text = text + f'，它可能是{self.label_list[int(predicted[0])]}，概率为{predicted[1]}'
            # 设置选中文件名
            if found and not label == -1:
                self.show_text(text)

    def get_selected_label(self, current, previous):
        if current is not None:
            selected_text = current.text()
            label = 0
            for i in range(len(self.label_list)):
                if self.label_list[i] == selected_text:
                    label = i
                    break
            self.selected_label = label
            if self.selected_label >= 0 and not self.selected_sample == '':
                print(f"Selected {self.selected_sample} will be annotated as {self.selected_label}")
                self.Check_Manual_annotate.setEnabled(True)
                self.AnnotateShortcut.setEnabled(True)
        else:
            self.Check_Manual_annotate.setEnabled(False)
            self.AnnotateShortcut.setEnabled(False)

    def to_annotate(self):
        annotate.manual_annotate(self.label_csv, self.selected_sample, self.selected_label)
        base_name = os.path.basename(self.selected_sample)
        src = self.selected_sample
        dst = os.path.join(self.labelled_folder, base_name)
        print(src)
        print(dst)
        if not dst == src:
            os.rename(src, dst)
        # 选取下一张图片
        for i in range(len(self.selected_file_list)):
            if self.selected_file_list[i] == self.selected_sample:
                if i < (len(self.selected_file_list) - 1):
                    self.selected_sample = self.selected_file_list[i + 1]
                    self.show_img(self.selected_sample)
                    break

        case = 0

        # 如果列表是已标签列表
        if self.selected_file_list == self.labelled_filelist:
            case = 1
            print(f'now list = labelled')
            found, label = get_label.get_label(self.label_csv, self.selected_sample)
            text = f'文件名：{os.path.basename(self.selected_sample)}，标签为{self.label_list[label]}'
            if found and not label == -1:
                self.show_text(text)
        # 如果列表是未标签列表
        elif self.selected_file_list == self.unlabelled_filelist:
            case = 2
            print(f'now list = unlabelled')
            # 设置选中文件名
            text = f'文件名：{os.path.basename(self.selected_sample)}'
            if os.path.exists(os.path.join(self.model_folder, 'self_training.pkl')):
                predicted = ui_interface.interface_advice_label(len(self.label_list), self.selected_sample,
                                                                os.path.join(self.model_folder,
                                                                             'self_training.pkl'))
                text = text + f'，它可能是{self.label_list[int(predicted[0])]}，概率为{predicted[1]}'
            elif os.path.exists(os.path.join(self.model_folder, 'validation.pkl')):
                predicted = ui_interface.interface_advice_label(len(self.label_list), self.selected_sample,
                                                                os.path.join(self.model_folder,
                                                                             'validation.pkl'))
                text = text + f'，它可能是{self.label_list[int(predicted[0])]}，概率为{predicted[1]}'
            self.show_text(text)
        # 如果列表是伪标签列表
        elif self.selected_file_list == self.pseudo_filelist:
            case = 3
            # 在下面添加代码：
            del_from_pseudo(self.pseudo_csv, src)
            # 将该文件(src)和其标签从pseudo.csv删去一行
            found, label = get_label.get_label(self.pseudo_csv, self.selected_sample)
            text = f'文件名：{os.path.basename(self.selected_sample)}，伪标签为{self.label_list[label]}'
            if found and not label == -1:
                self.show_text(text)

        elif self.selected_file_list == self.noise_filelist:
            case = 4
            found, label = get_label.get_label(self.label_csv, self.selected_sample)
            text = f'文件名：{os.path.basename(self.selected_sample)}，标签为{self.label_list[label]}'
            if os.path.exists(os.path.join(self.model_folder, 'self_training.pkl')):
                predicted = ui_interface.interface_advice_label(len(self.label_list), self.selected_sample,
                                                                os.path.join(self.model_folder,
                                                                             'self_training.pkl'))
                text = text + f'，但它可能是{self.label_list[int(predicted[0])]}，概率为{predicted[1]}'
            elif os.path.exists(os.path.join(self.model_folder, 'validation.pkl')):
                predicted = ui_interface.interface_advice_label(len(self.label_list), self.selected_sample,
                                                                os.path.join(self.model_folder,
                                                                             'validation.pkl'))
                text = text + f'，但它可能是{self.label_list[int(predicted[0])]}，概率为{predicted[1]}'
            self.show_text(text)

        # 更新文件列表

        self.unlabelled_filelist = glob.glob(os.path.join(self.img_folder, '*.jpg')) + \
                                   glob.glob(os.path.join(self.img_folder, '*.bmp')) + \
                                   glob.glob(os.path.join(self.img_folder, '*.png'))
        self.labelled_filelist = glob.glob(os.path.join(self.labelled_folder, '*.jpg')) + \
                                 glob.glob(os.path.join(self.labelled_folder, '*.bmp')) + \
                                 glob.glob(os.path.join(self.labelled_folder, '*.png'))
        if len(self.labelled_filelist) >= 100:
            self.GetNoiseDetected.setEnabled(True)
            self.GetAutoAnnotate.setEnabled(True)
        if len(self.labelled_filelist) >= 1:
            self.GetSetExported.setEnabled(True)
        self.pseudo_filelist = glob.glob(os.path.join(self.pseudo_folder, '*.jpg')) + \
                               glob.glob(os.path.join(self.pseudo_folder, '*.bmp')) + \
                               glob.glob(os.path.join(self.pseudo_folder, '*.png'))
        if len(self.pseudo_filelist) > 0:
            self.GetSetMerged.setEnabled(True)
        if case == 4:
            for i in range(len(self.noise_filelist)):
                # 从噪声标签列表中删除
                if src == self.noise_filelist[i]:
                    self.noise_filelist.pop(i)
                    break
            self.ListWrongLabel.clear()
            for item in self.noise_filelist:
                self.ListWrongLabel.addItem(item)
        elif case == 2:
            self.selected_file_list = self.unlabelled_filelist
        elif case == 3:
            self.selected_file_list = self.pseudo_filelist
        elif case == 1:
            self.selected_file_list = self.labelled_filelist
        self.ListPseudo.clear()
        self.ListUnlabel.clear()
        self.ListLabelled.clear()
        for item in self.pseudo_filelist:
            self.ListPseudo.addItem(item)
        for item in self.unlabelled_filelist:
            self.ListUnlabel.addItem(item)
        for item in self.labelled_filelist:
            self.ListLabelled.addItem(item)

    def open_window_detect(self):
        self.window_detect.show()
        self.window_detect.exec_()

    def get_detect_method(self, detect_method):
        print(f'main.py, detect method = {detect_method}')
        # 下面插入代码，执行自动去噪
        list_fname, list_label = get_label.get_all_labels(self.label_csv, self.labelled_folder)
        self.detect_thread = detect_thread()
        self.detect_thread.signal_returns_noise_fnames.connect(self.call_back_detect)
        self.detect_thread.get_args(list_fname, list_label, len(self.label_list),
                                    self.model_folder, detect_method[0], detect_method[1])
        self.detect_thread.start()
        self.LabelList_Select.setEnabled(False)
        self.Check_Manual_annotate.setEnabled(False)
        self.AnnotateShortcut.setEnabled(False)
        self.GetNoiseDetected.setEnabled(False)
        self.GetAutoAnnotate.setEnabled(False)
        self.NewProject.setEnabled(False)
        self.OpenProject.setEnabled(False)
        self.GetSetMerged.setEnabled(False)
        self.LabelAdvice.setText("正在执行噪声检测..")

    def call_back_detect(self, noise_samples):
        self.noise_filelist = noise_samples
        self.ListWrongLabel.clear()
        for item in self.noise_filelist:
            self.ListWrongLabel.addItem(item)
        QtWidgets.QMessageBox.warning(self, "我好了", f"噪声样本检测完成！")
        self.LabelList_Select.setEnabled(True)
        self.GetNoiseDetected.setEnabled(True)
        self.GetAutoAnnotate.setEnabled(True)
        self.NewProject.setEnabled(True)
        self.OpenProject.setEnabled(True)
        if len(self.pseudo_filelist) > 0:
            self.GetSetMerged.setEnabled(True)

    def open_window_annotate(self):
        self.window_autoannotate.show()
        self.window_autoannotate.exec_()

    def get_annotate_method(self, annotate_method):

        self.thread = annotate_thread()
        self.thread.signal_returns_tuples.connect(self.call_backlog)

        method = annotate_method[0]
        iter_rounds = annotate_method[1]
        threshold = annotate_method[2]
        print(f"main.py: method={method}, iter_rounds={iter_rounds}, threshold={threshold}")

        labelled_fnames, labels = get_label.get_all_labels(self.label_csv, self.labelled_folder)
        unlabelled_fnames = glob.glob(os.path.join(self.img_folder, '*.jpg')) + \
                            glob.glob(os.path.join(self.img_folder, '*.bmp')) + \
                            glob.glob(os.path.join(self.img_folder, '*.png'))

        self.thread.get_args(labelled_fnames, labels, unlabelled_fnames, len(self.label_list),
                             self.model_folder, method, iter_rounds, threshold)
        self.thread.start()
        self.LabelList_Select.setEnabled(False)
        self.Check_Manual_annotate.setEnabled(False)
        self.AnnotateShortcut.setEnabled(False)
        self.GetNoiseDetected.setEnabled(False)
        self.GetAutoAnnotate.setEnabled(False)
        self.NewProject.setEnabled(False)
        self.OpenProject.setEnabled(False)
        self.GetSetMerged.setEnabled(False)
        self.LabelAdvice.setText("正在执行自动标注..")

    def call_backlog(self, confident_tuples):
        """
        :param confident_tuples: List of confident tuples: (file_name,label)
        :return: None
        """
        for tuples in confident_tuples:
            pseudo_filename = tuples[0]
            pseudo_label = tuples[1]
            annotate.manual_annotate(self.pseudo_csv, pseudo_filename, pseudo_label)
            base_name = os.path.basename(pseudo_filename)
            dst = os.path.join(self.pseudo_folder, base_name)
            os.rename(pseudo_filename, dst)
        # 更新列表
        self.unlabelled_filelist = glob.glob(os.path.join(self.img_folder, '*.jpg')) + \
                                   glob.glob(os.path.join(self.img_folder, '*.bmp')) + \
                                   glob.glob(os.path.join(self.img_folder, '*.png'))
        self.labelled_filelist = glob.glob(os.path.join(self.labelled_folder, '*.jpg')) + \
                                 glob.glob(os.path.join(self.labelled_folder, '*.bmp')) + \
                                 glob.glob(os.path.join(self.labelled_folder, '*.png'))
        self.pseudo_filelist = glob.glob(os.path.join(self.pseudo_folder, '*.jpg')) + \
                               glob.glob(os.path.join(self.pseudo_folder, '*.bmp')) + \
                               glob.glob(os.path.join(self.pseudo_folder, '*.png'))

        self.ListPseudo.clear()
        self.ListUnlabel.clear()
        self.ListLabelled.clear()
        for item in self.pseudo_filelist:
            self.ListPseudo.addItem(item)
        for item in self.unlabelled_filelist:
            self.ListUnlabel.addItem(item)
        for item in self.labelled_filelist:
            self.ListLabelled.addItem(item)

        if len(self.labelled_filelist) >= 100:
            self.GetNoiseDetected.setEnabled(True)
            self.GetAutoAnnotate.setEnabled(True)
        if len(self.labelled_filelist) >= 1:
            self.GetSetExported.setEnabled(True)
        QtWidgets.QMessageBox.warning(self, "我好了", f"自动标注完成！\n本次共标注{len(confident_tuples)}个样本")
        self.LabelList_Select.setEnabled(True)
        self.NewProject.setEnabled(True)
        self.OpenProject.setEnabled(True)
        self.GetSetMerged.setEnabled(True)

    def open_merge_hint(self):
        self.merge.show()
        self.merge.exec_()

    def get_pseudo_merged(self, do_merge):
        if do_merge:
            self.merge_thread = merge_thread()
            self.merge_thread.signal_returns_finished.connect(self.call_back_merge)
            self.merge_thread.get_args(self.pseudo_csv, self.pseudo_folder,
                                       self.label_csv, self.labelled_folder)
            self.LabelList_Select.setEnabled(False)
            self.Check_Manual_annotate.setEnabled(False)
            self.AnnotateShortcut.setEnabled(False)
            self.GetNoiseDetected.setEnabled(False)
            self.GetAutoAnnotate.setEnabled(False)
            self.NewProject.setEnabled(False)
            self.OpenProject.setEnabled(False)
            self.GetSetMerged.setEnabled(False)
            self.merge_thread.start()
            self.LabelAdvice.setText("正在合并数据集..")
        else:
            pass

    def call_back_merge(self, finished):
        if finished:
            if len(self.labelled_filelist) >= 100:
                self.GetNoiseDetected.setEnabled(True)
                self.GetAutoAnnotate.setEnabled(True)
            if len(self.labelled_filelist) >= 1:
                self.GetSetExported.setEnabled(True)
            self.LabelList_Select.setEnabled(True)
            self.NewProject.setEnabled(True)
            self.OpenProject.setEnabled(True)
            self.GetSetMerged.setEnabled(True)
            self.LabelAdvice.setText("合并完成。")
            self.unlabelled_filelist = glob.glob(os.path.join(self.img_folder, '*.jpg')) + \
                                       glob.glob(os.path.join(self.img_folder, '*.bmp')) + \
                                       glob.glob(os.path.join(self.img_folder, '*.png'))
            self.labelled_filelist = glob.glob(os.path.join(self.labelled_folder, '*.jpg')) + \
                                     glob.glob(os.path.join(self.labelled_folder, '*.bmp')) + \
                                     glob.glob(os.path.join(self.labelled_folder, '*.png'))
            self.pseudo_filelist = glob.glob(os.path.join(self.pseudo_folder, '*.jpg')) + \
                                   glob.glob(os.path.join(self.pseudo_folder, '*.bmp')) + \
                                   glob.glob(os.path.join(self.pseudo_folder, '*.png'))
            self.ListPseudo.clear()
            self.ListUnlabel.clear()
            self.ListLabelled.clear()
            for item in self.pseudo_filelist:
                self.ListPseudo.addItem(item)
            for item in self.unlabelled_filelist:
                self.ListUnlabel.addItem(item)
            for item in self.labelled_filelist:
                self.ListLabelled.addItem(item)

            QtWidgets.QMessageBox.warning(self, "我好了", f"合并完成！")

    def get_dataset_exported(self):
        self.export_thread = output_dataset()
        self.export_thread.signal_returns_finished.connect(self.call_back_export)
        self.export_thread.get_args(self.label_csv, self.labelled_folder, self.label_list)
        self.LabelList_Select.setEnabled(False)
        self.Check_Manual_annotate.setEnabled(False)
        self.AnnotateShortcut.setEnabled(False)
        self.GetNoiseDetected.setEnabled(False)
        self.GetAutoAnnotate.setEnabled(False)
        self.NewProject.setEnabled(False)
        self.OpenProject.setEnabled(False)
        self.GetSetMerged.setEnabled(False)
        self.GetSetExported.setEnabled(False)
        self.export_thread.start()
        self.LabelAdvice.setText("正在导出数据集..")

    def call_back_export(self, finished):
        if finished:
            self.LabelAdvice.setText("导出完成。")
            QtWidgets.QMessageBox.warning(self, "我好了", f"导出完成")
        else:
            self.LabelAdvice.setText("导出失败。")
            QtWidgets.QMessageBox.warning(self, "我好了", f"导出失败")
        self.LabelList_Select.setEnabled(True)
        self.NewProject.setEnabled(True)
        self.OpenProject.setEnabled(True)
        self.GetSetMerged.setEnabled(True)
        if len(self.labelled_filelist) >= 100:
            self.GetNoiseDetected.setEnabled(True)
            self.GetAutoAnnotate.setEnabled(True)
        if len(self.labelled_filelist) >= 1:
            self.GetSetExported.setEnabled(True)
