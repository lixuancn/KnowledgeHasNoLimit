from typing import List
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from langchain_core.messages import SystemMessage, HumanMessage

import os
from langchain_openai import ChatOpenAI

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


def split_route_handler(message:str)->List[str]:
    codes = message.split('###')
    if len(codes) != 2:
        raise Exception("Invalid message format")
    return codes


def models_node(state):
    prompt = """
#模型
1.用户模型，包含字段：UserID(int), UserName(string), UserEmail(string)
生成上述模型对于的 struct。struct名称示例：UserModel
"""
    message = llm.invoke([SystemMessage(content=systemMessage), HumanMessage(content=prompt)])
    state["models"] += [message.content]
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
2.拥有路由代码
{routes}
handler代码已经生成，无需再进行处理
3.启动端口为8080
    """

    prompt = prompt.format(routes=state["routes"][-1])
    message = llm.invoke([SystemMessage(content=systemMessage), HumanMessage(content=prompt)])
    state["main"] += message.content
    return state


if __name__ == "__main__":
    sg = StateGraph(State)

    sg.add_node("route_node", route_node)
    sg.add_node("handler_node", handler_node)
    sg.add_node("models_node", models_node)
    sg.add_node("main_node", main_node)

    sg.add_edge(START, "models_node")
    sg.add_edge("models_node", "route_node")
    sg.add_edge("route_node", "handler_node")
    sg.add_edge("handler_node", "main_node")
    sg.add_edge("main_node", END)

    graph = sg.compile()
    code = graph.invoke({"main": "", "routes": [], "handlers": [], "models": []})

    print("code: ")
    print(code)
    print("models: ")
    print(code["models"])
    print("routes: ")
    print(code["routes"])
    print("main: ")
    print(code["main"])
    for handler in code["handlers"]:
        print(handler)

