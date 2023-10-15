import os
import torch
import glob
import detect.train_with_mobilenet
from detect import define_utils
from detect import define_detect
import cv2
from detect import predict
from detect import define_model
from torch.utils.data import random_split


def interface_advice_label(class_num, filename, param_filename):
    """
    与图形界面的接口，用于给出建议标签，返回一个代表标签的整数
    :param class_num: 类别数
    :param filename: 输入的文件名（全路径）
    :param param_filename: 模型参数的文件名（全路径）
    :return: 代表标签的整数和其概率
    """
    img = cv2.imread(filename)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    model = define_model.get_model(class_num, param_filename)
    class_id, proba = predict.predict_one_img(img, model)
    return class_id, proba


def interface_noise_detect(file_list, label_list, class_num, save_param_path, detect_method, threshold):
    """
    与图形界面的接口，用于噪声检测，返回一个包含噪声文件名的列表
    :param file_list: 文件名（全路径）列表
    :param label_list: 文件对应标签列表
    :param class_num: 类别数
    :param save_param_path: 保存的参数路径
    :param detect_method: 噪声检测的方法
    :param threshold: 阈值
    :return:一个包含噪声文件名的列表LIST
    """
    noise_fname_list = []
    labelled_dataset = define_utils.load_dataset_hard_label(file_list, label_list)
    if detect_method == "use_lowerbound":
        noise_fname_list = define_detect.detect_using_crossval(labelled_dataset, class_num, save_param_path, threshold)
    elif detect_method == "use_cleanlab":
        # do not use threshold
        noise_fname_list = define_detect.detect_using_cleanlab(labelled_dataset, class_num, save_param_path)
    elif detect_method == "use_both":
        noise_fname_list = define_detect.detect_using_both(labelled_dataset, class_num, save_param_path, threshold)
    return noise_fname_list


def interface_auto_annotate(file_list, label_list, unlabelled_file_list, class_num, save_param_path,
                            annotate_method, max_iterations, threshold):
    """
    与图形界面的接口，用于自动标注，返回包含标注了的文件名（全路径）和标签的列表
    :param file_list:有标签的文件列表（全路径）
    :param label_list:有标签的标签列表（对应）
    :param unlabelled_file_list:无标签的文件列表（全路径）
    :param class_num:分类数
    :param save_param_path:模型保存位置
    :param annotate_method:标注法
    :param max_iterations:迭代轮数
    :param threshold: 置信度阈值
    :return: List of (annotated_filename, pseudo_label)
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if annotate_method == 'soft':
        labelled_set = define_utils.load_dataset_soft_label(file_list, label_list, class_num)
    else:
        labelled_set = define_utils.load_dataset_hard_label(file_list, label_list)
    params = os.path.join(save_param_path, 'self_training.pkl')
    # model = get_model.get_model(class_num)
    # model = model.to(device)
    unlabelled_pics, unlabelled_filenames = define_utils.load_unlabelled_set(unlabelled_file_list)
    confident_pics_tuples = []
    now_iter_round = 0
    while now_iter_round < max_iterations \
            and len(unlabelled_pics) > 0 \
            and len(unlabelled_filenames) > 0:
        train_size = int(0.9 * (len(labelled_set)))
        test_size = len(labelled_set) - train_size
        train_set, test_set = random_split(labelled_set, [train_size, test_size])
        model = detect.train_with_mobilenet.use_mobilenet(train_set, test_set, params, class_num,
                                                          (annotate_method == 'soft'))
        i = 0
        while i < len(unlabelled_pics):
            pic = unlabelled_pics[i]
            class_index, softmax_proba, proba = predict.predict_get_softmax_proba(pic, model)
            if proba >= threshold:
                fname = unlabelled_filenames[i]
                confident_pics_tuples.append((fname, class_index))
                unlabelled_pics.pop(i)
                unlabelled_filenames.pop(i)
                if annotate_method == 'soft':
                    labelled_set.add_sample(pic, softmax_proba, fname)
                else:
                    labelled_set.add_sample(pic, class_index, fname)
            else:
                i += 1
        now_iter_round += 1
    return confident_pics_tuples


if __name__ == "__main__":
    path = 'D:\cat_dog_train\labelled'
    file_list = os.listdir(path)
    labelled_file_list = []
    labels = []
    for i in range(len(file_list)):
        label = file_list[i].split('.')[0].split('_')[2]
        labels.append(int(label))  # 参数
        labelled_file_list.append(os.path.join(path, file_list[i]))  # 参数

    save_param_path = 'D:\cat_dog_train\models'
    class_num = 2
    annotate_method = 'soft'
    max_iterations = 2
    threshold = 0.7

    unlabelled_filelist = glob.glob(os.path.join("D:\cat_dog_train", '*.jpg'))

    print(interface_auto_annotate(labelled_file_list, labels, unlabelled_filelist, class_num,
                                  save_param_path, annotate_method, max_iterations, threshold))
