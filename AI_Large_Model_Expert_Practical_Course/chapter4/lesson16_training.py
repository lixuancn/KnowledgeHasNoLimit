from torch import nn
from torch.utils.data import DataLoader
import torch.optim as optim
# 导入必需的库
from torch.utils.data import Dataset
import torch
import jieba
import json
import lesson16_transformerDecoderModel

# 定义TextDataset类，该类继承自PyTorch中的Dataset
class TextDataset(Dataset):
    # 初始化函数，filepath为输入文件路径
    def __init__(self, filepath):
        words = []  # 创建一个空列表来存储所有单词

        # 打开文件并读取每一行
        with open(filepath, 'r') as file:
            for line in file:
                # 使用jieba库进行分词，并去除每行的首尾空白字符
                words.extend(list(jieba.cut(line.strip())))

        # 将所有单词转换为一个集合来去除重复，然后再转回列表形式，形成词汇表
        self.vocab = list(set(words))
        self.vocab_size = len(self.vocab)  # 计算词汇表的大小

        # 创建从单词到整数的映射和从整数到单词的映射
        self.word_to_int = {word: i for i, word in enumerate(self.vocab)}
        self.int_to_word = {i: word for i, word in enumerate(self.vocab)}

        # 将映射关系保存为JSON文件
        with open('../../excluded_folders/AI_Large_Model_Expert_Practical_Course/16_data/word_to_int.json', 'w') as f:
            json.dump(self.word_to_int, f, ensure_ascii=False, indent=4)
        with open('../../excluded_folders/AI_Large_Model_Expert_Practical_Course/16_data/int_to_word.json', 'w') as f:
            json.dump(self.int_to_word, f, ensure_ascii=False, indent=4)

        # 将所有单词转换为对应的整数索引，形成数据列表
        self.data = [self.word_to_int[word] for word in words]
        print("init", self.data)

    # 返回数据集的长度减1，这通常是因为在机器学习中可能需要使用当前数据点预测下一个数据点
    def __len__(self):
        return len(self.data) - 1

    # 根据索引idx返回数据，这里用于返回模型训练时的输入序列和目标输出
    def __getitem__(self, idx):
        # 从数据中提取最多50个整数索引作为输入序列
        input_seq = torch.tensor(self.data[max(0, idx - 50):idx], dtype=torch.long)
        print("idx", idx)
        print("input_seq", input_seq)
        print("input_seq len", len(input_seq))
        # 提取目标输出，即索引位置的单词
        target = torch.tensor(self.data[idx], dtype=torch.long)
        print("target", target)
        return input_seq, target  # 返回一个元组包含输入序列和目标输出

# 模型训练
def training():
    # 加载数据集
    print("加载数据集")
    dataset = TextDataset('../../excluded_folders/AI_Large_Model_Expert_Practical_Course/16_data/wiki_zh_sentence_head10.txt')
    print(dataset.__getitem__(5))

    batch_size=1
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True, drop_last=True)
    # dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True, collate_fn=collate_fn, drop_last=True)

    # 初始化TransformerDecoderModel，设置特定的参数：
    # vocab_size - 数据集中的词汇表大小
    # embed_size - 嵌入层的维度（这里是512）
    # num_heads - 多头注意力机制中的注意力头数（这里是8）
    # hidden_dim - 变换器中前馈网络模型的维度（这里是2048）
    # num_layers - 模型中的层数（这里是6）
    model = lesson16_transformerDecoderModel.TransformerDecoderModel(vocab_size=dataset.vocab_size, embed_size=512, num_heads=8, hidden_dim=2048, num_layers=6)

    # 将模型传送到定义的设备上（例如GPU或CPU），以便进行训练
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    # 初始化优化器，这里使用Adam优化器，并设置学习率
    # model.parameters() - 从模型中获取参数
    # lr - 学习率（这里用变量learning_rate表示）
    learning_rate = 0.001
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    # 初始化损失函数，这里使用交叉熵损失，适用于分类问题
    criterion = nn.CrossEntropyLoss()
    # 将模型设置为训练模式
    model.train()

    # 循环遍历所有的训练周期
    print("遍历训练周期")
    num_epochs = 1  # 训练轮数
    for epoch in range(num_epochs):
        # 循环遍历数据加载器中的每个批次
        for i, (inputs, targets) in enumerate(dataloader):
            print("i: ", i)
            print("inputs: ", inputs)
            print("targets: ", targets)
            # 将输入数据转置，以符合模型的期望输入维度
            inputs = inputs.t()
            # 在每次迭代前清空梯度
            optimizer.zero_grad()
            # 前向传播：计算模型对当前批次的输出
            outputs = model(inputs)
            print("outputs", outputs)
            print("outputs len", len(outputs))
            # 选择输出的最后一个元素进行损失计算
            if len(outputs) > 1:
                outputs = outputs[-1]
                # 计算损失值
                loss = criterion(outputs, targets)
                # 反向传播：计算损失的梯度
                loss.backward()
                # 更新模型的参数
                optimizer.step()
            # 每隔50步打印一次当前的训练状态
            if i % 50 == 0:
                print(f'Epoch [{epoch + 1}/{num_epochs}], Step [{i + 1}/{len(dataloader)}], Loss: {loss.item()}')

    # 保存模型到指定路径
    model_path = "../../excluded_folders/AI_Large_Model_Expert_Practical_Course/16_data/transformer_model.pth"
    torch.save(model, model_path)
    print('模型（保存权重和架构（模型的结构））已保存到', model_path)

    model_path = "../../excluded_folders/AI_Large_Model_Expert_Practical_Course/16_data/transformer_model_state_dict.pth"
    torch.save(model.state_dict(), model_path)
    print('模型（只保存权重）已保存到', model_path)

training()
