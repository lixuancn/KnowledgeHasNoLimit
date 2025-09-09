# 举一反三的练手，创建一个阿里妈妈广告计划

import os
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END, MessagesState
from typing_extensions import Literal

def DeepSeek():
    return ChatOpenAI(
        model="deepseek-chat",
        api_key=os.environ.get("DEEPSEEK_API_KEY_TEST"),
        base_url="https://api.deepseek.com"
    )

@tool
def get_product_id() -> int:
    """
    获取可投广的淘宝商品ID

    Returns:
    -----------
        int: 商品ID
    """
    return 111222333

@tool
def get_adv_id() -> int:
    """
    获取可投广的广告主ID

    Returns:
    -----------
        int: 广告主ID
    """
    return 444555666


@tool
def create_ad(budget: int, roi:float, product_id: int, adv_id: int):
    """
    创建一个阿里妈妈新广告计划的工具。

    Parameters:
    -----------
    budget: int 预算
    roi: float ROI目标
    product_id: int 商品id
    """
    print(f"创建了一个预算{budget}, ROI目标{roi}, 商品ID是{product_id}, 广告主ID是{adv_id}, ad_id=111111111")
    return 'success'

tools = [create_ad, get_adv_id, get_product_id]
llm = DeepSeek()
llm_with_tools = llm.bind_tools(tools)
tools_names = {tool.name: tool for tool in tools}

def llm_call(state: MessagesState):
    systemMessage = """
    你是一个专业的广告投放优化师, 擅长使用已有工具管理广告相关的数据。
    你可以多次调用工具来获取所需要的信息

    你可以使用的工具有：
    1. get_product_id 获取可以投广的商品ID
    2. get_adv_id 获取可投广的广告主ID
    3. create_ad 创建广告计划

    如果你认为结束了，可以在结尾街上"\nFinal Answer" 字样
    """
    messages = [SystemMessage(content=systemMessage)] + state['messages']

    print("------messages[-1]-------")
    # print(state["messages"])
    print(state["messages"][-1])
    print("------------------")
    response = llm_with_tools.invoke(messages)
    state['messages'].append(response)
    return state

def tool_node(state):
    for tool_call in state["messages"][-1].tool_calls:
        tool = tools_names[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])
        print(f"调用工具{tool.name}, 参数{tool_call['args']}, 结果{observation}")
        # 将观察结果转换为字符串格式
        if isinstance(observation, list):
            # 如果是列表，将其转换为字符串表示
            observation = str(observation)
        state["messages"].append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))
    return state

def should_continue(state: MessagesState) -> Literal["environment", "END"]:
    message = state['messages']
    last_message = message[-1]
    if "Final Answer" in last_message.content:
        return "END"
    return "Action"

if __name__ == "__main__":
    query = "创建一个阿里妈妈广告计划，预算10000, ROI目标3"
    agent_builder = StateGraph(MessagesState)
    agent_builder.add_node("llm_call", llm_call)
    agent_builder.add_node("environment", tool_node)

    agent_builder.add_edge(START, "llm_call")
    agent_builder.add_conditional_edges("llm_call", should_continue, {"Action": "environment", "END": END})
    agent_builder.add_edge("environment", "llm_call")
    agent = agent_builder.compile()

    messages = [HumanMessage(content=query)]
    ret = agent.invoke({"messages": messages})
    print(ret["messages"][-1].content)
