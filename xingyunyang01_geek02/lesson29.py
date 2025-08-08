import akshare as ak
import pandas as pd

csv_file = "../excluded_folders/xingyunyang01_geek02/300750.csv"
stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol="300750", period="daily", start_date="20250407", end_date='20250807', adjust="qfq")
print(stock_zh_a_hist_df)
stock_zh_a_hist_df['日期'] = pd.to_datetime(stock_zh_a_hist_df['日期'])
stock_zh_a_hist_df.set_index("日期", inplace=True)
stock_zh_a_hist_df.sort_index(ascending=False, inplace=True)

r = stock_zh_a_hist_df.to_csv(csv_file)
print(stock_zh_a_hist_df.dtypes)