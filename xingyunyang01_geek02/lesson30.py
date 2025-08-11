import os
from typing import Any, Hashable

from langgraph.prebuilt import create_react_agent
from typing_extensions import Literal
import akshare as ak
from langchain_core.messages import SystemMessage, ToolMessage, HumanMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState, StateGraph, START, END

def DeepSeek():
    return ChatOpenAI(model='deepseek-chat', api_key=os.environ.get('DEEPSEEK_API_KEY_TEST'), base_url="https://api.deepseek.com")

@tool
def get_stock_info(code: str, name: str) -> list[Any] | list[dict[Hashable, Any]]:
    """可以根据传入的股票代码或股票名称获取股票信息
    Args:
        code: 股票代码
        name: 股票名称
    """
    code_isempty = (code == '' or len(code) <= 2)
    name_isempty = (name == '' or len(name) <= 2)

    if code_isempty and name_isempty:
        return []

    df = ak.stock_cy_a_spot_em()

    if code_isempty and not name_isempty:
        ret = df[df['名称'].str.contains(name)]
    elif not code_isempty and name_isempty:
        ret = df[df['代码'].str.contains(code)]
    else:
        ret = df[df['代码'].str.contains(code) & df['代码'].str.contains(name)]

    return ret.to_dict(orient='records')

def llm_call(state: MessagesState):
    print("llm_call: ", state["messages"])
    """LLM 决定是否调用工具"""
    messages = [
        SystemMessage(content="""
            你是一个股票助手，具备以下技能：
            1. 可以使用 get_stock_info 工具查询股票信息，该工具需要两个参数：
               - code: 股票代码（如果不知道可以传空字符串）
               - name: 股票名称（如果不知道可以传空字符串）

            规则：
            1. 请给出精简的回答，不要做任何的解释和说明
            2. 如果没有匹配到工具，则只会回复"对不起，我无法回答这个问题"
        """)
    ] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def tool_node(state: dict):
    """执行工具调用"""
    print("tool_node", state)
    result = []
    for tool_call in state["messages"][-1].tool_calls:
        tool = tools_by_name[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])
        print("tool_node", tool, observation)
        if isinstance(observation, list):
            observation = str(observation)
        result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))
    return {"messages": result}

def should_continue(state: MessagesState) -> Literal["environment", "END"]:
    """根据大模型是否调用工具来决定是继续循环还是终止"""
    print("should_continue msg start--------")
    for i, msg in enumerate(state["messages"]):
        print(f"should_continue：{i}，元素：{msg}")
    print("should_continue msg end--------")
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        print("should_continue: Action")
        return "Action"
    print("should_continue: End")
    return "END"

llm = DeepSeek()
tools = [get_stock_info]
if False:
    tools_by_name = {tool.name: tool for tool in tools}
    llm_with_tools = llm.bind_tools(tools)
    agent_builder = StateGraph(MessagesState)
    agent_builder.add_node("llm_call", llm_call)
    agent_builder.add_node("environment", tool_node)
    agent_builder.add_edge(START, "llm_call")
    agent_builder.add_conditional_edges("llm_call", should_continue, {"Action": "environment", "END": END})
    agent_builder.add_edge("environment", "llm_call")
    agent = agent_builder.compile()
else:
    agent = create_react_agent(llm, tools=tools)
    graph_png = agent.get_graph(xray=True).draw_mermaid_png()
    with open("agent_graph.png", "wb") as f:
        f.write(graph_png)


messages = [HumanMessage(content="300750 是哪只股票的代码？")]
messages = agent.invoke({"messages": messages})
for m in messages["messages"]:
    m.pretty_print()