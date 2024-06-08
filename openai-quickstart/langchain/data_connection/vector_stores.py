from langchain.document_loaders import TextLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma

# 加载长文本
raw_documents = TextLoader('../tests/state_of_the_union.txt').load()
# 实例化文本分割器
text_splitter = CharacterTextSplitter(chunk_size=200, chunk_overlap=0)
# 分割文本
documents = text_splitter.split_documents(raw_documents)
embeddings_model = OpenAIEmbeddings()
# 将分割后的文本，使用 OpenAI 嵌入模型获取嵌入向量，并存储在 Chroma 中
db = Chroma.from_documents(documents, embeddings_model)

query = "What did the president say about Ketanji Brown Jackson"
docs = db.similarity_search(query)
print(docs[0].page_content)

embedding_vector = embeddings_model.embed_query(query)
docs = db.similarity_search_by_vector(embedding_vector)
print(docs[0].page_content)