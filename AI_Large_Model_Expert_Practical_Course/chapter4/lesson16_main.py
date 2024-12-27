# 导入所需库
import json
import jieba
import torch
import lesson16_transformerDecoderModel

def load_model(model_path):
    # 加载模型到CPU
    model = torch.load(model_path, map_location=torch.device('cpu'), weights_only=False)
    # 设置为评估模式
    model.eval()
    return model


def load_vocab(json_file):
    """从JSON文件中加载词汇表。"""
    # 读取词汇表文件
    with open(json_file, 'r') as f:
        vocab = json.load(f)
    return vocab


def predict(model, initial_seq, max_len=50):
    # 加载数字到单词的映射
    int_to_word = load_vocab('16_data/int_to_word.json')
    # 确保模型处于评估模式
    model.eval()
    # 关闭梯度计算
    with torch.no_grad():
        generated = initial_seq
        # 生成最多max_len个词
        for _ in range(max_len):
            input_tensor = torch.tensor([generated], dtype=torch.long)
            output = model(input_tensor)
            predicted_idx = torch.argmax(output[:, -1], dim=-1).item()
            generated.append(predicted_idx)
            # 如果生成结束标记，则停止生成
            if predicted_idx == len(int_to_word) - 1:
                break
        # 将生成的索引转换为单词
        return [int_to_word[str(idx)] for idx in generated]


def generate(model, input_sentence, max_len=50):
    # 使用jieba分词对输入句子进行分词
    input_words = list(jieba.cut(input_sentence.strip()))
    # 加载单词到数字的映射
    word_to_int = load_vocab('16_data/word_to_int.json')
    # 将单词转换为索引
    input_seq = [word_to_int.get(word, len(word_to_int) - 1) for word in input_words]
    print("input_seq:", input_seq)
    # 生成文本
    generated_text = predict(model, input_seq, max_len)
    print("generated_text:", generated_text)
    # 将生成的单词列表合并为字符串
    return "".join(generated_text)


def main():
    # 定义输入提示
    prompt = "hello"
    # 加载模型
    model = load_model('16_data/transformer_model.pth')
    # 生成文本
    completion = generate(model, prompt)
    # 打印生成的文本
    print("生成文本：", completion)


if __name__ == '__main__':
    # 主函数入口
    main()
