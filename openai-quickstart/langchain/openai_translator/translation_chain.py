from langchain.schema import AIMessage, HumanMessage, SystemMessage
# 导入 Chat Model 即将使用的 Prompt Templates
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

# 翻译任务指令始终由 System 角色承担
template = (
    """You are a translation expert, proficient in various languages. \n
    Translates English to Chinese."""
)
system_message_prompt = SystemMessagePromptTemplate.from_template(template)
print(system_message_prompt)

# 待翻译文本由 Human 角色输入
human_template = "{text}"
human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
print(human_message_prompt)

# 使用 System 和 Human 角色的提示模板构造 ChatPromptTemplate
chat_prompt_template = ChatPromptTemplate.from_messages(
    [system_message_prompt, human_message_prompt]
)
print(chat_prompt_template)

# 生成用于翻译的 Chat Prompt
chat_prompt_template.format_prompt(text="I love programming.")


# 生成聊天模型真正可用的消息记录 Messages
chat_prompt = chat_prompt_template.format_prompt(text="I love programming.").to_messages()
print(chat_prompt)


from langchain.chat_models import ChatOpenAI

# 为了翻译结果的稳定性，将 temperature 设置为 0
translation_model = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
translation_result = translation_model(chat_prompt)
print(translation_result)
# 查看翻译结果
print(translation_result.content)



from langchain.chains import LLMChain

# 无需再每次都使用 to_messages 方法构造 Chat Prompt
translation_chain = LLMChain(llm=translation_model, prompt=chat_prompt_template)
# 等价于 translation_result.content (字符串类型)
chain_result = translation_chain.run({'text': "I love programming."})
print(chain_result)
translation_chain.run({'text': "I love AI and Large Language Model."})
translation_chain.run({'text': "[Fruit, Color, Price (USD)] [Apple, Red, 1.20] [Banana, Yellow, 0.50] [Orange, Orange, 0.80] [Strawberry, Red, 2.50] [Blueberry, Blue, 3.00] [Kiwi, Green, 1.00] [Mango, Orange, 1.50] [Grape, Purple, 2.00]"})


# System 增加 source_language 和 target_language
template = (
    """You are a translation expert, proficient in various languages. \n
    Translates {source_language} to {target_language}."""
)
system_message_prompt = SystemMessagePromptTemplate.from_template(template)
# 待翻译文本由 Human 角色输入
human_template = "{text}"
human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
# 使用 System 和 Human 角色的提示模板构造 ChatPromptTemplate
m_chat_prompt_template = ChatPromptTemplate.from_messages(
    [system_message_prompt, human_message_prompt]
)
m_translation_chain = LLMChain(llm=translation_model, prompt=m_chat_prompt_template)
m_translation_chain.run({
    "source_language": "Chinese",
    "target_language": "English",
    "text": "我喜欢学习大语言模型，轻松简单又愉快",
})
m_translation_chain.run({
    "source_language": "Chinese",
    "target_language": "Japanese",
    "text": "我喜欢学习大语言模型，轻松简单又愉快",
})