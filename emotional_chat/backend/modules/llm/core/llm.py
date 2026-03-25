import os
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

class LLM:
    def ChatOpenAI(self, api_key=None, base_url=None, model_name=None, temperature=None):
        """
        创建一个大模型客户端 
        """
        if api_key is None:
            api_key=os.getenv("ALIYUN_TONGYI_QWEN_API_KEY")
        if base_url is None:
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        if model_name is None:
            model_name="qwen-max"
        if temperature is None:
            temperature=0.7
        llm = ChatOpenAI(
            api_key=api_key,
            base_url=base_url,
            model_name=model_name,
            temperature=temperature
        )
        return llm
    
    def getPromptBySystemMessageAndHumanMessage(self, system_message: str, human_message: str):
        """
        根据系统消息和用户消息创建一个完整的提示
        """
        return [
                # System角色：设置系统提示
                SystemMessage(content=system_message),
                # User角色：用户输入
                HumanMessage(content=human_message)
            ]