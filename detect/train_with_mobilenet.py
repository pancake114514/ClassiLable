from detect import define_model
import torch
from torch.optim.lr_scheduler import StepLR


def get_soft_tensor(labels, batchsize):
    label_list = []
    for i in range(batchsize):
        lst = []
        for ts in labels:
            lst.append(ts[i].item())
        # lst = torch.tensor(lst)
        label_list.append(lst)
        # print(lst)
    label_list = torch.tensor(label_list, dtype=torch.float32)
    return label_list


def use_mobilenet(train_set, test_set, output_param_path, num_classes, use_soft_label=False, input_parameter_path=None):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    train_loader = torch.utils.data.DataLoader(dataset=train_set, batch_size=64, shuffle=True)
    test_loader = torch.utils.data.DataLoader(dataset=test_set, batch_size=64, shuffle=False)
    model = define_model.get_model(num_classes, input_parameter_path)
    # 定义损失函数和优化器
    if not use_soft_label:
        # 使用硬标签
        model = model.to(device)
        criterion = torch.nn.CrossEntropyLoss()
        optimizer = torch.optim.SGD(model.classifier.parameters(), lr=0.005, momentum=0.9)
        scheduler = StepLR(optimizer, step_size=3, gamma=0.2)
        epochs = 10
        for epoch in range(epochs):
            model.train()
            for images, labels, fname in train_loader:
                # Move tensors to the configured device
                images = images.to(device)
                labels = labels.to(device)
                outputs = model(images)
                loss = criterion(outputs, labels)
                # Backward and optimize
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                print('Epoch [{}/{}], Loss: {:.4f}'.format(epoch + 1, epochs, loss.item()))
            scheduler.step()
            # 测试准确率
            with torch.no_grad():
                model.eval()
                correct = 0
                total = 0
                for data in test_loader:
                    images, labels, fname = data
                    images = images.to(device)
                    labels = labels.to(device)
                    outputs = model(images)
                    _, predicted = torch.max(outputs.data, 1)
                    total += labels.size(0)
                    correct += (predicted == labels).sum().item()
                    new_accuracy = 100 * correct / total
                print('Accuracy: {} %'.format(new_accuracy))
        print(output_param_path)
        torch.save(model.state_dict(), output_param_path)
    else:
        model = model.to(device)
        criterion = torch.nn.CrossEntropyLoss()
        optimizer = torch.optim.SGD(model.classifier.parameters(), lr=0.005, momentum=0.9)
        scheduler = StepLR(optimizer, step_size=3, gamma=0.2)
        epochs = 10
        for epoch in range(epochs):
            model.train()
            for images, labels, fname in train_loader:
                # Move tensors to the configured device
                images = images.to(device)
                this_batchsize = len(labels[0])
                label_list = get_soft_tensor(labels, this_batchsize)
                label_list = label_list.to(device)
                # Forward pass
                outputs = model(images)
                loss = criterion(outputs, label_list)
                # Backward and optimize
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                print('Epoch [{}/{}], Loss: {:.4f}'.format(epoch + 1, epochs, loss.item()))
            scheduler.step()
            # Test the model
            with torch.no_grad():
                model.eval()
                correct = 0
                total = 0
                for data in test_loader:
                    images, labels, fname = data
                    images = images.to(device)
                    test_size = len(labels[0])
                    labels = get_soft_tensor(labels, test_size)
                    labels_scalar = []
                    for i in range(test_size):
                        labels_scalar.append(torch.argmax(labels[i]).item())
                    labels_scalar = torch.tensor(labels_scalar, dtype=torch.float32).to(device)
                    outputs = model(images)
                    _, predicted = torch.max(outputs.data, 1)
                    total += labels.size(0)
                    correct += (predicted == labels_scalar).sum().item()
                    new_accuracy = 100 * correct / total
                print('Accuracy: {} %'.format(new_accuracy))
        torch.save(model.state_dict(), output_param_path)
    return model
