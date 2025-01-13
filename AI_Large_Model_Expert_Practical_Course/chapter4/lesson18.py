import torch.nn.init

import lesson16_transformerDecoderModel
from torch import nn

model = lesson16_transformerDecoderModel.TransformerDecoderModel(vocab_size=122, embed_size=512, num_heads=8, hidden_dim=2048, num_layers=6)

# -------自定义初始化策略-------

# 创建一个TransformDecoderLayer实例
decoder_layer = nn.TransformerDecoderLayer(d_model=512, nhead=8)

def custom_init(m):
    if isinstance(m, nn.Linear):
        torch.nn.init.xavier_uniform_(m.weight)
        if m.bias is not None:
            torch.nn.init.constant_(m.bias, 0.0)


decoder_layer.apply(custom_init)

