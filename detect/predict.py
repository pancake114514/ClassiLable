import torch
import torch.nn.functional as F
from detect import define_utils

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def predict_one_img(img, eval_model):
    img = define_utils.mobile_net_transform(img)
    img = img.unsqueeze(0)
    img = img.to(device)
    eval_model = eval_model.to(device)
    with torch.no_grad():
        eval_model.eval()
        outputs = eval_model(img)
        out = F.softmax(outputs, dim=1)
        proba, class_ind = torch.max(out, 1)
        proba = float(proba)
        class_ind = int(class_ind)
        return class_ind, proba


def predict_get_softmax_proba(img, eval_model):
    img = define_utils.mobile_net_transform(img)
    img = img.unsqueeze(0)
    img = img.to(device)
    with torch.no_grad():
        eval_model.eval()
        outputs = eval_model(img)
        out = F.softmax(outputs, dim=1)
        proba, class_ind = torch.max(out, 1)
        class_ind = int(class_ind)
        out_softmax = out.tolist()
        return class_ind, out_softmax[0], proba
