# 1.加载 MNIST 数据集####
import os
import torch
from torchvision import datasets, transforms
from torch.utils.data import DataLoader

# 图像预处理
transform = transforms.Compose([
    transforms.ToTensor(),  # 转为张量
    transforms.Normalize((0.1307,), (0.3081,))  # 标准化
])

# 获取脚本所在目录的绝对路径
dir = os.path.dirname(os.path.abspath(__file__))

# 定义数据保存路径
data_root = os.path.join(dir, 'data')

# 下载并加载训练集和测试集
train_dataset = datasets.MNIST(root=data_root, train=True, transform=transform, download=True)
test_dataset  = datasets.MNIST(root=data_root, train=False, transform=transform, download=True)

train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
test_loader  = DataLoader(test_dataset, batch_size=1000, shuffle=False)




# 2.定义 CNN 模型####
import torch.nn as nn
import torch.nn.functional as F
class CNN(nn.Module):
    def __init__(self):
        super(CNN, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3)  # 输入1通道，输出32通道
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3)
        self.dropout = nn.Dropout(0.25)
        self.fc1 = nn.Linear(9216, 128)  # 计算公式: 64*(28-2*2)^2 = 9216
        self.fc2 = nn.Linear(128, 10)    # 输出10类
    
    def forward(self, x):
        x = F.relu(self.conv1(x))   # [1,28,28] -> [32,26,26]
        x = F.relu(self.conv2(x))   # -> [64,24,24]
        x = F.max_pool2d(x, 2)      # -> [64,12,12]
        x = self.dropout(x)
        x = x.view(-1, 64 * 12 * 12)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return F.log_softmax(x, dim=1)




# 3.训练模型####
import torch.optim as optim

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = CNN().to(device)
optimizer = optim.Adam(model.parameters(), lr=0.001)


def train(epoch):
    model.train()
    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        output = model(data)
        loss = F.nll_loss(output, target)  # 负对数似然损失
        loss.backward()
        optimizer.step()

        if batch_idx % 100 == 0:
            print(
                f"Train Epoch: {epoch} [{batch_idx * len(data)}/{len(train_loader.dataset)}]  Loss: {loss.item():.6f}")




# 4.测试模型####
def test():
    model.eval()
    test_loss = 0
    correct = 0
    with torch.no_grad():  # 关闭梯度计算
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            test_loss += F.nll_loss(output, target, reduction='sum').item()
            pred = output.argmax(dim=1)
            correct += pred.eq(target).sum().item()

    test_loss /= len(test_loader.dataset)
    acc = 100. * correct / len(test_loader.dataset)
    print(f"Epoch {epoch}: Test Loss: {test_loss:.4f}, Accuracy: {correct}/{len(test_loader.dataset)} ({acc:.2f}%)")
    return acc




# 5.执行训练和测试
import matplotlib.pyplot as plt

EPOCH = 5 # 训练5轮并每轮测试
acc_list_test = []
for epoch in range(1, EPOCH+1):
    train(epoch)
    # if epoch % 10 == 9:  #每训练10轮 测试1次
    acc_test = test()
    acc_list_test.append(acc_test)

plt.plot(acc_list_test)
plt.xlabel('Epoch')
plt.ylabel('Accuracy On TestSet')
# plt.show()
plt.savefig(os.path.join(dir, "Accuracy_plot.png"))
plt.close()

examples = enumerate(test_loader)
batch_idx, (example_data, example_targets) = next(examples)

with torch.no_grad():
    output = model(example_data.to(device))

fig = plt.figure()
for i in range(12):
    plt.subplot(3,4,i+1)
    plt.tight_layout()
    plt.imshow(example_data[i][0], cmap='gray', interpolation='none')
    plt.title(f"Prediction: {output.argmax(dim=1)[i].item()}")
    plt.xticks([])
    plt.yticks([])
# plt.show()
plt.savefig(os.path.join(dir, "Prediction_plot.png"))