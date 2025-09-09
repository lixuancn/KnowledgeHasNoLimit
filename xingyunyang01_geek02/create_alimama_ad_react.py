# 举一反三的练手，创建一个阿里妈妈广告计划
import json
import os
import re

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
    return OpenAI(
        api_key=os.getenv("HOU_SHAN_FANG_ZHOU_API_KEY"),
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        timeout=1800,
    )

tools = [
    {
        "name": "get_product_id",
        "description": "获取可投广的淘宝商品ID",
    },
    {
        "name": "get_adv_id",
        "description": "获取可投广的广告主ID",
    },
    {
        "name": "create_ad",
        "description": "创建一个阿里妈妈新广告计划，返回值为新建的广告计划的id",
        "parameters": {
            "type": "object",
            "properties": {
                "budget": {
                    "type": "integer",
                    "description": "广告预算",
                },
                "roi": {
                    "type": "number",
                    "description": "ROI目标",
                },
                "product_id": {
                    "type": "integer",
                    "description": "商品ID",
                },
                "adv_id": {
                    "type": "integer",
                    "description": "广告主ID",
                },
            },
            "required": ["budget", "roi", "product_id", "adv_id"]
        }
    }
]

@tool
def get_product_id() -> int:
    """
    获取可投广的淘宝商品ID

    Returns:
    -----------
        int: 商品ID
    """
    print("调用工具get_product_id，返回111222333")
    return 111222333

@tool
def get_adv_id() -> int:
    """
    获取可投广的广告主ID

    Returns:
    -----------
        int: 广告主ID
    """
    print("调用工具get_adv_id，返回444555666")
    return 444555666


@tool
def create_ad(budget: int, roi:float, product_id: int, adv_id: int) -> int:
    """
    创建一个阿里妈妈新广告计划的工具。

    Parameters:
    -----------
    budget: int 预算
    roi: float ROI目标
    product_id: int 商品id
    """
    print(f"调用工具create_ad 预算{budget}, ROI目标{roi}, 商品ID是{product_id}, 广告主ID是{adv_id}, ad_id=111111111")
    return 111111111

llm = DeepSeek()

REACT_PROMPT = """
    你是一个专业的广告投放优化师, 擅长使用已有工具管理广告相关的数据。
    你可以多次调用工具来获取所需要的信息

    TOOLS:
    ------

    You have access to the following tools:

    {tools}

    To use a tool, please use the following format:

    ```
    Thought: Do I need to use a tool? Yes
    Action: the action to take, should be one of [get_product_id, get_adv_id, create_ad]
    Action Input: the input to the action
    ```

    Then wait for Human will response to you the result of action by use Observation.
    ... (this Thought/Action/Action Input/Observation can repeat N times)
    When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:

    ```
    Thought: Do I need to use a tool? No
    Final Answer: [your response here]
    ```
    
    Begin!

    New input: {input}
    """

def llm_call(messages):
    print('send_messages', messages)
    response = llm.invoke(messages)
    return response

if __name__ == "__main__":
    query = "创建一个阿里妈妈广告计划，预算10000, ROI目标3"
    prompt = REACT_PROMPT.format(tools=tools, input=query)
    messages = [SystemMessage(content=REACT_PROMPT.format(tools=tools, input=query)), HumanMessage(content=query)]
    while True:
        response = llm.invoke(messages)
        print(f"大模型回复：{response.content}")
        response_text = response.content
        final_answer_match = re.search(r'Final Answer:\s*(.*)', response_text)
        if final_answer_match:
            final_answer = final_answer_match.group(1)
            print("最终答案：", final_answer)
            break
        messages.append(HumanMessage(content=response_text))

        action_match = re.search(r'Action:\s*(\w+)', response_text)
        action_input_match = re.search(r'Action Input:\s*({.*?}|".*?")', response_text, re.DOTALL)

        if action_match and action_input_match:
            tool_name = action_match.group(1)
            params = json.loads(action_input_match.group(1))
            print(params)
            if tool_name == "get_product_id":
                observation = get_product_id(params)
                print("人类的回复get_product_id：Observation:", observation)
                messages.append(HumanMessage(content=f"Observation: {observation}"))
            if tool_name == "get_adv_id":
                observation = get_adv_id(params)
                print("人类的回复get_adv_id：Observation:", observation)
                messages.append(HumanMessage(content=f"Observation: {observation}"))
            if tool_name == "create_ad":
                observation = create_ad(params)
                print("人类的回复create_ad：Observation:", observation)
                messages.append(HumanMessage(content=f"Observation: {observation}"))

