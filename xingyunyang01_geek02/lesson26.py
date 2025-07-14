from typing import List
import os
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


def DeepSeek():
    return ChatOpenAI(
        model="deepseek-chat",
        api_key=os.environ.get("DEEPSEEK_API_KEY_TEST"),
        base_url="https://api.deepseek.com"
    )


llm = DeepSeek()


class State(TypedDict):
    models: list[str]


def TongyiEmbedding()->DashScopeEmbeddings:
    api_key = os.environ.get("TONGYI_API_KEY")
    return DashScopeEmbeddings(dashscope_api_key=api_key, model="text-embedding-v1")


def QdrantVecStoreFromDocs(collection_name:str, docs:List[Document]):
    eb = TongyiEmbedding()
    return QdrantVectorStore.from_documents(docs, eb, url="http://127.0.0.1:6333", collection_name=collection_name)


def load_doc():
    #nltk.download('punkt_tab')
    #nltk.download('averaged_perceptron_tagger')
    word = UnstructuredWordDocumentLoader('../excluded_folders/xingyunyang01_geek02/数据字典.docx')
    docs = word.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=50, chunk_overlap=20)
    s_docs = splitter.split_documents(docs)
    vec_store = QdrantVecStoreFromDocs('data', s_docs)
    print(vec_store)


def QdrantVecStore(collection_name: str):
    eb = TongyiEmbedding()
    return QdrantVectorStore.from_existing_collection(embedding=eb, url="http://127.0.0.1:6333", collection_name=collection_name)


def clearstr(s):
    filter_chars = ['\n', '\r', '\t', '\u3000','  ']
    for char in filter_chars:
        s = s.replace(char, '')
    return s


def format_docs(docs):
    a = "\n\n".join(clearstr(doc.page_content) for doc in docs)
    print("format_docs: ", a)
    return a


def qdrant_search(query:str):
    prompt = """
SYSTEM
你是一个 go 语言编程专家，擅长根据问题生成模型实体类代码。
使用上下文来创建实体struct。你只需输出golang代码，无需任何解释和说明。不要将代码放到 ```go ``` 中。

上下文：
{context}

模型名称例子：UserModel

HUMAN
模型或数据表信息：{question}
"""
    vec_store = QdrantVecStore(collection_name="data")
    retriver = vec_store.as_retriever(search_kwargs={"k": 5})
    print("retriver: ", retriver)
    prompt = ChatPromptTemplate.from_template(prompt)
    print("prompt: ", prompt)

    chain = {"context": retriver | format_docs,
             "question": RunnablePassthrough()} | prompt | llm | StrOutputParser()
    ret = chain.invoke(query)
    print("ret: ", ret)
    return ret


@tool
def modelsTool(model_name: str):
    """该工具可用于生成实体类代码"""
    return qdrant_search(model_name)


systemMessage = """
你是一个golang开发者, 擅长使用gin框架, 你将编写基于gin框架的web程序
你只需直接输出代码, 不要做任何解释和说明，不要将代码放到 ```go ``` 中
"""

models_prompt = """
#模型
生成商品和用户的相关模型
"""


tools = [modelsTool]
llm_withTools = DeepSeek().bind_tools(tools)
tools_names = {tool.name: tool for tool in tools}


def models_node(state):
    message = llm_withTools.invoke([SystemMessage(content=systemMessage), HumanMessage(content=models_prompt)])
    print("message", message)
    for tool_call in message.tool_calls:
        tool_name = tool_call["name"]
        print("tool_name: ", tool_name)
        print("tool_call_args: ", tool_call["args"])
        get_tool = tools_names[tool_name]
        result = get_tool.invoke(tool_call["args"])
        state["models"].append(result)
    return state


if __name__ == "__main__":
    # 入库
    # load_doc()
    # 查询
    # ret = qdrant_search("生成模型")
    # print(ret)

    sg = StateGraph(State)
    sg.add_node("models_node", models_node)
    sg.add_edge(START, "models_node")
    sg.add_edge("models_node", END)
    graph = sg.compile()
    code = graph.invoke({"models": []})
    print("code: ")
    print(code)
    print("models: ")
    for model in code["models"]:
        print(model)