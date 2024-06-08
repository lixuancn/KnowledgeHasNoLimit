import os

# 更换为自己的 Serp API KEY
os.environ["SERPAPI_API_KEY"] = "1e3c93e0753ac224098370cd71da86150c6609caba6b5aaa307e04b72a5006e1"

from langchain import OpenAI, SerpAPIWrapper
from langchain.agents import initialize_agent, AgentType, Tool

llm = OpenAI(temperature=0)

# 实例化查询工具
search = SerpAPIWrapper()
tools = [
    Tool(
        name="Intermediate Answer",
        func=search.run,
        description="useful for when you need to ask with search",
    )
]

# 实例化 SELF_ASK_WITH_SEARCH Agent
self_ask_with_search = initialize_agent(
    tools, llm, agent=AgentType.SELF_ASK_WITH_SEARCH, verbose=True
)

# 实际运行 Agent，查询问题（正确）
self_ask_with_search.run(
    "成都举办的大运会是第几届大运会？"
)

# 实际运行 Agent，查询问题（有歧义）
self_ask_with_search.run(
    "2023年大运会举办地在哪里？"
)

# Reason-only 答案（错误）
print(llm("成都举办的大运会是第几届大运会？"))
# Reason-only 答案（错误）
print(llm("2023年大运会举办地在哪里？"))





from langchain.chat_models import ChatOpenAI

chat_model = ChatOpenAI(model="gpt-4-1106-preview", temperature=0)
self_ask_with_search_chat = initialize_agent(
    tools, chat_model, agent=AgentType.SELF_ASK_WITH_SEARCH, verbose=True
)
# GPT-4 based ReAct 答案（正确）
self_ask_with_search_chat.run(
    "2023年大运会举办地在哪里？"
)