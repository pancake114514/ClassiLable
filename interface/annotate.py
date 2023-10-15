import os
import csv


def manual_annotate(csv_file_name, img_file_name, label):
    found = False
    with open(csv_file_name, 'r', newline='') as csv_file:
        reader = csv.reader(csv_file)
        rows = [row for row in reader]
        num_rows = len(rows)
        for i in range(num_rows):
            if rows[i][0] == os.path.basename(img_file_name):
                print(f'found! Old label = {rows[i][1]}')
                rows[i][1] = int(label)
                print(f'new label = {label}')
                found = True
                break

    with open(csv_file_name, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        if not found:
            # The row is not found, do something
            # writer.writerows()
            print('not found, append')
            rows.append([os.path.basename(img_file_name), int(label)])
        writer.writerows(rows)
