from langchain import PromptTemplate


prompt_template = PromptTemplate.from_template(
    "Tell me a {adjective} joke about {content}."
)

# 使用 format 生成提示
prompt = prompt_template.format(adjective="funny", content="chickens")
print(prompt)
print(prompt_template)

prompt_template = PromptTemplate.from_template(
    "Tell me a joke"
)
# 生成提示
prompt = prompt_template.format()
print(prompt)
print(prompt_template)

print("---------")

valid_prompt = PromptTemplate(
    input_variables=["adjective", "content"],
    template="Tell me a {adjective} joke about {content}."
)
print(valid_prompt)
print(valid_prompt.format(adjective="funny", content="chickens"))


prompt_template = PromptTemplate.from_template(
    "讲{num}个给程序员听得笑话"
)
prompt = prompt_template.format(num=2)
print(prompt)
print(f"prompt: {prompt}")
from langchain_openai import OpenAI
llm = OpenAI(model_name="text-davinci-003", max_tokens=1000)
result = llm(prompt)
print(f"result: {result}")