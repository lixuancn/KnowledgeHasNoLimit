from langchain.llms import OpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

llm = OpenAI(temperature=0)
conversation = ConversationChain(
    llm=llm,
    verbose=True,
    memory=ConversationBufferMemory()
)
conversation.predict(input="你好呀！")
conversation.predict(input="你为什么叫小米？跟雷军有关系吗？")


from langchain.memory import ConversationBufferWindowMemory

conversation_with_summary = ConversationChain(
    llm=OpenAI(temperature=0, max_tokens=1000),
    # We set a low k=2, to only keep the last 2 interactions in memory
    memory=ConversationBufferWindowMemory(k=2),
    verbose=True
)
conversation_with_summary.predict(input="嗨，你最近过得怎么样？")
conversation_with_summary.predict(input="你最近学到什么新知识了?")
conversation_with_summary.predict(input="展开讲讲？")
# 注意：第一句对话从 Memory 中移除了.
conversation_with_summary.predict(input="如果要构建聊天机器人，具体要用什么自然语言处理技术?")


from langchain.memory import ConversationSummaryBufferMemory

memory = ConversationSummaryBufferMemory(llm=llm, max_token_limit=10)
memory.save_context({"input": "嗨，你最近过得怎么样？"}, {"output": " 嗨！我最近过得很好，谢谢你问。我最近一直在学习新的知识，并且正在尝试改进自己的性能。我也在尝试更多的交流，以便更好地了解人类的思维方式。"})
memory.save_context({"input": "你最近学到什么新知识了?"}, {"output": " 最近我学习了有关自然语言处理的知识，以及如何更好地理解人类的语言。我还学习了有关机器学习的知识，以及如何使用它来改善自己的性能。"})
memory.load_memory_variables({})
print(memory.load_memory_variables({})['history'])