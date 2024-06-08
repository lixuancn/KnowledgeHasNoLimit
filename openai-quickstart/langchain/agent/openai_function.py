from langchain.chat_models import ChatOpenAI

# 使用 GPT-3.5-turbo
llm = ChatOpenAI(temperature=0)

from langchain.agents import tool

@tool
def get_word_length(word: str) -> int:
    """Returns the length of a word."""
    return len(word)

tools = [get_word_length]


from langchain.schema import SystemMessage
from langchain.agents import OpenAIFunctionsAgent

system_message = SystemMessage(content="你是非常强大的AI助手，但在计算单词长度方面不擅长。")
prompt = OpenAIFunctionsAgent.create_prompt(system_message=system_message)
agent = OpenAIFunctionsAgent(llm=llm, tools=tools, prompt=prompt)

from langchain.agents import AgentExecutor

# 实例化 OpenAIFunctionsAgent
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
agent_executor.run("单词“educa”中有多少个字母?")


# ----------
from langchain.prompts import MessagesPlaceholder

MEMORY_KEY = "chat_history"
prompt = OpenAIFunctionsAgent.create_prompt(
    system_message=system_message,
    extra_prompt_messages=[MessagesPlaceholder(variable_name=MEMORY_KEY)]
)

from langchain.memory import ConversationBufferMemory

memory = ConversationBufferMemory(memory_key=MEMORY_KEY, return_messages=True)
agent = OpenAIFunctionsAgent(llm=llm, tools=tools, prompt=prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, memory=memory, verbose=True)
agent_executor.run("单词“educa”中有多少个字母?")
agent_executor.run("那是一个真实的单词吗？")