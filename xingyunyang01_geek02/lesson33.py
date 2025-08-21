import os
import akshare as ak
import pandas as pd
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent


def set_df_hist(code: str, start_date: str, end_date: str):
    csv_file = f"../excluded_folders/xingyunyang01_geek02/lesson33/{code}_hist_{start_date}_{end_date}.csv"
    stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol=code, period="daily", start_date=start_date, end_date=end_date, adjust="qfq")
    stock_zh_a_hist_df['日期'] = pd.to_datetime(stock_zh_a_hist_df['日期'])
    stock_zh_a_hist_df.set_index("日期", inplace=True)
    stock_zh_a_hist_df.sort_index(ascending=False, inplace=True)
    stock_zh_a_hist_df.to_csv(csv_file)

def load_df(file: str) -> pd.DataFrame:
    df = pd.read_csv(file)
    if df.empty:
        raise Exception("文件不存在")
    df['日期'] = pd.to_datetime(df['日期'])
    df['股票代码'] = df['股票代码'].astype(str)
    return df

def calc_vol_ratio_around_date(df: pd.DataFrame, target_date: str, before_days: int = 3, after_days: int = 3) -> float:
    """
    计算目标日期后指定天数成交量与前指定天数成交量的比值
    
    参数:
    df: 包含'日期'和'成交量'列的DataFrame
    target_date: 目标日期字符串，格式如'2024-09-15'
    before_days: 目标日期前的天数，默认为3
    after_days: 目标日期后的天数，默认为3
    
    返回:
    后段时间成交量与前段时间成交量的比值
    """
    target_date = pd.to_datetime(target_date)
    date_mask = df['日期'] == target_date
    if not date_mask.any():
        raise ValueError(f"日期 {target_date} 不在数据范围内")

    # 筛选前后两个时间段的数据
    target_idx = df[date_mask].index[0]
    before_date = df.iloc[target_idx-before_days: target_idx]['成交量']
    after_date = df.iloc[target_idx: target_idx+after_days]['成交量']
    if len(before_date) == before_days and len(after_date) == after_days:
        return after_date.mean() / before_date.mean()
    else:
        raise ValueError(f"日期 {target_date} 附近数据不足{before_days}天或{after_days}天")

@tool
def vol_info(target_date: str):
    """
    计算目标日期后指定天数成交量与前指定天数成交量的比值
    param target_date: str 指定日期，YYYY-MM-DD
    return: float 成交量比值
    """
    df = load_df("../excluded_folders/xingyunyang01_geek02/lesson33/300750_hist_20240901_20240930.csv")
    return calc_vol_ratio_around_date(df, target_date)

@tool
def stock_price(target_date: str):
    """
    计算目标日期后指定天数成交量与前指定天数成交量的比值
    param target_date: str 指定日期，YYYY-MM-DD
    return: float 成交量比值
    """
    df = load_df("../excluded_folders/xingyunyang01_geek02/lesson33/300750_hist_20240901_20240930.csv")
    return calc_price_ratio_around_date(df, target_date)

def calc_price_ratio_around_date(df: pd.DataFrame, target_date: str, before_days: int = 3, after_days: int = 3) -> str:
    """
    计算目标日期后指定天数收盘价与前指定天数收盘价的比值

    参数:
    df: 包含'日期'和'收盘'列的DataFrame
    target_date: 目标日期字符串，格式如'2024-09-15'
    before_days: 目标日期前的天数，默认为3
    after_days: 目标日期后的天数，默认为3

    返回:
    后段时间收盘价与前段时间收盘价的比值
    """
    target_date = pd.to_datetime(target_date)
    date_mask = df['日期'] == target_date
    if not date_mask.any():
        raise ValueError(f"日期 {target_date} 不在数据范围内")

    # 获取目标日期的索引
    target_idx = df[date_mask].index[0]

    # 获取前后的数据并合并
    combined_data = pd.concat([
        df.iloc[target_idx-before_days: target_idx][['日期', '收盘']],
        df.iloc[target_idx: target_idx+after_days][['日期', '收盘']]
    ])
    combined_data['日期'] = combined_data['日期'].dt.strftime('%Y-%m-%d')
    return combined_data.to_string(index=False)

def DeepSeek():
    return ChatOpenAI(
        model="deepseek-chat",
        api_key=os.environ.get("DEEPSEEK_API_KEY_TEST"),  # 自行搞定  你的秘钥
        base_url="https://api.deepseek.com"
    )

if __name__ == '__main__':
    # set_df_hist("300750", "20240901", "20240930")
    # print(vol_info('2024-09-18'))
    # print(stock_price('2024-09-18'))
    llm = DeepSeek()
    pre_built_agent = create_react_agent(llm, tools=[vol_info, stock_price])
    prompt = """
    你是一个股票分析助手，你可以根据用户的问题，使用工具来回答用户的问题。
    工具：
    1. stock_price：获取股票指定日期前三天与后三天（包含指定日期）的收盘价
    2. vol_info：计算指定日期后3天（含指定日期）与前3天的成交量比值
    要求：
    需要分析出股票属于以下量价关系（量增价涨、量增价跌、量缩价涨、量缩价跌）中的哪一种。并给出分析结论
    """
    messages = [SystemMessage(content=prompt), HumanMessage(content="600600这只股票在2024-09-18左右的表现如何？")]
    messages = pre_built_agent.invoke({"messages": messages})
    for m in messages["messages"]:
        m.pretty_print()

