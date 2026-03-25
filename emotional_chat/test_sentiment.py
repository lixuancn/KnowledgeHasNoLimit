# 示例：
# from textblob import TextBlob

# text = "我很生气"
# blob = TextBlob(text)
# print(blob.sentiment)


# 示例
from transformers import pipeline

classifier = pipeline("sentiment-analysis", 
                     model="cardiffnlp/twitter-roberta-base-sentiment-latest")

result = classifier("I feel completely hopeless and don't want to go on.")

print(result)  # [{'label': 'NEGATIVE', 'score': 0.998}]