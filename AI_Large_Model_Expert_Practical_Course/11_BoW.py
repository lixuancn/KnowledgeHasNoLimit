from sklearn.feature_extraction.text import CountVectorizer
corpus = ['Text analysis is fun', 'Text analysis with Python', 'Data Science is fun', 'Python is great for text analysis']
vectorizer = CountVectorizer()
x = vectorizer.fit_transform(corpus)
print(vectorizer.get_feature_names_out())
print(x.toarray())
