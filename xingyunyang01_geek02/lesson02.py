import json
import re
import os
from openai import OpenAI

REACT_PROMPT = """
{instructions}

TOOLS:
------

You have access to the following tools:

{tools}

To use a tool, please use the following format:

```
Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
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

def get_client():
    client = OpenAI(
        api_key=os.getenv("HOU_SHAN_FANG_ZHOU_API_KEY"),
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        timeout=1800,
    )
    return client

tools = [
    {
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
]


def get_closing_price(name):
    print('get_closing_price', name)
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
        messages=messages
    )
    return response


if __name__ == "__main__":
    instructions = "你是一个股票助手，可以回答股票相关问题"
    query = "青岛啤酒和贵州茅台收盘价哪个贵？"
    prompt = REACT_PROMPT.format(instructions=instructions, tools=tools, tool_names="get_closing_price", input=query)
    messages = [{"role": "user", "content": prompt}]
    print(messages)
    while True:
        response = send_messages(messages)
        response_text = response.choices[0].message.content
        print("大模型回复：")
        print(response_text)
        final_answer_match = re.search(r'Final Answer:\s*(.*)', response_text)
        if final_answer_match:
            final_answer = final_answer_match.group(1)
            print("最终答案：", final_answer)
            break
        messages.append(response.choices[0].message)

        action_match = re.search(r'Action:\s*(\w+)', response_text)
        action_input_match = re.search(r'Action Input:\s*({.*?}|".*?")', response_text, re.DOTALL)

        if action_match and action_input_match:
            tool_name = action_match.group(1)
            params = json.loads(action_input_match.group(1))
            if tool_name == "get_closing_price":
                observation = get_closing_price(params['name'])
                print("人类的回复：Observation:", observation)
                messages.append({"role": "user", "content": f"Observation: {observation}"})


