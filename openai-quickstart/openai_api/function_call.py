import json
import requests
import os
from tenacity import retry, wait_random_exponential, stop_after_attempt
from termcolor import colored

# 注意：本示例直接构造 HTTP 请求访问 OpenAI API，因此无需使用 openai Python SDK。

GPT_MODEL = "gpt-3.5-turbo"

# 使用了retry库，指定在请求失败时的重试策略。
# 这里设定的是指数等待（wait_random_exponential），时间间隔的最大值为40秒，并且最多重试3次（stop_after_attempt(3)）。
# 定义一个函数chat_completion_request，主要用于发送 聊天补全 请求到OpenAI服务器
@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
def chat_completion_request(messages, functions=None, function_call=None, model=GPT_MODEL):

    # 设定请求的header信息，包括 API_KEY
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + os.getenv("OPENAI_API_KEY"),
    }

    # 设定请求的JSON数据，包括GPT 模型名和要进行补全的消息
    json_data = {"model": model, "messages": messages}

    # 如果传入了functions，将其加入到json_data中
    if functions is not None:
        json_data.update({"functions": functions})

    # 如果传入了function_call，将其加入到json_data中
    if function_call is not None:
        json_data.update({"function_call": function_call})

    # 尝试发送POST请求到OpenAI服务器的chat/completions接口
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=json_data,
        )
        # 返回服务器的响应
        return response

    # 如果发送请求或处理响应时出现异常，打印异常信息并返回
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e


# 定义一个函数pretty_print_conversation，用于打印消息对话内容
def pretty_print_conversation(messages):
    role_to_color = {
        "system": "red",
        "user": "green",
        "assistant": "blue",
        "function": "magenta",
    }
    for message in messages:
        if message["role"] == "system":
            print(colored(f"system: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "user":
            print(colored(f"user: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "assistant" and message.get("function_call"):
            print(colored(f"assistant[function_call]: {message['function_call']}\n", role_to_color[message["role"]]))
        elif message["role"] == "assistant" and not message.get("function_call"):
            print(colored(f"assistant[content]: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "function":
            print(colored(f"function ({message['name']}): {message['content']}\n", role_to_color[message["role"]]))

# 定义一个名为functions的列表，其中包含两个字典，这两个字典分别定义了两个功能的相关参数

# 第一个字典定义了一个名为"get_current_weather"的功能
functions = [
    {
        "name": "get_current_weather",  # 功能的名称
        "description": "Get the current weather",  # 功能的描述
        "parameters": {  # 定义该功能需要的参数
            "type": "object",
            "properties": {  # 参数的属性
                "location": {  # 地点参数
                    "type": "string",  # 参数类型为字符串
                    "description": "The city and state, e.g. San Francisco, CA",  # 参数的描述
                },
                "format": {  # 温度单位参数
                    "type": "string",  # 参数类型为字符串
                    "enum": ["celsius", "fahrenheit"],  # 参数的取值范围
                    "description": "The temperature unit to use. Infer this from the users location.",  # 参数的描述
                },
            },
            "required": ["location", "format"],  # 该功能需要的必要参数
        },
    },
    # 第二个字典定义了一个名为"get_n_day_weather_forecast"的功能
    {
        "name": "get_n_day_weather_forecast",  # 功能的名称
        "description": "Get an N-day weather forecast",  # 功能的描述
        "parameters": {  # 定义该功能需要的参数
            "type": "object",
            "properties": {  # 参数的属性
                "location": {  # 地点参数
                    "type": "string",  # 参数类型为字符串
                    "description": "The city and state, e.g. San Francisco, CA",  # 参数的描述
                },
                "format": {  # 温度单位参数
                    "type": "string",  # 参数类型为字符串
                    "enum": ["celsius", "fahrenheit"],  # 参数的取值范围
                    "description": "The temperature unit to use. Infer this from the users location.",  # 参数的描述
                },
                "num_days": {  # 预测天数参数
                    "type": "integer",  # 参数类型为整数
                    "description": "The number of days to forecast",  # 参数的描述
                }
            },
            "required": ["location", "format", "num_days"]  # 该功能需要的必要参数
        },
    },
]

# ---------------

messages = []
messages.append({
    "role": "system",
    "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."  # 消息的内容
})
messages.append({
    "role": "user",
    "content": "what's the weather like tody"
})
chat_response = chat_completion_request(messages, functions)

assistant_message = chat_response.json()["choices"][0]["message"]

messages.append(assistant_message)

pretty_print_conversation(messages)

# ---------------

# 向messages列表添加一条用户角色的消息，用户告知他们在苏格兰的格拉斯哥
messages.append({
    "role": "user",  # 消息的角色是"user"
    "content": "I'm in Shanghai, China."  # 用户的消息内容
})

# 再次使用定义的chat_completion_request函数发起一个请求，传入更新后的messages和functions作为参数
chat_response = chat_completion_request(messages, functions)

# 解析返回的JSON数据，获取助手的新的回复消息
assistant_message = chat_response.json()["choices"][0]["message"]

# 将助手的新的回复消息添加到messages列表中
messages.append(assistant_message)

pretty_print_conversation(messages)



# ---------------

# 初始化一个空的messages列表
messages = []

# 向messages列表添加一条系统角色的消息，要求不做关于函数参数值的假设，如果用户的请求模糊，应该寻求澄清
messages.append({
    "role": "system",  # 消息的角色是"system"
    "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."
})

# 向messages列表添加一条用户角色的消息，用户询问在未来x天内苏格兰格拉斯哥的天气情况
messages.append({
    "role": "user",  # 消息的角色是"user"
    "content": "what is the weather going to be like in Shanghai, China over the next x days"
})

# 使用定义的chat_completion_request函数发起一个请求，传入messages和functions作为参数
chat_response = chat_completion_request(
    messages, functions=functions
)

# 解析返回的JSON数据，获取助手的回复消息
assistant_message = chat_response.json()["choices"][0]["message"]

# 将助手的回复消息添加到messages列表中
messages.append(assistant_message)

# 打印助手的回复消息
pretty_print_conversation(messages)

# ---------------

# 向messages列表添加一条用户角色的消息，用户指定接下来的天数为5天
messages.append({
    "role": "user",  # 消息的角色是"user"
    "content": "5 days"
})

# 使用定义的chat_completion_request函数发起一个请求，传入messages和functions作为参数
chat_response = chat_completion_request(
    messages, functions=functions
)

# 解析返回的JSON数据，获取第一个选项
assistant_message = chat_response.json()["choices"][0]["message"]

# 将助手的回复消息添加到messages列表中
messages.append(assistant_message)

# 打印助手的回复消息
pretty_print_conversation(messages)


# ---------------------

# 在这个代码单元中，我们强制GPT 模型使用get_n_day_weather_forecast函数
messages = []  # 创建一个空的消息列表

# 添加系统角色的消息
messages.append({
    "role": "system",  # 角色为系统
    "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."
})

# 添加用户角色的消息
messages.append({
    "role": "user",  # 角色为用户
    "content": "Give me a weather report for San Diego, USA."
})

# 使用定义的chat_completion_request函数发起一个请求，传入messages、functions以及特定的function_call作为参数
chat_response = chat_completion_request(
    messages, functions=functions, function_call={"name": "get_n_day_weather_forecast"}
)

# 解析返回的JSON数据，获取第一个选项
assistant_message = chat_response.json()["choices"][0]["message"]

# 将助手的回复消息添加到messages列表中
messages.append(assistant_message)

# 打印助手的回复消息
pretty_print_conversation(messages)

# ---------------------
# 如果我们不强制GPT 模型使用 get_n_day_weather_forecast，它可能不会使用
messages = []  # 创建一个空的消息列表

# 添加系统角色的消息
messages.append({
    "role": "system",  # 角色为系统
    "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."
})

# 添加用户角色的消息
messages.append({
    "role": "user",  # 角色为用户
    "content": "Give me a weather report for San Diego, USA."
})

# 使用定义的chat_completion_request函数发起一个请求，传入messages和functions作为参数
chat_response = chat_completion_request(
    messages, functions=functions
)

# 解析返回的JSON数据，获取第一个选项
assistant_message = chat_response.json()["choices"][0]["message"]

# 将助手的回复消息添加到messages列表中
messages.append(assistant_message)

# 打印助手的回复消息
pretty_print_conversation(messages)

# --------------------------

# 创建另一个空的消息列表
messages = []

# 添加系统角色的消息
messages.append({
    "role": "system",  # 角色为系统
    "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."
})

# 添加用户角色的消息
messages.append({
    "role": "user",  # 角色为用户
    "content": "Give me the current weather (use Celcius) for Toronto, Canada."
})

# 使用定义的chat_completion_request函数发起一个请求，传入messages、functions和function_call作为参数
chat_response = chat_completion_request(
    messages, functions=functions, function_call="none"
)

# 解析返回的JSON数据，获取第一个选项
assistant_message = chat_response.json()["choices"][0]["message"]

# 将助手的回复消息添加到messages列表中
messages.append(assistant_message)

# 打印助手的回复消息
pretty_print_conversation(messages)