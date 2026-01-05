import pandas as pd
import matplotlib.pyplot as plt
from utils.data_loader import DataLoader
from strategies.regime_detector import RegimeDetector
from strategies.maotai_t_strategy import MaotaiTStrategy
from strategies.backtester_v2 import BacktesterV2

def run_analysis():
    print("=== 茅台持仓增强器：近两年深度回测分析 ===")
    
    # 1. 初始化
    loader = DataLoader()
    detector = RegimeDetector()
    strategy = MaotaiTStrategy()
    backtester = BacktesterV2()
    
    # 2. 获取近两年数据 (约 500 个交易日)
    end_date = pd.Timestamp.now().strftime('%Y%m%d')
    start_date = (pd.Timestamp.now() - pd.Timedelta(days=730)).strftime('%Y%m%d')
    
    df = loader.get_daily_data(start_date, end_date)
    
    # 3. 运行策略流水线
    df = detector.detect(df)
    df = strategy.generate_signals(df)
    df = backtester.run(df)
    
    # 4. 计算指标
    metrics, drawdown = backtester.calculate_metrics(df)
    
    print("\n--- 回测指标统计 ---")
    for k, v in metrics.items():
        print(f"{k}: {v}")
        
    # 5. 可视化
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), gridspec_kw={'height_ratios': [3, 1]})
    
    # 净值曲线
    ax1.plot(df.index, df['benchmark_nav'], label='Benchmark (Hold Maotai)', color='gray', alpha=0.6)
    ax1.plot(df.index, df['strategy_nav'], label='Strategy (Maotai Enhancer)', color='blue', linewidth=2)
    ax1.set_title('Maotai Holding Enhancer: 2-Year Backtest (NAV Comparison)')
    ax1.set_ylabel('Normalized Value')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 回撤曲线
    ax2.fill_between(df.index, drawdown, 0, color='red', alpha=0.3, label='Strategy Drawdown')
    ax2.set_title('Strategy Maximum Drawdown')
    ax2.set_ylabel('Drawdown')
    ax2.set_ylim(-0.5, 0.05)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('backtest_report.png')
    print("\n回测报告图表已保存为 'backtest_report.png'")
    
    # 保存详细数据到 CSV
    df.to_csv('backtest_results.csv')
    print("详细回测数据已保存为 'backtest_results.csv'")

if __name__ == "__main__":
    run_analysis()
