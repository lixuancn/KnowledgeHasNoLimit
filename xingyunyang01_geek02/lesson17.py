from typing import List

from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_community.document_loaders import UnstructuredWordDocumentLoader
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

import os

jds = """1. 岗位名称: AI应用开发专家TAM
公司名称: 阿里云
岗位要求: 岗位职责:
1. 基于阿里云大模型，支撑阿里云客户构建创新AI应用。帮助客户进行大模型的微调、再训练、模型评测、提示词优化等工作。
2. 负责帮助客户治理企业已有数据资产，进行数据集建设和知识工程加工。
3. 负责结合行业特点和业务场景，完成算法的工程化实现，沉淀可复用的AI应用资产。
4. 调研最新业界和学术界成果，对前沿AI应用方向进行持续探索。
任职要求：
1. 研究生及以上学历，计算机相关专业
2. 精通Python、JAVA或C++开发语言，3年以上算法开发经验，掌握数据处理、知识工程、算法选型、算法优化，开发及上线测试的全链路能力
3. 参与过完整的算法实现项目，有云计算&大模型对口行业实战算法项目经验加分
4. 有国产GPU适配经验者优先
加分项：
1. 有阿里云ACE认证者优先
2. 熟练使用阿里云AI大模型、AI开发平台产品、大数据产品者优先
3. 具备流利的英语会话能力者优先
技能要求: Golang,Java,PostgreSQL,机器学习经验,Redis,Numpy,PyTorch,MySQL,MongoDB,架构设计经验,Python,Kubernetes,TensorFlow
薪资待遇: 30-50K"""

ResumePrompt = """
你是一个 AI 简历助手。我会给你提供我的简历以及某公司的详细岗位要求。你的任务是根据公司的岗位要求, 帮我改写和完善我的简历，使我的简历符合该公司的要求。

简历：
{resume}

岗位要求：
{input}
"""

ResumePrompt2 = """
你是一个 AI 简历助手。我会给你提供我的简历以及某公司的详细岗位要求。你的任务是根据公司的岗位要求, 帮我改写和完善我的简历，使我的简历符合该公司的要求。
此外，我还会给你一个简历模板，模板中会包含简历中部分内容的大纲，当你匹配到我的简历中有模板提及的内容时，要按照我模板的格式进行编写。

简历：
{resume}

简历模板：
专业技能
  请在此描述符合职位要求的技能，尤其是编程技能

项目经验
 (1) 项目描述
 (2) 我在项目中的角色
 (3) 项目规模
 (4) 技术堆栈
 (5) 已开发模块的描述
 (6) 解决难题的经验

岗位要求：
{input}
"""


# 加载 职位描述
def load_jobs() -> str:
    return jds


def load_doc() -> list:
    word = UnstructuredWordDocumentLoader('../excluded_folders/xingyunyang01_geek02/zhangsan_resume.docx')
    docs = word.load()
    return docs


def fix_resume():
    prompt = PromptTemplate.from_template(ResumePrompt2)
    llm = DeepSeekR1()
    docs = load_doc()
    print(prompt)
    print(llm)
    print(docs)
    chain = {
                "resume": lambda _: docs,
                "input": RunnablePassthrough()
            } | prompt | llm | StrOutputParser()
    ret = chain.invoke(load_jobs())
    print(ret)


def DeepSeekR1():
    return ChatOpenAI(
        model="deepseek-reasoner",
        api_key=os.environ.get("DEEPSEEK_API_KEY_TEST"),
        base_url="https://api.deepseek.com"
    )


if __name__ == '__main__':
    fix_resume()
