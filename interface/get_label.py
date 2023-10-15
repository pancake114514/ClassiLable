import os
import csv
import glob


def get_label(csv_file_name, img_file_name):
    found = False
    old_label = -1
    with open(csv_file_name, 'r', newline='') as csv_file:
        reader = csv.reader(csv_file)
        rows = [row for row in reader]
        num_rows = len(rows)
        for i in range(num_rows):
            if rows[i][0] == os.path.basename(img_file_name):
                old_label = rows[i][1]
                found = True
                break
    return found, int(old_label)


def get_all_labels(csv_file_name, labelled_file_path):
    file_names = []
    labels = []
    filename_list = glob.glob(os.path.join(labelled_file_path, '*.jpg')) + \
                    glob.glob(os.path.join(labelled_file_path, '*.bmp')) + \
                    glob.glob(os.path.join(labelled_file_path, '*.png'))

    for filename in filename_list:
        full_name = filename
        file_names.append(full_name)
        labels.append(get_label(csv_file_name, full_name)[1])
    return file_names, labels

# if __name__ == "__main__":
#     c = "D:\cat_dog\labels.csv"
#     lab = "D:\cat_dog\labelled"
#     fnames, labels = get_all_labels(c, lab)
#     for i in range(len(fnames)):
#         print(f"Label={labels[i]},fname={fnames[i]}")
