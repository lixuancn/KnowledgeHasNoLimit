import torch
import torch.nn as nn
import torch.optim as optim
import torch.quantization
import lesson16_transformerDecoderModel
from torch.utils.data import DataLoader

# 知识蒸馏
teacher_model = torch.load('../../excluded_folders/AI_Large_Model_Expert_Practical_Course/16_data/transformer_model.pth', map_location=torch.device('cpu'), weights_only=False)
teacher_model.eval()

# 定义学生模型
student_model = lesson16_transformerDecoderModel.TransformerDecoderModel(vocab_size=1000, embed_size=512, num_heads=8, hidden_dim=2048, num_layers=6)

# 损失函数和优化器
criterion = nn.MSELoss()
optimizer = optim.Adam(student_model.parameters(), lr=0.001)

# 数据加载器
train_loader = DataLoader(dataset, batch_size=batch_size, shuffle=True, drop_last=True)

# 蒸馏的构成
for epoch in range(num_epochs):
    student_model.train()
    for data, target in train_loader:
        optimizer.zero_grad()

        # 教师模型的输出
        with torch.no_grad():
            teacher_output = teacher_model(data)

        # 学生模型的输出
        student_output = student_model(data)
        # 计算损失：根据需要混合教师输出和真实标签
        loss = criterion(student_output, teacher_output) # 以教师模型的输出为目标
        # 反向传播和优化
        loss.backward()
        optimizer.step()

# 评估学生模型性能
student_model.eval()
