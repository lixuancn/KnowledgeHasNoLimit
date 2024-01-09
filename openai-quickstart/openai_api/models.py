import os
from openai import OpenAI
client = OpenAI()

models = client.models.list()
model_list = [model.id for model in models.data]
print(model_list)

gpt3 = client.models.retrieve("text-davinci-003")
print(gpt3)


# completions
data = client.completions.create(
  model="text-davinci-003",
  prompt="Say this is a test",
  max_tokens=7,
  temperature=0
)

# 聊天模式
messages=[
    {
        "role": "user",
        "content": "Hello!"
    }
]
data = client.chat.completions.create(
  model="text-davinci-003",
  messages=messages
)
messages.append(data.choices[0].message)