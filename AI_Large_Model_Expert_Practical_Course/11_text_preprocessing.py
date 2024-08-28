import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
import spacy

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
def remove_noise(text):
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'[^\w\s]', '', text)
    return text

# 清洗 去除html
text = "<p>Hello, World! Here's a <a href='https://example.com'>link</a>.</p>"
clean_text = remove_noise(text)
print(clean_text)

tokens_normalized = [token.lower() for token in clean_text]
print(tokens_normalized)

# 去除停用词
stop_words = set(stopwords.words('english'))
filtered_tokens = [word for word in tokens_normalized if not word in stop_words]
print(filtered_tokens)

# 分词
text = "Natural language processing (NLP) is a field of computer science."
text = "The leaves on the trees are falling quickly in the autumn season."
tokens = word_tokenize(text)
print(tokens)

# 词干提取
stemmer = PorterStemmer()
stemmed_tokens = [stemmer.stem(token) for token in tokens]
print("原始文本:")
print(tokens)
print("词干提取后:")
print(stemmed_tokens)

# 词性还原
lemmatizer = WordNetLemmatizer()
lemmatized_tokens = [lemmatizer.lemmatize(token) for token in tokens]
print("原始文本:")
print(tokens)
print("词形还原后:")
print(lemmatized_tokens)

# 命名实体识别
nlp = spacy.load("en_core_web_sm")
text = "Apple is looking at buying U.K. startup for $1 billion."
doc = nlp(text)
for d in doc:
    print((d.text, d.pos_))
print("命名实体识别:")
for ent in doc.ents:
    print((ent.text, ent.label_))