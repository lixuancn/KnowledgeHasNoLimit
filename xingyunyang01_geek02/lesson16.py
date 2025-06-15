# pip install python-docx
import nltk
import os
from langchain_community.document_loaders import UnstructuredWordDocumentLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain import hub

from typing import List

def DeepSeek():
    return ChatOpenAI(
        model="deepseek-chat",
        api_key=os.environ.get("DEEPSEEK_API_KEY_TEST"),  # 自行搞定  你的秘钥
        base_url="https://api.deepseek.com"
    )


def TongyiEmbedding()->DashScopeEmbeddings:
    api_key=os.environ.get("TONGYI_API_KEY")
    return DashScopeEmbeddings(dashscope_api_key=api_key,
                           model="text-embedding-v1")


def QdrantVecStoreFromDocs(docs:List[Document]):
    eb=TongyiEmbedding()
    return QdrantVectorStore.from_documents(docs,eb,url="http://127.0.0.1:6333")


def QdrantVecStore(eb:DashScopeEmbeddings,collection_name:str):
    return  QdrantVectorStore.\
        from_existing_collection(embedding=eb,
         url="http://127.0.0.1:6333",
          collection_name=collection_name)


RAGPrompt = """
You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
Question: {question} 
Context: {context} 
Answer:
"""


def clearstr(s):
    filter_chars = ['\n', '\r', '\t', '\u3000', '  ']
    for char in filter_chars:
        s=s.replace(char,'')
    return s
def format_docs(docs):
    return "\n\n".join(clearstr(doc.page_content) for doc in docs)

def load_doc():
    # nltk.download('punkt_tab')
    # nltk.download('averaged_perceptron_tagger')

    word = UnstructuredWordDocumentLoader('../excluded_folders/xingyunyang01_geek02/zhangsan_resume.docx')
    docs = word.load()
    print(docs)

    splitter = RecursiveCharacterTextSplitter(chunk_size=50, chunk_overlap=20)
    s_docs = splitter.split_documents(docs)
    vec_store = QdrantVecStoreFromDocs(s_docs)
    print(vec_store)

    llm = DeepSeek()
    prompt = hub.pull("rlm/rag-prompt")
    chain = {"context": vec_store.as_retriever() | format_docs,
             "question": RunnablePassthrough()} | prompt | llm | StrOutputParser()
    print(chain)
    ret = chain.invoke("请输出姓名.格式如下\n姓名: ?")
    print(ret)
    ret = chain.invoke("总结专业技能情况,内容可能包含golang、AI Agent、python、rag等.格式如下\n专业技能: ?")
    print(ret)
    ret = chain.invoke("根据各大公司工作过的年份总结工作经验有多少年.格式如下\n工作经验: ?年")
    print(ret)

if __name__ == '__main__':
    load_doc()