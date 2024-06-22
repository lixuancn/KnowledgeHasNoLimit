from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader


# 实例化文档加载器
loader = TextLoader("../tests/state_of_the_union.txt")
# 加载文档
documents = loader.load()

# 实例化文本分割器
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
# 分割文本
docs = text_splitter.split_documents(documents)

# OpenAI Embedding 模型
embeddings = OpenAIEmbeddings()

# FAISS 向量数据库，使用 docs 的向量作为初始化存储
db = FAISS.from_documents(docs, embeddings)

# 构造提问 Query
query = "What did the president say about Ketanji Brown Jackson"

# 在 Faiss 中进行相似度搜索，找出与 query 最相似结果
docs = db.similarity_search(query)

# 输出 Faiss 中最相似结果
print(docs[0].page_content)

# 持久化
db.save_local("faiss_index")

# 加载
new_db = FAISS.load_local("faiss_index", embeddings)
docs = new_db.similarity_search(query)
print(docs[0].page_content)