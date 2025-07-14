import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import tool
from langchain_community.document_loaders import UnstructuredWordDocumentLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain.prompts.chat import ChatPromptTemplate
from typing import List


def TongyiEmbedding()->DashScopeEmbeddings:
    api_key = os.environ.get("TONGYI_API_KEY")
    return DashScopeEmbeddings(dashscope_api_key=api_key, model="text-embedding-v1")


def QdrantVecStoreFromDocs(collection_name: str, docs: List[Document]):
    eb = TongyiEmbedding()
    return QdrantVectorStore.from_documents(docs, eb, url="http://127.0.0.1:6333", collection_name=collection_name)



def QdrantVecStore(collection_name: str):
    eb = TongyiEmbedding()
    return QdrantVectorStore.from_existing_collection(embedding=eb, url="http://127.0.0.1:6333", collection_name=collection_name)


def load_code(ext: str, dir_path: str):
    if not os.path.exists(dir_path):
        print(f"文件夹{dir_path}不存在")
        return

    files = []

    for file in os.listdir(dir_path):
        if file.endswith(ext):
            print(f"加载文件{file}")
            files.append(os.path.join(dir_path, file))

    print("files: ", files)

    all_docs = []
    code_text_splitter = CharacterTextSplitter(separator="\n", chunk_size=500, chunk_overlap=100, length_function=len)

    for file in files:
        loader = TextLoader(file, encoding='utf-8').load()
        docs = code_text_splitter.split_documents(loader)
        for doc in docs:
            doc.metadata["source"] = file
            all_docs.append(doc)

    QdrantVecStoreFromDocs("code", all_docs)


if __name__ == '__main__':
    # 入库
    load_code(".go", '../excluded_folders/xingyunyang01_geek02/code/')
