import akshare as ak
import pandas as pd
import os
from datetime import datetime, timedelta

class DataLoader:
    """
    数据加载类：负责从 AkShare 获取茅台及大盘数据
    """
    def __init__(self, symbol="sh600519", index_symbol="sh000300"):
        self.symbol = symbol  # 贵州茅台
        self.index_symbol = index_symbol  # 沪深300

    def get_daily_data(self, start_date, end_date):
        """
        获取日线数据
        """
        print(f"正在获取 {self.symbol} 日线数据...")
        df_stock = ak.stock_zh_a_hist(symbol=self.symbol.replace("sh", ""), period="daily", 
                                     start_date=start_date, end_date=end_date, adjust="qfq")
        df_stock['date'] = pd.to_datetime(df_stock['日期'])
        df_stock.set_index('date', inplace=True)
        
        print(f"正在获取 {self.index_symbol} 指数数据...")
        df_index = ak.stock_zh_index_daily(symbol=self.index_symbol)
        df_index['date'] = pd.to_datetime(df_index['date'])
        df_index.set_index('date', inplace=True)
        
        # 合并数据
        df = df_stock[['开盘', '最高', '最低', '收盘', '成交量']].copy()
        df.columns = ['open', 'high', 'low', 'close', 'volume']
        df['index_close'] = df_index['close']
        
        return df.dropna()

    def get_minute_data(self, period='1'):
        """
        获取分钟级数据 (AkShare 接口通常返回最近几个交易日的数据)
        """
        print(f"正在获取 {self.symbol} {period}分钟线数据...")
        df = ak.stock_zh_a_hist_min_em(symbol=self.symbol.replace("sh", ""), period=period, adjust="qfq")
        df['时间'] = pd.to_datetime(df['时间'])
        df.set_index('时间', inplace=True)
        df.columns = ['open', 'close', 'high', 'low', 'volume', 'amount', 'amplitude', 'pct_chg', 'turnover']
        return df
