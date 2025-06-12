import torch
import torch.nn as nn
import torch.quantization
import lesson16_transformerDecoderModel

# 静态量化
model = lesson16_transformerDecoderModel.TransformerDecoderModel(vocab_size=1000, embed_size=512, num_heads=8, hidden_dim=2048, num_layers=6)
model.eval()
model_fp32_prepared = torch.quantization.prepare(model)

# 模型校准过程
# 运行一些输入数据来校准模型
for input_batch in calibration_dataset:
    model_fp32_prepared(input_batch)

# 转换模型为量化版本
model_int8 = torch.quantization.convert(model_fp32_prepared)

# 保存
torch.save(model_int8.state_dict(), '../../excluded_folders/AI_Large_Model_Expert_Practical_Course/16_data/transformer_model_quantization_int8.pth')


# 动态量化
# 这里指定了量化nn.Linear和nn.LSTM层，使用8-bit的量化整数（torch.qint8）
quantized_model = quantize_dynamic(
    model,
    {nn.Linear}, # 指定量化的层类型
    dtype=torch.qint8 # 指定量化的数据类型
)
torch.save(model_int8.state_dict(), '../../excluded_folders/AI_Large_Model_Expert_Practical_Course/16_data/transformer_model_quantization_dynamic.pth')