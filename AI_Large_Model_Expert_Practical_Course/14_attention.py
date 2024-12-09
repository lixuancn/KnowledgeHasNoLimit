import torch
import torch.nn.functional as F
# 假设我们已经有了每个词的嵌入向量，这里用简单的随机向量代替真实的词嵌入
# 假设嵌入大小为 4
embed_size = 4
# 输入序列 "我 喜欢 学习 机器 学习" 的嵌入表示
inputs = torch.rand((5, embed_size))
# 假设 "machine" 的查询向量
query_machine = torch.rand((1, embed_size))

def attention(query, keys, values):
    # 计算查询和键的点积，除以根号下的嵌入维度来缩放
    scores = torch.matmul(query, keys.transpose(-2, -1)) / (embed_size ** 0.5)
    # 应用softmax获取注意力权重
    attn_weights = F.softmax(scores, dim=-1)
    # 计算加权和
    output = torch.matmul(attn_weights, values)
    return output, attn_weights

output, attn_weights = attention(query_machine, inputs, inputs)

print("inputs: ", inputs)
print("query machine: ", query_machine)
print("Output Attention: ", output)
print("Attention Weights: ", attn_weights)