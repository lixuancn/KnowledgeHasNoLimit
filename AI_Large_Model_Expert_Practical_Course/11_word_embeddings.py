from nltk.tokenize import word_tokenize
from gensim.models import Word2Vec

# 定义训练语料
sentences = [ "The cat sat on the mat.", "Dogs and cats are enemies.", "The dog chased the cat."]
# 分词
tokenize_sentences = [word_tokenize(sentence.lower()) for sentence in sentences]
print(tokenize_sentences)
# 训练Word2Vec模型
model = Word2Vec(sentences=tokenize_sentences, vector_size=100, window=5, min_count=1, workers=4)
# 向量
cat_vector = model.wv["cat"]
print(cat_vector)
# 找与cat相关的词
similar_words = model.wv.most_similar('cat', topn=5)
print(similar_words)