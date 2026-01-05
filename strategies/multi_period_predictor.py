import pandas as pd
import numpy as np

class MultiPeriodPredictor:
    """
    多周期预测引擎：
    1. 月线定趋势
    2. 周线定区间
    3. 日线定买卖点
    4. 预测次日关键买卖价格
    """
    def __init__(self):
        pass

    def analyze_trend(self, df):
        """
        分析趋势：返回 1 (多头), -1 (空头), 0 (震荡)
        """
        ma5 = df['close'].rolling(5).mean()
        ma20 = df['close'].rolling(20).mean()
        if ma5.iloc[-1] > ma20.iloc[-1]:
            return 1
        elif ma5.iloc[-1] < ma20.iloc[-1]:
            return -1
        return 0

    def get_volatility_range(self, df, window=14):
        """
        使用 ATR 计算波动率区间
        """
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        atr = true_range.rolling(window).mean().iloc[-1]
        return atr

    def predict_next_day(self, daily_df, weekly_df, monthly_df):
        """
        综合多周期数据预测次日操作
        """
        # 1. 趋势共振分析
        m_trend = self.analyze_trend(monthly_df)
        w_trend = self.analyze_trend(weekly_df)
        d_trend = self.analyze_trend(daily_df)
        
        # 2. 计算波动率和枢轴点
        atr = self.get_volatility_range(daily_df)
        last_close = daily_df['close'].iloc[-1]
        
        # 优化预测逻辑：使用更保守的波动率区间以提高成功率
        # 预测买入价：昨日收盘价 - 0.3 * ATR (更易成交且安全)
        # 预测卖出价：昨日收盘价 + 0.3 * ATR
        buy_price = last_close - 0.25 * atr
        sell_price = last_close + 0.25 * atr
        
        prediction = {
            'date': daily_df.index[-1],
            'trend_m': m_trend,
            'trend_w': w_trend,
            'trend_d': d_trend,
            'action': 'Wait',
            'buy_price': buy_price,
            'sell_price': sell_price
        }
        
        # 高胜率过滤逻辑：
        # 只有当月线、周线、日线三者趋势共振时，才进行积极操作
        if m_trend == w_trend == d_trend and m_trend != 0:
            if m_trend == 1:
                prediction['action'] = 'BuyFirst'
            else:
                prediction['action'] = 'SellFirst'
        else:
            # 趋势不明确时，保持观望或极窄幅震荡
            prediction['action'] = 'Wait'
            
        return prediction
