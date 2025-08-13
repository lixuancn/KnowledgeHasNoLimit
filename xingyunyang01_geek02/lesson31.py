import os
import re

import pandas as pd
import akshare as ak
import asyncio

async def load_data(symbol: str, start_date: str, end_date: str):
    """
    加载指定时间段的A股历史数据

    参数:
    symbol (str): 股票代码，如'600000'
    start_date (str): 开始日期，格式如'YYYYMMDD'
    end_date (str): 结束日期，格式如'YYYYMMDD'

    返回:
    pandas.DataFrame: 包含日期、开盘价、最高价、最低价、收盘价和成交量的数据，按日期倒序排列
    """
    loop = asyncio.get_event_loop()
    # 调用akshare获取A股历史数据
    df = await loop.run_in_executor(None, lambda: ak.stock_zh_a_hist(
            symbol=symbol,
            period="daily",
            start_date=start_date,
            end_date=end_date,
            adjust="qfq",  # 使用前复权数据
            timeout=10
        )
    )
    # 将日期列转换为datetime类型并设置为索引
    if df.empty or df['日期'].empty:
        return pd.DataFrame()
    df['日期'] = pd.to_datetime(df['日期'])
    # 按日期倒序排列并设置日期为索引
    df.set_index('日期', inplace=True)
    df.sort_values(by='日期', ascending=False, inplace=True)
    return df

async def save_data(codes: list[str], start_date: str, end_date: str, file_prefix: int):
    """
    遍历股票代码列表，获取数据并合并写入CSV文件

    参数:
    codes (list): 股票代码列表，如['600000', '600036']
    start_date (str): 开始日期，格式如'YYYYMMDD'
    end_date (str): 结束日期，格式如'YYYYMMDD'
    """
    # 初始化空DataFrame用于存储所有数据
    all_data = pd.DataFrame()
    task_list = []
    # 遍历股票代码列表
    for symbol in codes:
        # 调用load_data获取单只股票数据
        task = asyncio.create_task(load_data(symbol, start_date, end_date))
        task_list.append(task)
    rets = await asyncio.gather(*task_list)
    for ret in rets:
        # 合并数据
        all_data = pd.concat([all_data, ret], axis=0)
    # 构造文件路径
    file_path = f"../excluded_folders/xingyunyang01_geek02/lesson31/{file_prefix}_{start_date}_{end_date}.csv"
    # 写入CSV文件
    all_data.to_csv(file_path)

def get_all_codes() -> list[str]:
    """
    获取A股市场中代码以60、30、00或68开头的股票代码列表

    返回:
    list[str]: 符合条件的股票代码列表
    """
    # 获取所有A股实时数据
    df = ak.stock_zh_a_spot_em()
    # 筛选代码以60、30、00或68开头的股票
    mask = df['代码'].str.startswith(('60', '30', '00', '68'))
    filtered_codes = df.loc[mask, '代码'].tolist()
    return filtered_codes

def save_all_date():
    """
    获取所有股票代码并分组调用save_data保存20230101至20250812的历史数据
    """
    # 获取所有符合条件的股票代码
    codes = get_all_codes()
    print(f"共获取到{len(codes)}个股票代码，开始分组处理...")
    # 将股票代码分成每组100个
    group_size = 100
    groups = [codes[i:i+group_size] for i in range(0, len(codes), group_size)]

    # 遍历每个组并调用save_data
    for i, group in enumerate(groups):
        if i < 50:
            continue
        print(f"正在处理第{i+1}/{len(groups)}组，共{len(group)}个股票代码")
        asyncio.run(save_data(group, "20230101", "20250812", i))


def load_df(file: str) -> pd.DataFrame:
    df = pd.read_csv("../excluded_folders/xingyunyang01_geek02/lesson31/{}".format(file))
    if df.empty:
        raise Exception("文件不存在")
    df['日期'] = pd.to_datetime(df['日期'])
    df['股票代码'] = df['股票代码'].astype(str)
    return df

def concat_csv(file_name: str):
    folder_path = '../excluded_folders/xingyunyang01_geek02/lesson31/'
    # 列出文件夹中的所有文件和目录
    files = os.listdir(folder_path)
    # 定义一个正则表达式，匹配以数字开头的文件名
    pattern = re.compile(r'^\d+_.+\.csv$')
    # 遍历文件，筛选出符合条件的文件名
    filtered_files = [file for file in files if pattern.match(file)]
    ret = pd.DataFrame()
    # 打印结果
    for file in filtered_files:
        df = load_df(file)
        ret = pd.concat([ret, df])
    ret.to_csv("../excluded_folders/xingyunyang01_geek02/lesson31/{}".format(file_name))
    print("合并完成,文件名是{}".format(file_name))

def join_csv(file1:str, file2:str):
    cols = ['股票代码','日期','收盘']
    df1 = load_df(file1).loc[:, cols]
    df2 = load_df(file2).loc[:, cols]
    df = pd.concat([df1, df2], axis=0)
    df.sort_values(['股票代码', '日期'], ascending=False, inplace=True)
    df.drop_duplicates(subset=['股票代码', '日期'], keep='first', inplace=True)
    df.reset_index(drop=True, inplace=True)
    print(df)

if __name__ == "__main__":
    # 调用新函数保存所有数据
    # save_all_date()
    # 合并多个csv
    concat_csv("total_20230101_20250812.csv")