import pandas as pd
import numpy as np

class TPlus0Backtester:
    """
    双向做T回测引擎：
    1. 保持持股数不变 (100股)
    2. 支持先买后卖 (正T) 和 先卖后买 (反T)
    3. 计算做T产生的现金差额 (即增强收益)
    """
    def __init__(self, initial_shares=100, initial_cash_multiplier=1.0, fee=0.0002):
        self.initial_shares = initial_shares
        self.fee = fee # 调低手续费至万二，更符合大资金实盘情况
        # 假设手中还有等值于 100 股茅台的现金
        self.initial_cash = None # 将在运行中根据第一天价格初始化

    def run(self, daily_df, predictions):
        """
        predictions: 每日预测结果的列表
        """
        results = []
        shares = self.initial_shares
        
        # 初始化现金：等于第一天持仓价值
        cash = shares * daily_df.iloc[0]['close']
        self.initial_cash = cash
        
        # 记录初始总资产
        initial_total_value = cash + shares * daily_df.iloc[0]['close']
        
        # 遍历每一天进行模拟
        # 注意：预测是基于前一天数据，应用于当天
        for i in range(1, len(daily_df)):
            current_date = daily_df.index[i]
            day_data = daily_df.iloc[i]
            
            # 获取针对这一天的预测 (由前一天生成)
            # 在实际回测中，我们需要确保预测只使用 i-1 之前的数据
            pred = predictions[i-1] 
            
            daily_profit = 0
            trade_type = "None"
            
            # 模拟日内交易 (优化成交逻辑：预测区间必须被当日振幅完全覆盖才算成功)
            if pred['action'] == 'BuyFirst':
                # 先买：如果当日最低价触及买入价
                if day_data['low'] <= pred['buy_price']:
                    buy_cost = pred['buy_price'] * 100 * (1 + self.fee)
                    # 尝试卖出：当日最高价必须触及卖出价
                    if day_data['high'] >= pred['sell_price']:
                        sell_revenue = pred['sell_price'] * 100 * (1 - self.fee)
                        daily_profit = sell_revenue - buy_cost
                        trade_type = "BuyFirst_Success"
                    else:
                        # 卖出失败，尾盘强制卖出
                        sell_revenue = day_data['close'] * 100 * (1 - self.fee)
                        daily_profit = sell_revenue - buy_cost
                        trade_type = "BuyFirst_Failed_Close"
            
            elif pred['action'] == 'SellFirst' or pred['action'] == 'RangeT':
                # 先卖：如果当日最高价触及卖出价
                if day_data['high'] >= pred['sell_price']:
                    sell_revenue = pred['sell_price'] * 100 * (1 - self.fee)
                    # 尝试买回：当日最低价必须触及买入价
                    if day_data['low'] <= pred['buy_price']:
                        buy_cost = pred['buy_price'] * 100 * (1 + self.fee)
                        daily_profit = sell_revenue - buy_cost
                        trade_type = "SellFirst_Success"
                    else:
                        # 买回失败，尾盘强制买回
                        buy_cost = day_data['close'] * 100 * (1 + self.fee)
                        daily_profit = sell_revenue - buy_cost
                        trade_type = "SellFirst_Failed_Close"
            
            cash += daily_profit
            
            results.append({
                'date': current_date,
                'close': day_data['close'],
                'trade_type': trade_type,
                'daily_profit': daily_profit,
                'total_cash': cash,
                'stock_value': shares * day_data['close'],
                'total_value': cash + shares * day_data['close']
            })
            
        res_df = pd.DataFrame(results)
        res_df.set_index('date', inplace=True)
        
        # 计算基准：死拿 100 股 + 初始现金
        res_df['benchmark_value'] = self.initial_cash + self.initial_shares * res_df['close']
        
        return res_df
