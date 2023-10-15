import csv
import os
import cv2
from detect.define_dataset import FDataset
from torchvision import transforms

mobile_net_transform = transforms.Compose([
    transforms.ToTensor(),  # 转化为tensor类型
    # 从[0,1]归一化到[-1,1]
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    # transforms.RandomHorizontalFlip(),  # 随机水平镜像
    transforms.Resize([224, 224])
])


def load_dataset_soft_label(labelled_filename, labels, types):
    """
        用于构建软标签，软标签为一个长度为types的列表，其中为独热编码的label，即第label项为1，其他项目为0
        在加载初始标签的时候可以使用独热编码标签，后来训练时输出的伪标签需要作softmax使其和为1
        参数列表：
        :param labelled_filename: 输入的已标签图片所在路径
        :param labels：输入的标签（转化为软标签）
        :param types: 类别数
        :returns: 带软标签的dataset类数据集
    """
    pics = []
    added_filenames = []
    soft_labels = []
    length = len(labelled_filename)
    for i in range(length):
        label = int(labels[i])
        filename = labelled_filename[i]
        lst = [0.0] * types
        # 将label项设为1.0
        lst[label] = 1.0
        # print(lst)
        try:
            pic = cv2.imread(filename)
            b, g, r = cv2.split(pic)
            pic = cv2.merge([r, g, b])
            pics.append(pic)
            soft_labels.append(lst)
            added_filenames.append(filename)
        except ValueError as errorMsg:
            print(filename)
            print(errorMsg)
    labelled_set = FDataset(pics, soft_labels, filenames=added_filenames, transform=mobile_net_transform)
    return labelled_set


def load_dataset_hard_label(labelled_filename, labels):
    """
        使用硬标签时的加载方式
        参数列表：
        :param labelled_filename: 输入的已标签图片（全路径）
        :param labels：输入的标签
        :returns : 带硬标签的dataset类数据集
    """
    added_filenames = []
    pics = []
    hard_labels = []
    length = len(labelled_filename)
    for i in range(length):
        label = int(labels[i])
        filename = labelled_filename[i]
        try:
            pic = cv2.imread(filename)
            b, g, r = cv2.split(pic)
            pic = cv2.merge([r, g, b])
            pics.append(pic)
            hard_labels.append(label)
            added_filenames.append(filename)
        except ValueError as errorMsg:
            print(filename)
            print(errorMsg)
    labelled_set = FDataset(pics, labels, filenames=added_filenames, transform=mobile_net_transform)
    return labelled_set


def load_unlabelled_set(unlabelled_filenames):
    """
        加载未标签图像
        参数列表：
        :param unlabelled_filenames: 输入的无标签图片列表（全路径）
        :returns: 保存图片和文件名的列表
    """
    pics = []
    loaded_filenames = []
    length = len(unlabelled_filenames)
    for i in range(length):
        try:
            filename = unlabelled_filenames[i]
            pic = cv2.imread(filename)
            b, g, r = cv2.split(pic)
            pic = cv2.merge([r, g, b])
            pics.append(pic)
            loaded_filenames.append(filename)
        except ValueError as errorMsg:
            print(errorMsg)
    return pics, loaded_filenames
