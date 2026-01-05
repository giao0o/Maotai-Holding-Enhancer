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

    def get_data(self, period="daily", start_date="20200101", end_date="20260101"):
        """
        获取指定周期的数据 (daily, weekly, monthly)
        """
        print(f"正在获取 {self.symbol} {period} 数据...")
        df = ak.stock_zh_a_hist(symbol=self.symbol.replace("sh", ""), period=period, 
                               start_date=start_date, end_date=end_date, adjust="qfq")
        df['date'] = pd.to_datetime(df['日期'])
        df.set_index('date', inplace=True)
        df = df[['开盘', '最高', '最低', '收盘', '成交量']]
        df.columns = ['open', 'high', 'low', 'close', 'volume']
        return df

    def get_multi_period_data(self, start_date, end_date):
        """
        获取日、周、月多周期数据
        """
        daily = self.get_data("daily", start_date, end_date)
        weekly = self.get_data("weekly", start_date, end_date)
        monthly = self.get_data("monthly", start_date, end_date)
        
        # 获取指数数据作为参考
        index_df = ak.stock_zh_index_daily(symbol=self.index_symbol)
        index_df['date'] = pd.to_datetime(index_df['date'])
        index_df.set_index('date', inplace=True)
        
        daily['index_close'] = index_df['close']
        return daily, weekly, monthly

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
