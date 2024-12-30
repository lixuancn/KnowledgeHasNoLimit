import torch
from torchviz import make_dot

x = torch.randint(100, (50,))  # 假设一个序列长度为1的输入
model = torch.load('../excluded_folders/16_data/transformer_model.pth', map_location=torch.device('cpu'), weights_only=False)
# 设置为评估模式
model.eval()
y = model(x)
dot = make_dot(y.mean(), params=dict(model.named_parameters()), show_attrs=True, show_saved=True)
dot.render(filename="lesson17_net", format='png')
