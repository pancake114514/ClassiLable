import torchvision
from torchvision.models import MobileNet_V2_Weights
import torch


def get_model(class_num, parameter_path=None):
    """
    :param class_num: 分类类别
    :param parameter_path: 加载的参数文件
    :returns: 一个模型
    """
    if parameter_path is not None:
        model = torchvision.models.mobilenet_v2()
        for param in model.parameters():
            param.requires_grad = False
        model.classifier[-1] = torch.nn.Linear(model.last_channel, class_num)
        model.load_state_dict(torch.load(parameter_path))
    else:
        model = torchvision.models.mobilenet_v2(weights=MobileNet_V2_Weights.IMAGENET1K_V1)
        for param in model.parameters():
            param.requires_grad = False
        model.classifier[-1] = torch.nn.Linear(model.last_channel, class_num)
    return model
