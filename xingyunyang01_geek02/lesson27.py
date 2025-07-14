import os
from typing import List
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_community.document_loaders import UnstructuredWordDocumentLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document
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

systemMessage = """
你是一个golang开发者, 擅长使用gin框架, 你将编写基于gin框架的web程序
你只需直接输出代码, 不要做任何解释和说明，不要将代码放到 ```go ``` 中
"""

class State(TypedDict):
    main: str
    routes: list[str]
    handlers: list[str]
    models: list[str]
    middlewares: list[str]


def split_route_handler(message:str)->List[str]:
    codes = message.split('###')
    if len(codes) != 2:
        raise Exception("Invalid message format")
    return codes


def models_node(state):
    prompt = """
#模型
生成用户的相关模型
"""
    message = llm_withTools.invoke([SystemMessage(content=systemMessage), HumanMessage(content=prompt)])
    print("message", message)
    for tool_call in message.tool_calls:
        tool_name = tool_call["name"]
        print("tool_name: ", tool_name)
        print("tool_call_args: ", tool_call["args"])
        get_tool = tools_names[tool_name]
        result = get_tool.invoke(tool_call["args"])
        state["models"].append(result)
    return state


def middleware_node(state):
    prompt = """
#中间件
创建用于跨域的中间件函数
"""
    message = llm_withTools.invoke([SystemMessage(content=systemMessage), HumanMessage(content=prompt)])
    print("message", message)
    for tool_call in message.tool_calls:
        tool_name = tool_call["name"]
        print("tool_name: ", tool_name)
        print("tool_call_args: ", tool_call["args"])
        get_tool = tools_names[tool_name]
        result = get_tool.invoke(tool_call["args"])
        state["middlewares"].append(result)
    return state


def route_node(state):
    prompt = """
#任务
生成gin的路由代码

#路由
1.Get /version 获取应用的版本
2.Get /users 获取用户列表

#规则
字符串分三段，第一段：Method，第二段：请求 PATH，第三段：代码注释

#示例
r.Get("/version", version_handler) // 用于获取应用的版本的路由，handler函数名示例：version_handler
"""
    message = llm.invoke([SystemMessage(content=systemMessage), HumanMessage(content=prompt)])
    state["routes"] += [message.content]
    return state


def handler_node(state):
    prompt = """
#任务
生成gin的路由所对应的handler处理函数代码

#规则
你只需要生成提供的路由代码对应的 handler 函数，不需要生成额外代码
handler函数是和路由代码一一对应的，handler函数的名称在路由代码的注释中已经给出
如果handler函数需要用到模型，则在模型代码中选择

#路由代码
{routes}

#模型代码
{models}

#路由处理函数功能
1.输出应用的版本为1.0
2.输出用户列表
"""
    prompt = prompt.format(routes=state["routes"], models=state["models"])
    message = llm.invoke([SystemMessage(content=systemMessage),HumanMessage(content=prompt)])
    state["handlers"] += [message.content]
    return state


def main_node(state):
    prompt = """
1.创建gin对象
2.中间件的代码为{middlewares}，请提取其函数名称，并使用r.Use注册这些中间件
3.拥有路由代码
{routes}
handler代码已经生成，无需再进行处理
4.启动端口为8080
"""

    prompt = prompt.format(routes=state["routes"][-1], middlewares=state["middlewares"][-1])
    message = llm.invoke([SystemMessage(content=systemMessage), HumanMessage(content=prompt)])
    state["main"] += message.content
    return state


@tool
def middlewares_tool(middlewares_name: str):
    """该工具可用于生成中间件函数，参数需传入具体的生成代码的需求，例如：跨域中间件"""
    prompt = """
SYSTEM
你是一个 go 语言编程专家，擅长根据问题以及代码库的代码进行代码生成。
使用上下文来生成代码。你只需输出golang代码，无需任何解释和说明。不要将代码放到 ```go ``` 中。

上下文：
{context}

HUMAN
问题：{question}
    """
    print("middlewaresTool---start")
    vec_store = QdrantVecStore(collection_name="code")
    retriver = vec_store.as_retriever(search_kwargs={"k": 5})
    print("retriver: ", retriver)
    prompt = ChatPromptTemplate.from_template(prompt)
    print("prompt: ", prompt)

    chain = {"context": retriver | format_docs,
             "question": RunnablePassthrough()} | prompt | llm | StrOutputParser()
    ret = chain.invoke(middlewares_name)
    print("middlewaresTool---end")
    return ret


@tool
def models_tool(model_name: str):
    """该工具可用于生成实体类代码"""
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
    print("models_tool---start")
    vec_store = QdrantVecStore(collection_name="data")
    retriver = vec_store.as_retriever(search_kwargs={"k": 5})
    print("retriver: ", retriver)
    prompt = ChatPromptTemplate.from_template(prompt)
    print("prompt: ", prompt)

    chain = {"context": retriver | format_docs,
             "question": RunnablePassthrough()} | prompt | llm | StrOutputParser()
    ret = chain.invoke(model_name)
    print("ret: ", ret)
    print("models_tool---end")
    return ret



def QdrantVecStore(collection_name: str):
    eb = TongyiEmbedding()
    return QdrantVectorStore.from_existing_collection(embedding=eb, url="http://127.0.0.1:6333", collection_name=collection_name)


def TongyiEmbedding()->DashScopeEmbeddings:
    api_key = os.environ.get("TONGYI_API_KEY")
    return DashScopeEmbeddings(dashscope_api_key=api_key, model="text-embedding-v1")


def clearstr(s):
    filter_chars = ['\n', '\r', '\t', '\u3000','  ']
    for char in filter_chars:
        s = s.replace(char, '')
    return s


def format_docs(docs):
    a = "\n\n".join(clearstr(doc.page_content) for doc in docs)
    print("format_docs: ", a)
    return a


tools = [models_tool, middlewares_tool]
llm_withTools = DeepSeek().bind_tools(tools)
tools_names = {tool.name: tool for tool in tools}


if __name__ == "__main__":
    sg = StateGraph(State)

    sg.add_node("route_node", route_node)
    sg.add_node("handler_node", handler_node)
    sg.add_node("models_node", models_node)
    sg.add_node("middleware_node", middleware_node)
    sg.add_node("main_node", main_node)

    sg.add_edge(START, "models_node")
    sg.add_edge("models_node", "middleware_node")
    sg.add_edge("middleware_node", "route_node")
    sg.add_edge("route_node", "handler_node")
    sg.add_edge("handler_node", "main_node")
    sg.add_edge("main_node", END)

    graph = sg.compile()
    code = graph.invoke({"main": "", "routes": [], "handlers": [], "models": [], "middlewares": []})

    print("code: ")
    print(code)
    print("main: ")
    print(code["main"])
    print("models: ")
    for model in code["models"]:
        print(model)
    print("middlewares: ")
    for middleware in code["middlewares"]:
        print(middleware)
    print("routes: ")
    for route in code["routes"]:
        print(route)
    print("handlers: ")
    for handler in code["handlers"]:
        print(handler)

