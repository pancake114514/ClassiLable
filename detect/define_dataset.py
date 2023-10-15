import copy

from torch.utils.data import Dataset
import torch
from torchvision.transforms.functional import to_tensor,  hflip, rotate
import numpy as np


class FDataset(Dataset):
    def __init__(self, pics, labels, filenames=None, transform=None):
        self.pics = pics
        self.labels = labels
        self.filenames = filenames
        self.transform = transform

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        label = self.labels[idx]
        pic = copy.deepcopy(self.pics[idx])
        if self.transform is not None:
            pic = self.transform(pic)
        if self.filenames is not None:
            filename = self.filenames[idx]
        # check transforms
        return pic, label, filename

    def enhance(self, image, angle):
        if torch.rand(1) < 0.5:
            image = hflip(to_tensor(image))
        else:
            image = to_tensor(image)
        rotate_angle = torch.randint(-1 * int(angle), int(angle), (1,))
        image = rotate(image, int(rotate_angle))
        image = image.numpy()
        image = np.transpose(image, (1, 2, 0))
        return image

    def add_sample(self, pic, label, fname, use_enhance=False):
        if use_enhance:
            pic = self.enhance(pic, 15)
        self.pics.append(pic)
        self.labels.append(label)
        self.filenames.append(fname)
