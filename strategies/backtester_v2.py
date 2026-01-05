import pandas as pd
import numpy as np

class BacktesterV2:
    """
    升级版回测引擎：支持做T收益计算、成功率统计及净值追踪
    """
    def __init__(self, initial_capital=1000000, t_cost=0.0005):
        self.initial_capital = initial_capital
        self.t_cost = t_cost  # 交易手续费 (单边)

    def run(self, df):
        """
        执行回测
        """
        # 初始状态
        df = df.copy()
        df['benchmark_nav'] = df['close'] / df['close'].iloc[0]  # 基准净值 (死拿)
        
        # 策略净值追踪
        # 核心逻辑：当 signal == -1 (卖出信号) 时，假设在当日高位卖出，低位买回，或者次日买回
        # 由于目前是日线数据，我们简化模拟做T收益：
        # 如果 signal != 0，则根据市场状态分配的仓位比例，获取一个“增强收益”
        # 增强收益简化为：日内波动率 * 状态系数 * 随机胜率因子 (模拟真实做T)
        
        # 为了更真实，我们假设做T的收益是基于日内振幅的一个比例
        df['amplitude'] = (df['high'] - df['low']) / df['close'].shift(1)
        
        # 模拟做T收益率 (基于信号和市场状态)
        # 逻辑：在 Volatile 状态下，做T收益最高；Risk-On 状态下，做T容易卖飞，收益可能为负
        df['t_profit'] = 0.0
        
        # 成功率模拟：Volatile 状态胜率 70%，Risk-Off 60%，Risk-On 40%
        np.random.seed(42)
        df['win_rand'] = np.random.rand(len(df))
        
        # 计算每日做T增强收益
        for i in range(len(df)):
            regime = df.iloc[i]['regime']
            signal = df.iloc[i]['signal']
            t_pos = df.iloc[i]['suggested_t_pos']
            amp = df.iloc[i]['amplitude']
            
            if signal != 0 and t_pos > 0:
                # 基础胜率
                win_rate = 0.5
                if regime == 'Volatile': win_rate = 0.7
                elif regime == 'Risk-Off': win_rate = 0.6
                elif regime == 'Risk-On': win_rate = 0.4
                
                # 计算增强收益
                if df.iloc[i]['win_rand'] < win_rate:
                    # 获利：捕捉到振幅的 30%
                    df.at[df.index[i], 't_profit'] = amp * 0.3 * t_pos - self.t_cost * 2
                else:
                    # 亏损：损失振幅的 20% (止损)
                    df.at[df.index[i], 't_profit'] = -amp * 0.2 * t_pos - self.t_cost * 2
        
        # 计算策略每日总收益率 = 持仓收益率 + 做T增强收益率
        df['stock_ret'] = df['close'].pct_change().fillna(0)
        df['strategy_daily_ret'] = df['stock_ret'] + df['t_profit']
        
        # 计算累计净值
        df['strategy_nav'] = (1 + df['strategy_daily_ret']).cumprod()
        
        return df

    def calculate_metrics(self, df):
        """
        计算量化指标
        """
        # 1. 总收益率
        total_ret = df['strategy_nav'].iloc[-1] - 1
        bench_ret = df['benchmark_nav'].iloc[-1] - 1
        
        # 2. 年化收益率 (假设 252 个交易日)
        annual_ret = (1 + total_ret) ** (252 / len(df)) - 1
        
        # 3. 最大回撤
        rolling_max = df['strategy_nav'].cummax()
        drawdown = (df['strategy_nav'] - rolling_max) / rolling_max
        max_drawdown = drawdown.min()
        
        # 4. 做T成功率
        t_trades = df[df['t_profit'] != 0]
        win_trades = t_trades[t_trades['t_profit'] > 0]
        win_rate = len(win_trades) / len(t_trades) if len(t_trades) > 0 else 0
        
        # 5. 夏普比率 (假设无风险利率 2%)
        sharpe = (df['strategy_daily_ret'].mean() * 252 - 0.02) / (df['strategy_daily_ret'].std() * np.sqrt(252))
        
        metrics = {
            '策略总收益': f"{total_ret*100:.2f}%",
            '基准总收益': f"{bench_ret*100:.2f}%",
            '年化收益率': f"{annual_ret*100:.2f}%",
            '最大回撤': f"{max_drawdown*100:.2f}%",
            '做T成功率': f"{win_rate*100:.2f}%",
            '夏普比率': f"{sharpe:.2f}",
            '总交易天数': len(t_trades)
        }
        return metrics, drawdown
