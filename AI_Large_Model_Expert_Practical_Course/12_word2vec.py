import jieba
import xml.etree.ElementTree as ET
from gensim.models import Word2Vec

# 微博语料库 http://www.nlpir.org/wordpress/2017/12/03/nlpir%E5%BE%AE%E5%8D%9A%E5%86%85%E5%AE%B9%E8%AF%AD%E6%96%99%E5%BA%93-23%E4%B8%87%E6%9D%A1/
file_path = '12_weibo_content_corpus/data.xml'
tree = ET.parse(file_path)
root = tree.getroot()

# 获取<article>标签的内容
texts = [record.find('article').text for record in root.findall('RECORD')]
print(len(texts))

# 过滤停用词
stop_words = {"的", "了", "在", "是", "我", "有", "和", "就"}
processed_texts = []
for text in texts:
    if text is not None:
        words = jieba.cut(text)
        processed_text = [word for word in words if word not in stop_words]
        processed_texts.append(processed_text)
        # break

# for text in processed_texts:
#     print(text)

# 模型训练
model = Word2Vec(sentences=processed_texts, vector_size=100, window=5, min_count=1, workers=4, sg=1)
model.save('./12_weibo_content_corpus/12_word2vec.model')

# 使用模型
model = Word2Vec.load("./12_weibo_content_corpus/12_word2vec.model")
print(model.wv['科技'])

similar_words = model.wv.most_similar('科技', topn=5)
print(similar_words)

# 评估
result = model.wv.evaluate_word_pairs('12_valid.tsv')
print(result)