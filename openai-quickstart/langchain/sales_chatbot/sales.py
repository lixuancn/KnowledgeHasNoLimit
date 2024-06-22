with open("real_estate_sales_data.txt") as f:
    real_estate_sales = f.read()

from langchain.text_splitter import CharacterTextSplitter

text_splitter = CharacterTextSplitter(
    separator = r'\d+\.',
    chunk_size = 100,
    chunk_overlap  = 0,
    length_function = len,
    is_separator_regex = True,
)
docs = text_splitter.create_documents([real_estate_sales])
print(docs[0])

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS

db = FAISS.from_documents(docs, OpenAIEmbeddings())
query = "小区吵不吵"
answer_list = db.similarity_search(query)
for ans in answer_list:
    print(ans.page_content + "\n")
db.save_local("real_estates_sale")


# 实例化一个 TopK Retriever
topK_retriever = db.as_retriever(search_kwargs={"k": 3})
print(topK_retriever)
docs = topK_retriever.get_relevant_documents(query)
for doc in docs:
    print(doc.page_content + "\n")

docs = topK_retriever.get_relevant_documents("你们有没有1000万的豪宅啊？")
for doc in docs:
    print(doc.page_content + "\n")

# 实例化一个 similarity_score_threshold Retriever
retriever = db.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"score_threshold": 0.8}
)
docs = retriever.get_relevant_documents(query)
for doc in docs:
    print(doc.page_content + "\n")


docs = retriever.get_relevant_documents(query)
print(docs[0].page_content)
print(docs[0].page_content.split("[销售回答] "))
print(docs[0].page_content.split("[销售回答] ")[-1])



from typing import List

def sales(query: str, score_threshold: float=0.8) -> List[str]:
    retriever = db.as_retriever(search_type="similarity_score_threshold", search_kwargs={"score_threshold": score_threshold})
    docs = retriever.get_relevant_documents(query)
    ans_list = [doc.page_content.split("[销售回答] ")[-1] for doc in docs]
    return ans_list

query = "我想离医院近点"
print(sales(query))


print(sales(query, 0.75))

query = "价格200万以内"
print(f"score:0.8 ans: {sales(query)}\n")
print(f"score:0.75 ans: {sales(query, 0.75)}\n")
print(f"score:0.5 ans: {sales(query, 0.5)}\n")



# 当向量数据库中没有合适答案时，使用大语言模型能力¶
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI

llm = ChatOpenAI(model_name="gpt-4", temperature=0.5)
qa_chain = RetrievalQA.from_chain_type(
    llm,
    retriever=db.as_retriever(search_type="similarity_score_threshold",
    search_kwargs={"score_threshold": 0.8}))
qa_chain({"query": "你们小区有200万的房子吗？"})
qa_chain({"query": "小区吵不吵"})
print(sales("小区吵不吵"))


# 加载 FAISS 向量数据库已有结果
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS

db = FAISS.load_local("real_estates_sale", OpenAIEmbeddings())

from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI

llm = ChatOpenAI(model_name="gpt-4", temperature=0.5)
qa_chain = RetrievalQA.from_chain_type(llm,
                                       retriever=db.as_retriever(search_type="similarity_score_threshold",
                                                                 search_kwargs={"score_threshold": 0.8}))
qa_chain({"query": "我想买别墅，你们有么"})
# 输出内部 Chain 的日志
qa_chain.combine_documents_chain.verbose = True
qa_chain({"query": "我想买别墅，你们有么"})
# 返回向量数据库的检索结果
qa_chain.return_source_documents = True
result = qa_chain({"query": "我想买别墅，你们有么"})