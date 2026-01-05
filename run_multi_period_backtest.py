import pandas as pd
import matplotlib.pyplot as plt
from utils.data_loader import DataLoader
from strategies.multi_period_predictor import MultiPeriodPredictor
from strategies.t_plus_0_backtester import TPlus0Backtester

def run_multi_period_analysis():
    print("=== 茅台持仓增强器：多周期高胜率回测 (v2.0) ===")
    
    # 1. 初始化
    loader = DataLoader()
    predictor = MultiPeriodPredictor()
    backtester = TPlus0Backtester()
    
    # 2. 获取数据 (获取过去两年的数据)
    end_date = pd.Timestamp.now().strftime('%Y%m%d')
    start_date = (pd.Timestamp.now() - pd.Timedelta(days=730)).strftime('%Y%m%d')
    
    daily_df, weekly_df, monthly_df = loader.get_multi_period_data(start_date, end_date)
    
    # 3. 生成每日预测
    # 我们需要模拟真实情况：每天收盘后，基于当时的数据预测明天
    predictions = []
    for i in range(len(daily_df)):
        # 截取到当前日期的数据
        current_date = daily_df.index[i]
        d_sub = daily_df.iloc[:i+1]
        w_sub = weekly_df[weekly_df.index <= current_date]
        m_sub = monthly_df[monthly_df.index <= current_date]
        
        if len(d_sub) < 20 or len(w_sub) < 5 or len(m_sub) < 2:
            # 数据不足，跳过
            predictions.append({'action': 'Wait'})
            continue
            
        pred = predictor.predict_next_day(d_sub, w_sub, m_sub)
        predictions.append(pred)
    
    # 4. 执行回测
    res_df = backtester.run(daily_df, predictions)
    
    # 5. 计算指标
    total_days = len(res_df)
    trade_days = len(res_df[res_df['trade_type'] != 'None'])
    success_trades = len(res_df[res_df['trade_type'].str.contains('Success', na=False)])
    win_rate = success_trades / trade_days if trade_days > 0 else 0
    
    strategy_final = res_df['total_value'].iloc[-1]
    bench_final = res_df['benchmark_value'].iloc[-1]
    alpha = (strategy_final - bench_final) / bench_final
    
    print("\n--- 多周期回测指标 ---")
    print(f"总交易天数: {total_days}")
    print(f"实际做T天数: {trade_days}")
    print(f"做T成功次数: {success_trades}")
    print(f"做T成功率: {win_rate*100:.2f}%")
    print(f"策略最终价值: {strategy_final:.2f}")
    print(f"基准最终价值: {bench_final:.2f}")
    print(f"超额收益 (Alpha): {alpha*100:.2f}%")
    
    # 6. 可视化
    plt.figure(figsize=(14, 7))
    plt.plot(res_df.index, res_df['benchmark_value'], label='Benchmark (Hold + Cash)', color='gray', alpha=0.6)
    plt.plot(res_df.index, res_df['total_value'], label='Strategy (Multi-Period T+0)', color='red', linewidth=2)
    plt.title('Maotai Multi-Period T+0 Strategy: 2-Year Backtest')
    plt.ylabel('Total Asset Value')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('multi_period_backtest.png')
    
    # 输出明日预测 (示例)
    latest_pred = predictions[-1]
    print("\n--- 明日操作预测 ---")
    print(f"预测日期: {pd.Timestamp.now().strftime('%Y-%m-%d')}")
    print(f"建议动作: {latest_pred['action']}")
    if latest_pred['buy_price']:
        print(f"建议买入价: {latest_pred['buy_price']:.2f}")
        print(f"建议卖出价: {latest_pred['sell_price']:.2f}")

if __name__ == "__main__":
    run_multi_period_analysis()
