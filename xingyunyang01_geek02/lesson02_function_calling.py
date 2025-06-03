import json
import re
import os
from openai import OpenAI


def get_client():
    client = OpenAI(
        api_key=os.getenv("HOU_SHAN_FANG_ZHOU_API_KEY"),
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        timeout=1800,
    )
    return client


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_closing_price",
            "description": "使用该工具获取指定股票的收盘价",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "股票名称",
                    }
                },
                "required": ["name"]
            }
        }
    }
]


def get_closing_price(name):
    print('执行get_closing_price', name)
    if name == "青岛啤酒":
        return "67.92"
    elif name == "贵州茅台":
        return "1488.21"
    else:
        return "未搜索到该股票"


def send_messages(messages):
    print('send_messages', messages)
    response = get_client().chat.completions.create(
        model="deepseek-r1-250120",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    return response


if __name__ == "__main__":
    query = "青岛啤酒和贵州茅台收盘价哪个贵？"
    # query = "青岛啤酒收盘价是多少？"
    prompt = query
    messages = [{"role": "user", "content": prompt}]

    response = send_messages(messages)
    response_text = response.choices[0].message.content
    print("大模型回复：")
    print(response_text)
    print("大模型工具：")
    print(response.choices[0].message.tool_calls)
    messages.append(response.choices[0].message)
    for tool_function in response.choices[0].message.tool_calls:
        if tool_function.function.name == "get_closing_price":
            arg = json.loads(tool_function.function.arguments)
            price = get_closing_price(arg['name'])
            messages.append({
                "role": "tool",
                "content": price,
                "tool_call_id": tool_function.id
            })
    print("messages: ", messages)

    response = send_messages(messages)
    print("回复：")
    print(response.choices[0].message.content)

