import os
import csv


def del_from_pseudo(csv_file_name, img_file_name):
    with open(csv_file_name, 'r') as csv_file:
        reader = csv.reader(csv_file)
        csv_data = list(reader)

    # 遍历每一行数据，删除第一列值为img_file_name的行
    updated_csv_data = []
    for row in csv_data:
        if row[0] != os.path.basename(img_file_name):
            updated_csv_data.append(row)

    # 将更新后的csv数据写入csv文件中
    with open(csv_file_name, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(updated_csv_data)
