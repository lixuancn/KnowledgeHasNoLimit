import torch
from torch.utils.data import Dataset, DataLoader
import spacy
import jieba
from collections import Counter
from torch.nn.utils.rnn import pad_sequence
import torch.nn as nn
import random
import torch.optim as optim

# 加载英文的Spacy模型
spacy_en = spacy.load('en_core_web_sm')

def tokenize_en(text):
    """
    Tokenizes English text from a string into a list of strings (tokens)
    """
    return [tok.text for tok in spacy_en.tokenizer(text)]

def tokenize_cn(text):
    """
    Tokenizes Chinese text from a string into a list of strings (tokens)
    """
    return list(jieba.cut(text))

def build_vocab(sentences, tokenizer, max_size, min_freq):
    token_freqs = Counter()
    for sentence in sentences:
        tokens = tokenizer(sentence)
        token_freqs.update(tokens)
    vocab = {token: idx + 4 for idx, (token, freq) in enumerate(token_freqs.items()) if freq >= min_freq}
    vocab['<unk>'] = 0
    vocab['<pad>'] = 1
    vocab['<sos>'] = 2
    vocab['<eos>'] = 3
    return vocab

class TranslationDataset(Dataset):
    def __init__(self, src_sentences, trg_sentences, src_vocab, trg_vocab, tokenize_src, tokenize_trg):
        self.src_sentences = src_sentences
        self.trg_sentences = trg_sentences
        self.src_vocab = src_vocab
        self.trg_vocab = trg_vocab
        self.tokenize_src = tokenize_src
        self.tokenize_trg = tokenize_trg
    def __len__(self):
        return len(self.src_sentences)
    def __getitem__(self, idx):
        src_sentence = self.src_sentences[idx]
        trg_sentence = self.trg_sentences[idx]
        src_indices = [self.src_vocab[token] if token in self.src_vocab else self.src_vocab['<unk>']
                       for token in ['<sos>'] + self.tokenize_src(src_sentence) + ['<eos>']]
        trg_indices = [self.trg_vocab[token] if token in self.trg_vocab else self.trg_vocab['<unk>']
                       for token in ['<sos>'] + self.tokenize_trg(trg_sentence) + ['<eos>']]
        return torch.tensor(src_indices), torch.tensor(trg_indices)

def collate_fn(batch):
    src_batch, trg_batch = zip(*batch)
    src_batch = pad_sequence(src_batch, padding_value=1)  # 1 is the index for <pad>
    trg_batch = pad_sequence(trg_batch, padding_value=1)  # 1 is the index for <pad>
    return src_batch, trg_batch

class Encoder(nn.Module):
    def __init__(self, input_dim, emb_dim, hid_dim, n_layers, dropout):
        super().__init__()
        self.embedding = nn.Embedding(input_dim, emb_dim)
        self.rnn = nn.GRU(emb_dim, hid_dim, n_layers, dropout=dropout)
        self.dropout = nn.Dropout(dropout)
    def forward(self, src):
        # src: [src_len, batch_size]
        embedded = self.dropout(self.embedding(src))
        outputs, hidden = self.rnn(embedded)
        return hidden

class Decoder(nn.Module):
    def __init__(self, output_dim, emb_dim, hid_dim, n_layers, dropout):
        super().__init__()
        self.output_dim = output_dim
        self.embedding = nn.Embedding(output_dim, emb_dim)
        self.rnn = nn.GRU(emb_dim, hid_dim, n_layers, dropout=dropout)
        self.fc_out = nn.Linear(hid_dim, output_dim)
        self.dropout = nn.Dropout(dropout)
    def forward(self, input, hidden):
        input = input.unsqueeze(0)  # input: [1, batch_size]
        embedded = self.dropout(self.embedding(input))
        output, hidden = self.rnn(embedded, hidden)
        prediction = self.fc_out(output.squeeze(0))
        return prediction, hidden

class Seq2Seq(nn.Module):
    def __init__(self, encoder, decoder, device):
        super().__init__()
        self.encoder = encoder
        self.decoder = decoder
        self.device = device
    def forward(self, src, trg, teacher_forcing_ratio=0.5):
        # src: [src_len, batch_size]
        # trg: [trg_len, batch_size]
        # teacher_forcing_ratio是使用真实标签的概率
        trg_len = trg.shape[0]
        batch_size = trg.shape[1]
        trg_vocab_size = self.decoder.output_dim
        # 存储解码器输出
        outputs = torch.zeros(trg_len, batch_size, trg_vocab_size).to(self.device)
        # 编码器的最后一个隐藏状态用作解码器的初始隐藏状态
        hidden = self.encoder(src)
        # 解码器的第一个输入是<sos> tokens
        input = trg[0, :]
        for t in range(1, trg_len):
            output, hidden = self.decoder(input, hidden)
            outputs[t] = output
            # 决定是否使用teacher forcing
            teacher_force = random.random() < teacher_forcing_ratio
            top1 = output.argmax(1)
            input = trg[t] if teacher_force else top1
        return outputs

cn_sentences = []
zh_file_path = "13_data/train_1w.zh"
# 使用Python的文件操作逐行读取文件，并将每一行的内容添加到列表中
with open(zh_file_path, "r", encoding="utf-8") as file:
    for line in file:
        # 去除行末的换行符并添加到列表中
        cn_sentences.append(line.strip())
en_sentences = []
en_file_path = "13_data/train_1w.en"
# 使用Python的文件操作逐行读取文件，并将每一行的内容添加到列表中
with open(en_file_path, "r", encoding="utf-8") as file:
    for line in file:
        # 去除行末的换行符并添加到列表中
        en_sentences.append(line.strip())
# cn_sentences 和 en_sentences 分别包含了所有的中文和英文句子
cn_vocab = build_vocab(cn_sentences, tokenize_cn, max_size=10000, min_freq=2)
en_vocab = build_vocab(en_sentences, tokenize_en, max_size=10000, min_freq=2)

# cn_vocab 和 en_vocab 是已经创建的词汇表
dataset = TranslationDataset(cn_sentences, en_sentences, cn_vocab, en_vocab, tokenize_cn, tokenize_en)
train_loader = DataLoader(dataset, batch_size=32, collate_fn=collate_fn)
# 检查是否有可用的GPU，如果没有，则使用CPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("训练设备为：", device)
# 定义一些超参数
INPUT_DIM = 10000  # 输入语言的词汇量
OUTPUT_DIM = 10000  # 输出语言的词汇量
ENC_EMB_DIM = 256  # 编码器嵌入层大小
DEC_EMB_DIM = 256  # 解码器嵌入层大小
HID_DIM = 512  # 隐藏层维度
N_LAYERS = 2  # RNN层的数量
ENC_DROPOUT = 0.5  # 编码器中dropout的比例
DEC_DROPOUT = 0.5  # 解码器中dropout的比例
enc = Encoder(INPUT_DIM, ENC_EMB_DIM, HID_DIM, N_LAYERS, ENC_DROPOUT)
dec = Decoder(OUTPUT_DIM, DEC_EMB_DIM, HID_DIM, N_LAYERS, DEC_DROPOUT)
model = Seq2Seq(enc, dec, device).to(device)
# 假定模型已经被实例化并移到了正确的设备上
model.to(device)
# 定义优化器和损失函数
optimizer = optim.Adam(model.parameters())
criterion = nn.CrossEntropyLoss(ignore_index=en_vocab['<pad>'])  # 忽略<pad>标记的损失
num_epochs = 10  # 训练轮数
for epoch in range(num_epochs):
    model.train()
    total_loss = 0
    for src, trg in train_loader:
        src, trg = src.to(device), trg.to(device)
        optimizer.zero_grad()  # 清空梯度
        output = model(src, trg[:-1])  # 输入给模型的是除了最后一个词的目标句子
        # Reshape输出以匹配损失函数期望的输入
        output_dim = output.shape[-1]
        output = output.view(-1, output_dim)
        trg = trg[1:].view(-1)  # 从第一个词开始的目标句子
        loss = criterion(output, trg)
        loss.backward()  # 反向传播
        optimizer.step()  # 更新参数
        total_loss += loss.item()
    avg_loss = total_loss / len(train_loader)
    print(f'Epoch {epoch + 1}/{num_epochs}, Average Loss: {avg_loss}')
    # 可以在这里添加验证步骤

def translate_sentence(sentence, src_vocab, trg_vocab, model, device, max_len=50):
    # 将输入句子进行分词并转换为索引序列
    src_tokens = ['<sos>'] + tokenize_cn(sentence) + ['<eos>']
    src_indices = [src_vocab[token] if token in src_vocab else src_vocab['<unk>'] for token in src_tokens]
    # 将输入句子转换为张量并移动到设备上
    src_tensor = torch.LongTensor(src_indices).unsqueeze(1).to(device)
    # 将输入句子传递给编码器以获取上下文张量
    with torch.no_grad():
        encoder_hidden = model.encoder(src_tensor)
    # 初始化解码器输入为<sos>
    trg_token = '<sos>'
    trg_index = trg_vocab[trg_token]
    # 存储翻译结果
    translation = []
    # 解码过程
    for _ in range(max_len):
        # 将解码器输入传递给解码器，并获取输出和隐藏状态
        with torch.no_grad():
            trg_tensor = torch.LongTensor([trg_index]).to(device)
            output, encoder_hidden = model.decoder(trg_tensor, encoder_hidden)
        # 获取解码器输出中概率最高的单词的索引
        pred_token_index = output.argmax(dim=1).item()
        # 如果预测的单词是句子结束符，则停止解码
        if pred_token_index == trg_vocab['<eos>']:
            break
        # 否则，将预测的单词添加到翻译结果中
        pred_token = list(trg_vocab.keys())[list(trg_vocab.values()).index(pred_token_index)]
        translation.append(pred_token)
        # 更新解码器输入为当前预测的单词
        trg_index = pred_token_index
    # 将翻译结果转换为字符串并返回
    translation = ' '.join(translation)
    return translation

sentence = "我喜欢学习机器学习。"
translation = translate_sentence(sentence, cn_vocab, en_vocab, model, device)
print(f"Chinese: {sentence}")
print(f"Translation: {translation}")
