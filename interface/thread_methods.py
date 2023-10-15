import csv
from PyQt5 import QtCore
from detect import ui_interface
import get_label
import annotate
import os
import tarfile


class annotate_thread(QtCore.QThread):
    signal_returns_tuples = QtCore.pyqtSignal(list)

    def __init__(self):
        super(annotate_thread, self).__init__()

    def __del__(self):
        self.wait()

    def get_args(self, labelled_fnames, labels, unlabelled_fnames, class_num,
                 model_folder, method, iter_rounds, threshold):
        self.labelled_fnames = labelled_fnames
        self.labels = labels
        self.unlabelled_fnames = unlabelled_fnames
        self.class_num = class_num
        self.model_folder = model_folder
        self.method = method
        self.iter_rounds = iter_rounds
        self.threshold = threshold

    def run(self):
        confident_tuples = ui_interface.interface_auto_annotate(self.labelled_fnames, self.labels,
                                                                self.unlabelled_fnames, self.class_num,
                                                                self.model_folder, self.method,
                                                                self.iter_rounds, self.threshold)
        self.signal_returns_tuples.emit(confident_tuples)


class detect_thread(QtCore.QThread):
    signal_returns_noise_fnames = QtCore.pyqtSignal(list)

    def __init__(self):
        super(detect_thread, self).__init__()

    def __del__(self):
        self.wait()

    def get_args(self, list_fname, list_label, class_num, model_path, detect_method, threshold):
        self.list_fname = list_fname
        self.list_label = list_label
        self.class_num = class_num
        self.model_path = model_path
        self.detect_method = detect_method
        self.threshold = threshold

    def run(self):
        noise_fnames = ui_interface.interface_noise_detect(self.list_fname, self.list_label,
                                                           self.class_num, self.model_path,
                                                           self.detect_method, self.threshold)
        self.signal_returns_noise_fnames.emit(noise_fnames)


class merge_thread(QtCore.QThread):
    signal_returns_finished = QtCore.pyqtSignal(bool)

    def __init__(self):
        super(merge_thread, self).__init__()

    def __del__(self):
        self.wait()

    def get_args(self, pseudo_csv, pseudo_folder, labelled_csv, labelled_folder):
        self.pseudo_csv = pseudo_csv
        self.pseudo_folder = pseudo_folder
        self.labelled_csv = labelled_csv
        self.labelled_folder = labelled_folder

    def run(self):
        fnames, labels = get_label.get_all_labels(self.pseudo_csv, self.pseudo_folder)
        with open(self.pseudo_csv, 'w', newline='') as csvfile:
            csvfile.write('')
        for i in range(len(fnames)):
            annotate.manual_annotate(self.labelled_csv, fnames[i], labels[i])
            os.rename(fnames[i], os.path.join(self.labelled_folder, os.path.basename(fnames[i])))
        self.signal_returns_finished.emit(True)


class output_dataset(QtCore.QThread):
    signal_returns_finished = QtCore.pyqtSignal(bool)

    def __init__(self):
        super(output_dataset, self).__init__()

    def __del__(self):
        self.wait()

    def get_args(self, labelled_csv, labelled_folder, label_list):
        self.labelled_csv = labelled_csv
        self.labelled_folder = labelled_folder
        self.label_list = label_list

    def run(self):
        try:
            fnames, labels = get_label.get_all_labels(self.labelled_csv, self.labelled_folder)
            path = os.path.join(self.labelled_folder, 'dataset_labels.csv')
            with open(path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                for fname, label in zip(fnames, labels):
                    writer.writerow([os.path.basename(fname), int(label)])
            fnames.append(path)
            path2 = os.path.join(self.labelled_folder, 'labels_id.txt')
            with open(path2, 'w') as file:
                for i in range(len(self.label_list)):
                    file.write(f'{i}\t{self.label_list[i]}\n')
            fnames.append(path2)
            tar = tarfile.open(os.path.join(self.labelled_folder, 'output.tar'), 'w')
            for file in fnames:
                tar.add(file)
            tar.close()
            if os.path.isfile(path):
                os.remove(path)
            if os.path.isfile(path2):
                os.remove(path2)
            self.signal_returns_finished.emit(True)
        except Exception as e:
            print("Error occurred:", str(e))
            self.signal_returns_finished.emit(False)
