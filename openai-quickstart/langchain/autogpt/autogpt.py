import os

os.environ["SERPAPI_API_KEY"] = "1e3c93e0753ac224098370cd71da86150c6609caba6b5aaa307e04b72a5006e1"

from langchain.utilities import SerpAPIWrapper
from langchain.agents import Tool
from langchain.tools.file_management.write import WriteFileTool
from langchain.tools.file_management.read import ReadFileTool

# 构造 AutoGPT 的工具集
search = SerpAPIWrapper()
tools = [
    Tool(
        name="search",
        func=search.run,
        description="useful for when you need to answer questions about current events. You should ask targeted questions",
    ),
    WriteFileTool(),
    ReadFileTool(),
]

from langchain.embeddings import OpenAIEmbeddings

# OpenAI Embedding 模型
embeddings_model = OpenAIEmbeddings()



import faiss
from langchain.vectorstores import FAISS
from langchain.docstore import InMemoryDocstore

# OpenAI Embedding 向量维数
embedding_size = 1536
# 使用 Faiss 的 IndexFlatL2 索引
index = faiss.IndexFlatL2(embedding_size)
# 实例化 Faiss 向量数据库
vectorstore = FAISS(embeddings_model.embed_query, index, InMemoryDocstore({}), {})


agent = AutoGPT.from_llm_and_tools(
    ai_name="Jarvis",
    ai_role="Assistant",
    tools=tools,
    llm=ChatOpenAI(model_name="gpt-4", temperature=0, verbose=True),
    memory=vectorstore.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"score_threshold": 0.8}),# 实例化 Faiss 的 VectorStoreRetriever
)
# 打印 Auto-GPT 内部的 chain 日志
agent.chain.verbose = True
agent.run(["2023年成都大运会，中国金牌数是多少"])