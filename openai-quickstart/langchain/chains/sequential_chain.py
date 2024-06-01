from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate

llm = OpenAI(temperature=0.9, max_tokens=500)

prompt = PromptTemplate(
    input_variables=["product"],
    template="给制造{product}的有限公司取10个好名字，并给出完整的公司名称",
)

from langchain.chains import LLMChain

chain = LLMChain(llm=llm, prompt=prompt)
print(chain.run({
    'product': "性能卓越的GPU"
    }))


chain.verbose = True
print(chain.run({
    'product': "性能卓越的GPU"
    }))


# 这是一个 LLMChain，用于根据剧目的标题撰写简介。
llm = OpenAI(temperature=0.7, max_tokens=1000)
template = """你是一位剧作家。根据戏剧的标题，你的任务是为该标题写一个简介。
标题：{title}
剧作家：以下是对上述戏剧的简介："""
prompt_template = PromptTemplate(input_variables=["title"], template=template)
synopsis_chain = LLMChain(llm=llm, prompt=prompt_template)

# 这是一个LLMChain，用于根据剧情简介撰写一篇戏剧评论。
# llm = OpenAI(temperature=0.7, max_tokens=1000)
template = """你是《纽约时报》的戏剧评论家。根据剧情简介，你的工作是为该剧撰写一篇评论。
剧情简介：
{synopsis}
以下是来自《纽约时报》戏剧评论家对上述剧目的评论："""
prompt_template = PromptTemplate(input_variables=["synopsis"], template=template)
review_chain = LLMChain(llm=llm, prompt=prompt_template)

# 这是一个SimpleSequentialChain，按顺序运行这两个链
from langchain.chains import SimpleSequentialChain
overall_chain = SimpleSequentialChain(chains=[synopsis_chain, review_chain], verbose=True)
review = overall_chain.run("三体人不是无法战胜的")
print(review)
review = overall_chain.run("星球大战第九季")
print(review)



# # 这是一个 LLMChain，根据剧名和设定的时代来撰写剧情简介。
llm = OpenAI(temperature=.7, max_tokens=1000)
template = """你是一位剧作家。根据戏剧的标题和设定的时代，你的任务是为该标题写一个简介。
标题：{title}
时代：{era}
剧作家：以下是对上述戏剧的简介："""
prompt_template = PromptTemplate(input_variables=["title", "era"], template=template)
# output_key
synopsis_chain = LLMChain(llm=llm, prompt=prompt_template, output_key="synopsis", verbose=True)

# 这是一个LLMChain，用于根据剧情简介撰写一篇戏剧评论。

template = """你是《纽约时报》的戏剧评论家。根据该剧的剧情简介，你需要撰写一篇关于该剧的评论。
剧情简介：
{synopsis}
来自《纽约时报》戏剧评论家对上述剧目的评价："""
prompt_template = PromptTemplate(input_variables=["synopsis"], template=template)
review_chain = LLMChain(llm=llm, prompt=prompt_template, output_key="review", verbose=True)

from langchain.chains import SequentialChain
m_overall_chain = SequentialChain(
    chains=[synopsis_chain, review_chain],
    input_variables=["era", "title"],
    # Here we return multiple variables
    output_variables=["synopsis", "review"],
    verbose=True)
m_overall_chain({"title":"三体人不是无法战胜的", "era": "二十一世纪的新中国"})