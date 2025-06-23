import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("sk-19bd309af46c4c42bd1487a4ff1537ab"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    #api_key=os.getenv("deepseek"),
    #base_url="https://api.deepseek.com"
)