import json
import os
import re

import requests
from openai import OpenAI

tools = [
    {
        "name": "get_location_coordinate",
        "description": "根据POI名称获取经纬度",
        "parameters": {
            "type": "object",
            "properties": {
                "keywords": {
                    "type": "string",
                    "description": "POI中文名"
                },
                "region": {
                    "type": "string",
                    "description": "POI所在地区的中文名"
                },
            },
            "required": ["keywords"]
        },
    },
    {
        "name": "search_nearby_pois",
        "description": "搜索指定坐标附近的POI",
        "parameters": {
            "type": "object",
            "properties": {
                "keywords": {
                    "type": "string",
                    "description": "目标POI的关键字"
                },
                "location": {
                    "type": "string",
                    "description": "中心点坐标（经度,纬度）"
                },
            },
            "required": ["keywords"]
        },
    },
]


def http_get(uri, params=None):
    url = f"{BASE_URL}/{uri}"
    try:
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "message": str(e)}


BASE_URL = "https://restapi.amap.com/v5/place"
API_KEY = os.environ.get("GAODE_API_WEB")


def get_location_coordinate(keywords, region=None):
    """根据POI获取经纬度坐标"""
    print("get_location_coordination: ", keywords, region)
    params = {
        "key": API_KEY,
        "keywords": keywords
    }
    if region:
        params["region"] = region

    result = http_get("text", params)
    print(result)
    if result["success"] and result["data"].get("pois"):
        poi = result["data"].get("pois")[0]
        return f"POI: {keywords}, 坐标: {poi['location']}"
    return "未找到POI坐标"


def search_nearby_pois(keywords, location=None):
    """指定坐标搜索附近的POI"""
    print("search_nearby_pois: ", keywords, location)
    params = {
        "key": API_KEY,
        "keywords": keywords
    }
    if location:
        params["location"] = location

    result = http_get("around", params)
    if result["success"] and result["data"].get("pois"):
        results = []
        for poi in result["data"]["pois"][:3]:
            results.append(f"名称: {poi['name']}, 地址: {poi['address']}, 坐标: {poi['location']}")
        return "\n".join(results)
    return "未找到符合条件的POI"


def get_client():
    client = OpenAI(
        api_key=os.getenv("HOU_SHAN_FANG_ZHOU_API_KEY"),
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        timeout=1800,
    )
    return client


def send_messages(messages):
    print('send_messages', messages)
    response = get_client().chat.completions.create(
        model="deepseek-r1-250120",
        messages=messages
    )
    return response


PROMPT = """
你是一个定位助手，可以根据用户的输入，查找某地点附近的目标。

工具列表:
------
你可以选择下面的工具：
{tools}

如果使用了工具，请按照以下的格式输出，并且不要使用单引号，请使用双引号：
使用工具：<工具名>。工具参数：<工具参数>

Begin!
新的会话: {input}
"""

if __name__ == "__main__":
    # result = get_location_coordination("鼓楼", "北京")
    # print(result)
    # result = search_nearby_pois("奶茶", "116.395937,39.940781")
    # print(result)
    instructions = "你是一个定位助手，可以根据用户的输入，查找某地点附近的目标"
    query = "北京鼓楼附近的奶茶店有哪些"
    prompt = PROMPT.format(instructions=instructions, tools=tools, input=query)
    print(prompt)
    messages = [{"role": "user", "content": prompt}]
    print(messages)

    response = send_messages(messages)
    response_text = response.choices[0].message.content
    print(response)
    print("大模型回复：")
    print(response_text)

    tools = re.finditer(r'使用工具：\s*(\w+).*?工具参数：\s*(\{.*?\})', response_text,  re.DOTALL)
    for tool in tools:
        tool_name = tool.group(1)
        params_json = tool.group(2)
        params_dict = json.loads(params_json)
        if tool_name == "get_location_coordinate":
            observation = get_location_coordinate(**params_dict)
            print("调用工具获取的返回：", observation)
            messages.append({"role": "user", "content": f"调用工具获取的返回: {observation}"})
            response = send_messages(messages)
            response_text = response.choices[0].message.content
            print("大模型回复：")
            print(response_text)

        # if tool_name == "search_nearby_pois":
        #     observation = search_nearby_pois(params_dict)