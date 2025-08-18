import akshare as ak
import numpy as np
import pandas as pd
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import MessagesState, StateGraph, START, END
from matplotlib import pyplot as plt
import matplotlib as mpl
import os
from langchain_openai import ChatOpenAI
from typing_extensions import Literal

#保存财报数据
def save_financial_report(report_date):
    df = ak.stock_yjbb_em(date=report_date)
    df.to_csv('../excluded_folders/xingyunyang01_geek02/lesson32/financial_report.csv')

def load_df(file: str) -> pd.DataFrame:
    df = pd.read_csv(file)
    if df.empty:
        raise Exception("文件不存在")
    df['日期'] = pd.to_datetime(df['日期'])
    df['股票代码'] = df['股票代码'].astype(str)
    return df

@tool
def analyze_stocks(stock_codes: list[str], start_date: str, end_date: str) -> pd.DataFrame:
    """
    根据股票代码列表获取股票的起始价格，结束价格，区间涨跌幅，最大回撤，年化波动率

    Parameters:
    -----------
    stock_codes : list
        股票代码列表
    """
    # 先筛选出来指定的代码、指定时间范围的记录
    df = load_df('../excluded_folders/xingyunyang01_geek02/lesson31/total_20230101_20250812.csv')
    # 转换日期格式
    df['日期'] = pd.to_datetime(df['日期'])
    # 创建结果列表
    all_results = []
    # 创建图表
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
    plt.rcParams['axes.unicode_minus'] = False
    mpl.rcParams['font.family'] = 'sans-serif'
    plt.figure(figsize=(15, 8))
    # 转换日期参数
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    # 为每个股票代码进行分析
    for stock_code in stock_codes:
        try:
            stock_data = df[df['股票代码'].astype(str).str.zfill(6) == stock_code].copy()
            if stock_data.empty:
                print(f"警告: 在未找到股票: {stock_code}")
                continue
            # 筛选日期范围
            stock_data = stock_data[(stock_data['日期'] >= start_date) & (stock_data['日期'] <= end_date)]
            if len(stock_data) < 2:  # 确保至少有两条数据
                print(f"警告: 在指定日期范围内数据不足: {stock_code}")
                continue
            # 按日期排序
            stock_data = stock_data.sort_values('日期')
            # 计算日收益率
            stock_data['日收益率'] = stock_data['收盘'].pct_change()
            # 计算年化波动率 (假设一年252个交易日)
            volatility = stock_data['日收益率'].std() * np.sqrt(252) * 100
            # 计算区间涨跌幅
            start_price = stock_data.iloc[0]['收盘']
            end_price = stock_data.iloc[-1]['收盘']
            total_return = (end_price - start_price) / start_price * 100
            # 计算最大回撤
            stock_data['max_price'] = stock_data['收盘'].cummax()
            stock_data['min_price'] = stock_data['收盘'].cummin()
            stock_data['drawdown'] = (stock_data['max_price'] - stock_data['min_price']) / stock_data['max_price'] * 100
            max_drawdown = stock_data['drawdown'].max()
            # 添加到结果列表
            all_results.append({
                '股票代码': stock_code,
                '起始价格': start_price,
                '结束价格': end_price,
                '区间涨跌幅(%)': total_return,
                '最大回撤(%)': max_drawdown,
                '年化波动率(%)': volatility
            })
            # 绘制股价走势图
            plt.plot(stock_data['日期'], stock_data['收盘'], label=f'{stock_code}')
            # 添加关键价格标注
            plt.annotate(f'{stock_code} 起始价: {start_price:.2f}',
                         xy=(stock_data['日期'].iloc[0], start_price),
                         xytext=(10, 10), textcoords='offset points')
            plt.annotate(f'{stock_code} 结束价: {end_price:.2f}',
                         xy=(stock_data['日期'].iloc[-1], end_price),
                         xytext=(10, -10), textcoords='offset points')
            # 标注最大回撤点
            max_drawdown_idx = stock_data['drawdown'].idxmax()
            if max_drawdown_idx is not None and max_drawdown_idx in stock_data.index:
                plt.annotate(f'{stock_code} 最大回撤: {max_drawdown:.2f}%',
                             xy=(stock_data.loc[max_drawdown_idx, '日期'], stock_data.loc[max_drawdown_idx, '收盘']),
                             xytext=(10, -10), textcoords='offset points')
        except Exception as e:
            print(f"处理股票 {stock_code} 时出错: {str(e)}")
            continue
    if not all_results:
        raise ValueError("没有找到任何有效的股票数据")
    # 创建结果DataFrame
    results = pd.DataFrame(all_results)
    # 保存结果到CSV
    results.to_csv('../excluded_folders/xingyunyang01_geek02/lesson32/stocks_analysis.csv', index=False, encoding='utf-8-sig')
    # 完善图表
    plt.title(f'股价走势图 ({start_date.strftime("%Y-%m-%d")} 至 {end_date.strftime("%Y-%m-%d")})')
    plt.xlabel('日期')
    plt.ylabel('价格')
    plt.grid(True)
    plt.legend()
    # 调整x轴日期显示
    plt.gcf().autofmt_xdate()
    # 保存图表
    plt.savefig('../excluded_folders/xingyunyang01_geek02/lesson32/stocks_price_chart.png', dpi=300, bbox_inches='tight')
    plt.close()
    return results

@tool
def get_financial_report(stock_codes: list[str]):
     """
    根据股票代码列表获取财报数据

    Parameters:
    -----------
    stock_codes : list
        股票代码列表

    Returns:
    --------
    dict
        包含每个股票代码对应的财报数据的字典
    """
     # 读取CSV文件
     df = pd.read_csv('../excluded_folders/xingyunyang01_geek02/lesson32/financial_report.csv')
     print("从本地文件读取数据成功")
     # 确保股票代码列是字符串类型
     df['股票代码'] = df['股票代码'].astype(str).str.zfill(6)
     # 创建结果字典
     result = {}
     # 为每个股票代码获取数据
     for code in stock_codes:
         # 确保股票代码格式一致（6位数字）
         code = str(code).zfill(6)
         # 筛选该股票的数据
         stock_data = df[df['股票代码'] == code]
         if not stock_data.empty:
             # 将数据转换为字典格式，包含列名
             result[code] = {
                 'data': stock_data.to_dict('records')
             }
         else:
             result[code] = {
                 'data': []
             }
     return result

def DeepSeekV3():
    return ChatOpenAI(
        model= "deepseek-chat",
        api_key= os.environ.get("DEEPSEEK_API_KEY_TEST"),
        base_url="https://api.deepseek.com",
    )

def Tongyi():
    return ChatOpenAI(
        model="qwen-max",
        api_key=os.environ.get("TONGYI_API_KEY"),  # 自行搞定  你的秘钥
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )

def DeepSeekR1():
    return ChatOpenAI(
        model= "deepseek-reasoner",
        api_key= os.environ.get("DEEPSEEK_API_KEY_TEST"),
        base_url="https://api.deepseek.com",
    )

tools = [get_financial_report, analyze_stocks]
tools_by_name = {tool.name: tool for tool in tools}
deepseek_r1 = DeepSeekR1()
deepseek_v3 = DeepSeekV3()
llm_with_tools = deepseek_r1.bind_tools(tools)

class State(MessagesState):
    plan: str

PLAN_PROMPT = '''
你是一个金融分析师，擅长使用工具对股票，上市公司财报等进行分析。请为用户提出的问题创建分析方案步骤：

可调用工具列表：
get_financial_report:
    根据股票代码列表获取财报数据
    
    Parameters:
    -----------
    stock_codes : list
        股票代码列表
    
    Returns:
    --------
    dict
        包含每个股票代码对应的财报数据的字典

analyze_stocks:
   根据股票代码列表获取股票的起始价格，结束价格，区间涨跌幅，最大回撤，年化波动率
    
    Parameters:
    -----------
    stock_codes : list
        股票代码列表

    Returns:
    --------
    DataFrame
        包含每个股票代码对应的起始价格，结束价格，区间涨跌幅，最大回撤，年化波动率

要求：
1.用中文列出清晰步骤
2.每个步骤标记序号
3.明确说明需要分析和执行的内容
4.只需输出计划内容，不要做任何额外的解释和说明
5.设计的方案步骤要紧紧贴合我的工具所能返回的内容，不要超出工具返回的内容
'''

def plan_node(state: State):
    prompt = PLAN_PROMPT
    response = deepseek_r1.invoke([SystemMessage(content=prompt), state["messages"][0]])
    state["plan"] = response.content
    print(state)
    return state

def llm_call(state: State):
    messages = [SystemMessage(content=f"""你是一个思路清晰，有条理的金融分析师，必须严格按照以下金融分析计划执行： 
    当前金融分析计划：
    {state["plan"]}
    
    如果你认为计划已经执行到最后一步了，请在内容的末尾加上\nFinal Answer字样
    
    示例：
    分析报告xxxxxxxx
    Final Answer
    """)] + state['messages']

    print("------messages[-1]-------")
    print(state["messages"][-1])
    print("------------------")

    response = llm_with_tools.invoke(messages)
    state['messages'].append(response)
    return state

def tool_node(state):
    """Performs the tool call"""
    for tool_call in state["messages"][-1].tool_calls:
        tool = tools_by_name[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])
        # 将观察结果转换为字符串格式
        if isinstance(observation, list):
            # 如果是列表，将其转换为字符串表示
            observation = str(observation)
        state["messages"].append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))
    return state


def should_continue(state: State) -> Literal["environment", "END"]:
    message = state['messages']
    last_message = message[-1]
    if "Final Answer" in last_message.content:
        return "END"
    return "Action"


if __name__ == '__main__':
    agent_builder = StateGraph(State)
    agent_builder.add_node("plan_node", plan_node)
    agent_builder.add_node("llm_call", llm_call)
    agent_builder.add_node("environment", tool_node)

    agent_builder.add_edge(START, "plan_node")
    agent_builder.add_edge("plan_node", "llm_call")
    agent_builder.add_conditional_edges("llm_call", should_continue, {"Action":"environment", "END":END})
    agent_builder.add_edge("environment", "llm_call")
    agent = agent_builder.compile()

    messages = [HumanMessage(content="对比一下 '000333', '600600', '002461', '000729', '600573' 这四只股票的股价表现和财务情况，哪家更值得投资")]
    ret = agent.invoke({"plan": "", "messages": messages})
    print(ret["messages"][-1].content)