import pandas as pd
import numpy as np

class RegimeDetector:
    """
    市场状态识别模块：识别当前市场处于何种状态
    状态定义：
    1. 风险偏好上升 (Risk-On): 指数趋势向上，成交量放大
    2. 高位震荡 (Volatile): 波动率高，无明显趋势
    3. 系统性回撤 (Risk-Off): 指数破位，趋势向下
    4. 流动性收缩 (Low-Liquidity): 成交额下滑，横盘
    """
    def __init__(self, window=20):
        self.window = window

    def detect(self, df):
        """
        输入包含收盘价和指数价格的 DataFrame
        """
        # 计算移动平均线
        df['ma_index'] = df['index_close'].rolling(window=self.window).mean()
        df['ma_stock'] = df['close'].rolling(window=self.window).mean()
        
        # 计算波动率 (ATR 简化版或标准差)
        df['volatility'] = df['close'].pct_change().rolling(window=self.window).std()
        
        # 计算成交量变化
        df['vol_ma'] = df['volume'].rolling(window=self.window).mean()
        
        # 状态判定逻辑
        conditions = [
            (df['index_close'] > df['ma_index']) & (df['volume'] > df['vol_ma']), # 风险偏好上升
            (df['volatility'] > df['volatility'].rolling(window=60).mean()) & (df['index_close'].diff().abs() < df['index_close'].std()), # 高位震荡
            (df['index_close'] < df['ma_index']), # 系统性回撤
        ]
        choices = ['Risk-On', 'Volatile', 'Risk-Off']
        
        df['regime'] = np.select(conditions, choices, default='Low-Liquidity')
        
        return df
