# pip install python-docx
import nltk
from langchain_community.document_loaders import UnstructuredWordDocumentLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain import hub
from llm import QdrantVecStoreFromDocs, QdrantVecStore, ChatOpenAI, DeepSeek
from prompt import RAGPrompt


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

    word = UnstructuredWordDocumentLoader('../../excluded_folders/xingyunyang01_geek02/zhangsan_resume.docx')
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
    ret = chain.invoke("请输出姓名.格式如下\n姓名: ?")
    print(ret)
    ret = chain.invoke("总结专业技能情况,内容可能包含golang、AI Agent、python、rag等.格式如下\n专业技能: ?")
    print(ret)
    ret = chain.invoke("根据各大公司工作过的年份总结工作经验有多少年.格式如下\n工作经验: ?年")
    print(ret)

if __name__ == '__main__':
    load_doc()