from langchain_openai import OpenAI

llm = OpenAI(model_name="text-davinci-003")
# print(llm("Tell me a Joke"))

print(llm.max_tokens)

llm.max_tokens = 1024
print(llm.max_tokens)

from langchain_openai import ChatOpenAI
chat_model = ChatOpenAI(model_name="gpt-3.5-turbo")

from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
messages = [SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content="Who won the world series in 2020?"),
            AIMessage(content="The Los Angeles Dodgers won the World Series in 2020."),
            HumanMessage(content="Where was it played?")]
chat_result = chat_model(messages)
print(chat_result)
type(chat_result)