from torch.utils.data import random_split
import torch.utils.data
from sklearn.model_selection import KFold
import os
import numpy as np
from detect import train_with_mobilenet
import torch.nn.functional as F
import torch
from cleanlab.filter import find_label_issues

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def detect_using_crossval(dataset, output_classes, save_param_path, threshold):
    # 保存文件名
    detected_filenames = []
    for train_indices, test_parts in KFold(n_splits=4).split(dataset):
        to_filter = torch.utils.data.Subset(dataset, test_parts)
        train_set = torch.utils.data.Subset(dataset, train_indices)
        train_size = int(0.9 * len(train_set))
        test_size = len(train_set) - train_size
        train_set, test_set = torch.utils.data.random_split(train_set, [train_size, test_size])
        params = os.path.join(save_param_path, 'validation.pkl')
        new_model = train_with_mobilenet.use_mobilenet(train_set, test_set, params, output_classes)
        with torch.no_grad():
            new_model.eval()
            for img, label, fname in to_filter:
                img = img.unsqueeze(0)
                img = img.to(device)
                out = new_model(img)
                out = F.softmax(out, dim=1)
                out_probabs = np.array(out.detach().cpu().numpy())
                old_label_probab = out_probabs[0][label]
                if old_label_probab <= threshold:
                    detected_filenames.append(fname)
    detected_filenames.sort()
    return detected_filenames


def detect_using_cleanlab(dataset, output_classes, save_param_path):
    detected_filenames = []
    # 保存交叉验证产生的out-of-sample预测概率
    list_pred_probabs = []
    list_label = []
    list_filenames = []
    for train_indices, test_parts in KFold(n_splits=4).split(dataset):
        to_filter = torch.utils.data.Subset(dataset, test_parts)
        train_set = torch.utils.data.Subset(dataset, train_indices)
        train_size = int(0.9 * len(train_set))
        test_size = len(train_set) - train_size
        train_set, test_set = torch.utils.data.random_split(train_set, [train_size, test_size])
        params = os.path.join(save_param_path, 'validation.pkl')
        new_model = train_with_mobilenet.use_mobilenet(train_set, test_set, params, output_classes)
        with torch.no_grad():
            new_model.eval()
            for img, label, fname in to_filter:
                img = img.unsqueeze(0)
                img = img.to(device)
                out = new_model(img)
                out = F.softmax(out, dim=1)
                out = np.array(out.detach().cpu().numpy())
                list_filenames.append(fname)
                list_label.append(label)
                list_pred_probabs.append(out[0])

    np_pred_probabs = np.vstack(list_pred_probabs)

    # Reshape 2D numpy array to desired shape
    N = len(list_pred_probabs)
    K = list_pred_probabs[0].shape[0]
    np_pred_probabs = np_pred_probabs.reshape((N, K))
    label_issues = find_label_issues(labels=list_label, pred_probs=np_pred_probabs,
                                     return_indices_ranked_by='self_confidence', filter_by='confident_learning')
    for idx in label_issues:
        detected_filenames.append(list_filenames[idx])
    detected_filenames.sort()
    return detected_filenames


def detect_using_both(dataset, output_classes, save_param_path, threshold):
    noise_fname_crossval = []
    # 保存文件名
    list_filenames = []
    # 保存交叉验证产生的out-of-sample预测概率
    list_pred_probabs = []
    list_label = []
    lowerbound_detected = 0
    for train_indices, test_parts in KFold(n_splits=4).split(dataset):
        to_filter = torch.utils.data.Subset(dataset, test_parts)
        train_set = torch.utils.data.Subset(dataset, train_indices)
        train_size = int(0.9 * len(train_set))
        test_size = len(train_set) - train_size
        train_set, test_set = torch.utils.data.random_split(train_set, [train_size, test_size])
        params = os.path.join(save_param_path, 'validation.pkl')
        new_model = train_with_mobilenet.use_mobilenet(train_set, test_set, params, output_classes)
        with torch.no_grad():
            new_model.eval()
            for img, label, fname in to_filter:
                img = img.unsqueeze(0)
                img = img.to(device)
                out = new_model(img)
                out = F.softmax(out, dim=1)

                # 用于CL
                out_cl = np.array(out.detach().cpu().numpy())
                list_filenames.append(fname)
                list_label.append(label)
                list_pred_probabs.append(out_cl[0])

                # 查原标签的softmax概率
                old_label_probab = out[0][label]
                if old_label_probab <= threshold:
                    lowerbound_detected += 1
                    noise_fname_crossval.append(fname)

    np_pred_probabs = np.vstack(list_pred_probabs)

    # Reshape 2D numpy array to desired shape
    N = len(list_pred_probabs)
    K = list_pred_probabs[0].shape[0]
    np_pred_probabs = np_pred_probabs.reshape((N, K))
    label_issues = find_label_issues(labels=list_label, pred_probs=np_pred_probabs,
                                     return_indices_ranked_by='self_confidence', filter_by='confident_learning')
    noise_fname_cleanlab = []
    for idx in label_issues:
        noise_fname_cleanlab.append(list_filenames[idx])

    detected_filenames = list(set(noise_fname_cleanlab) & set(noise_fname_crossval))
    detected_filenames.sort()
    return detected_filenames
