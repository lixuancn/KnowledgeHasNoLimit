import os
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI


def DeepSeek():
    return ChatOpenAI(
        model="deepseek-chat",
        api_key=os.environ.get("DEEPSEEK_API_KEY_TEST"),
        base_url="https://api.deepseek.com"
    )


class State(TypedDict):
    models: list[str]


@tool
def modelsTool(modelname: str):
    """该工具可用于生成实体类代码"""

    modelname = modelname.lower()

    if "user" or "用户" in modelname:
        return """
type UserModel struct
{
    UserID int64 `json:"user_id"`
    UserName string `json:"user_name"`
    UserEmail string `json:"user_email"`
}        
"""
    return ""


tools = [modelsTool]
llm = DeepSeek().bind_tools(tools)
tools_names = {tool.name: tool for tool in tools}


systemMessage = """
你是一个golang开发者, 擅长使用gin框架, 你将编写基于gin框架的web程序
你只需直接输出代码, 不要做任何解释和说明，不要将代码放到 ```go ``` 中
"""

models_prompt = """
#模型
生成User相关模型
"""


def models_node(state):
    message = llm.invoke([SystemMessage(content=systemMessage),HumanMessage(content=models_prompt)])
    for tool_call in message.tool_calls:
        tool_name = tool_call["name"]
        get_tool = tools_names[tool_name]
        result = get_tool.invoke(tool_call["args"])
        state["models"].append(result)
    return state


if __name__ == "__main__":
    sg = StateGraph(State)
    sg.add_node("models_node", models_node)

    sg.add_edge(START, "models_node")
    sg.add_edge("models_node", END)

    graph = sg.compile()
    code = graph.invoke({"main": "", "routes": [], "handlers": [], "models": []})

    print("code: ")
    print(code)
    print("models: ")
    print(code["models"][0])