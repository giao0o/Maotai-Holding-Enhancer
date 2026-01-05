import pandas as pd
import numpy as np

class MaotaiTStrategy:
    """
    茅台持仓增强策略 (Maotai Holding Enhancer)
    核心逻辑：
    1. 根据市场状态决定是否做T
    2. 在适合做T的状态下，利用日内波动率和微结构规律生成信号
    3. 目标是降低持仓成本，而非单纯预测涨跌
    """
    def __init__(self, config=None):
        self.config = config or {
            'risk_on_t_ratio': 0.2,    # 趋势向上时，仅用20%仓位做T
            'volatile_t_ratio': 0.5,   # 震荡市，用50%仓位做T
            'risk_off_t_ratio': 0.8,   # 弱势市，用80%仓位做T或对冲
            'stop_loss': -0.015,       # 日内止损
            'take_profit': 0.02        # 日内止盈
        }

    def generate_signals(self, df):
        """
        生成交易信号
        """
        # 基础信号：基于布林带或 RSI 的日内超买超卖
        df['ma'] = df['close'].rolling(window=20).mean()
        df['std'] = df['close'].rolling(window=20).std()
        df['upper'] = df['ma'] + 2 * df['std']
        df['lower'] = df['ma'] - 2 * df['std']
        
        # 信号逻辑
        df['signal'] = 0
        
        # 卖出信号 (做T的卖出动作)：价格触及上轨且处于震荡或弱势状态
        df.loc[(df['close'] > df['upper']) & (df['regime'].isin(['Volatile', 'Risk-Off'])), 'signal'] = -1
        
        # 买入信号 (做T的买回动作)：价格触及下轨
        df.loc[(df['close'] < df['lower']), 'signal'] = 1
        
        # 根据市场状态调整建议仓位
        df['suggested_t_pos'] = 0.0
        df.loc[df['regime'] == 'Risk-On', 'suggested_t_pos'] = self.config['risk_on_t_ratio']
        df.loc[df['regime'] == 'Volatile', 'suggested_t_pos'] = self.config['volatile_t_ratio']
        df.loc[df['regime'] == 'Risk-Off', 'suggested_t_pos'] = self.config['risk_off_t_ratio']
        
        return df

class Backtester:
    """
    简易回测引擎
    """
    def __init__(self, initial_capital=1000000):
        self.initial_capital = initial_capital

    def run(self, df):
        # 假设初始持仓 1000 股茅台
        shares = 1000
        cash = 0
        
        df['hold_value'] = shares * df['close']
        df['strategy_value'] = df['hold_value']
        
        # 模拟做T收益 (简化版：信号触发时按收盘价计算)
        # 实际中应使用分钟线，这里先实现日线逻辑框架
        df['daily_ret'] = df['close'].pct_change()
        
        # 记录策略表现
        df['strategy_ret'] = df['daily_ret'] # 默认跟随持仓
        
        # 如果有卖出信号，且状态允许，则减少持仓，等待买回
        # 这里的逻辑是：如果 signal == -1，则卖出 suggested_t_pos 比例的仓位
        # 并在 signal == 1 时买回。
        
        return df
