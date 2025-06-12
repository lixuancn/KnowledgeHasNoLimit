import torch
from torchviz import make_dot
import torch.nn.utils.prune as prune

model = torch.load('../../excluded_folders/AI_Large_Model_Expert_Practical_Course/16_data/transformer_model.pth', map_location=torch.device('cpu'), weights_only=False)

# 打印原模型参数
for name, param in model.named_parameters():
    if param.requires_grad:
        print(name, param.numel())

# 裁剪
linear_layer = model.fc
# 应用无结构剪枝，移除50%的权重
prune.l1_unstructured(linear_layer, name="weight", amount=0.5)
prune.remove(model.fc, 'weight')
torch.save(model.state_dict(), '../../excluded_folders/AI_Large_Model_Expert_Practical_Course/16_data/transformer_model_cur.pth')

# 打印裁剪后的参数
cut_model = torch.load('../../excluded_folders/AI_Large_Model_Expert_Practical_Course/16_data/transformer_model_cur.pth', map_location=torch.device('cpu'), weights_only=False)

# 打印裁剪后模型参数
print("打印裁剪后模型参数")
for name, param in model.named_parameters():
    if param.requires_grad:
        print(name, param.numel())
