import os

# 更换为自己的 Serp API KEY
os.environ["SERPAPI_API_KEY"] = "1e3c93e0753ac224098370cd71da86150c6609caba6b5aaa307e04b72a5006e1"

from langchain.llms import OpenAI

llm = OpenAI(temperature=0)

from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.agents import AgentType

# 加载 LangChain 内置的 Tools
tools = load_tools(["serpapi", "llm-math"], llm=llm)

# 实例化 ZERO_SHOT_REACT Agent
agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)
agent.run("谁是莱昂纳多·迪卡普里奥的女朋友？她现在年龄的0.43次方是多少?")


from langchain.chat_models import ChatOpenAI

chat_model = ChatOpenAI(model="gpt-4-1106-preview", temperature=0)
agent = initialize_agent(tools, chat_model, agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION, verbose=True)
agent.run("谁是莱昂纳多·迪卡普里奥的女朋友？她现在年龄的0.43次方是多少?")