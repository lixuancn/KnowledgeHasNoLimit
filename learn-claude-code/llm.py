import os
from langchain_openai import ChatOpenAI

class LLM:
    def ChatOpenAI(self, api_key=None, base_url=None, model_name=None, temperature=None):
        """
        创建一个大模型客户端 
        """
        if api_key is None:
            api_key=os.getenv("HOU_SHAN_FANG_ZHOU_API_KEY")
        if base_url is None:
            base_url="https://ark.cn-beijing.volces.com/api/v3"
        if model_name is None:
            model_name="doubao-seed-2-0-code-preview-260215"
        if temperature is None:
            temperature=0.7
        llm = ChatOpenAI(
            api_key=api_key,
            base_url=base_url,
            model_name=model_name,
            temperature=temperature
        )
        return llm
