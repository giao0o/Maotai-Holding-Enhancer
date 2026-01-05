import pandas as pd
from utils.data_loader import DataLoader
from strategies.regime_detector import RegimeDetector
from strategies.maotai_t_strategy import MaotaiTStrategy
import matplotlib.pyplot as plt

def main():
    print("=== 茅台持仓增强器 (Maotai Holding Enhancer) v1.0 ===")
    
    # 1. 初始化
    loader = DataLoader()
    detector = RegimeDetector()
    strategy = MaotaiTStrategy()
    
    # 2. 获取数据 (获取过去一年的数据进行演示)
    end_date = pd.Timestamp.now().strftime('%Y%m%d')
    start_date = (pd.Timestamp.now() - pd.Timedelta(days=365)).strftime('%Y%m%d')
    
    try:
        df = loader.get_daily_data(start_date, end_date)
    except Exception as e:
        print(f"获取数据失败: {e}")
        return

    # 3. 市场状态识别
    df = detector.detect(df)
    
    # 4. 生成策略信号
    df = strategy.generate_signals(df)
    
    # 5. 输出最近的建议
    latest = df.iloc[-1]
    print("\n--- 最新市场分析 ---")
    print(f"日期: {df.index[-1].strftime('%Y-%m-%d')}")
    print(f"当前收盘价: {latest['close']:.2f}")
    print(f"市场状态: {latest['regime']}")
    print(f"建议做T仓位: {latest['suggested_t_pos']*100:.0f}%")
    
    if latest['signal'] == -1:
        print("操作建议: 【卖出/减仓】 触发日内高位信号，建议执行替代操作。")
    elif latest['signal'] == 1:
        print("操作建议: 【买入/回补】 触发日内低位信号，建议补回仓位。")
    else:
        print("操作建议: 【持有】 当前无明确做T信号，建议死拿。")

    # 6. 简单可视化 (保存到文件)
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['close'], label='Maotai Close')
    plt.title('Maotai Price and Market Regimes')
    
    # 用不同颜色背景表示不同状态
    colors = {'Risk-On': 'green', 'Volatile': 'yellow', 'Risk-Off': 'red', 'Low-Liquidity': 'gray'}
    for regime, color in colors.items():
        mask = df['regime'] == regime
        plt.fill_between(df.index, df['low'].min(), df['high'].max(), where=mask, color=color, alpha=0.2, label=regime)
    
    plt.legend()
    plt.savefig('maotai_analysis.png')
    print("\n分析图表已保存为 'maotai_analysis.png'")

if __name__ == "__main__":
    main()
