import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def moving_average_strategy(csv_file, M, N):
    # 读取数据
    df = pd.read_csv(csv_file)
    
    # 生成 ma 列
    df['ma'] = df['close'].rolling(window=M).mean()
    
    # 生成 signal 列：close > ma 为 1，close < ma 为 -1，其他为 0
    df['signal'] = np.where(df['close'] > df['ma'], 1, 
                            np.where(df['close'] < df['ma'], -1, 0))
    # 前 M 个信号设为 0（因为没有足够数据计算均线）
    df.loc[:M-1, 'signal'] = 0
    
    # 计算 open_signal 和 position
    df['open_signal'] = df['signal']
    df['position'] = df['open_signal'].rolling(window=N, min_periods=1).sum()
    
    # 计算 return 和 pnl
    # return = close / last_close - 1
    df['return'] = df['close'] / df['close'].shift(1) - 1
    df['return'] = df['return'].fillna(0)  # 第一行填充为0
    
    # pnl = return * last_position
    df['pnl'] = df['return'] * df['position'].shift(1)  # shift(1) 获取上一期的position
    df['pnl'] = df['pnl'].fillna(0)  # 第一行没有last position，填充为0
    
    # cpnl = 累计 PNL
    df['cpnl'] = df['pnl'].cumsum()
    
    # 删除临时列
    # df.drop(columns=['ma', 'signal'], inplace=True)
    
    # 保存结果到 kline 文件夹
    import os
    os.makedirs('kline', exist_ok=True)
    output_file = f'kline/merged_data_with_strategy_M{M}_N{N}.csv'
    df.to_csv(output_file, index=False)
    print(f"\nResult saved to: {output_file}")
    
    # 绘制 cpnl 图表
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['cpnl'], linewidth=1.5, color='blue')
    
    # 计算 Sharpe Ratio
    pnl_mean = df['pnl'].mean()
    pnl_std = df['pnl'].std()
    sharpe_ratio = (pnl_mean / pnl_std * 94) if pnl_std != 0 else 0
    
    plt.title(f'Cumulative PNL - M={M}, N={N}, Sharpe Ratio={sharpe_ratio:.2f}', 
              fontsize=14, fontweight='bold')
    plt.xlabel('Time Index', fontsize=12)
    plt.ylabel('Cumulative PNL', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # 保存图表到 kline 文件夹
    plot_file = f'kline/cpnl_plot_M{M}_N{N}.png'
    plt.savefig(plot_file, dpi=150)
    print(f"Plot saved to: {plot_file}")
    plt.close()
    
    return df, sharpe_ratio


if __name__ == "__main__":
    # 参数网格
    M_values = [5, 10, 15, 20, 25]
    N_values = [5, 10, 15, 20, 25]
    
    # 存储结果
    results_summary = []
    
    print("="*60)
    print(f"开始参数遍历: {len(M_values)} x {len(N_values)} = {len(M_values) * len(N_values)} 组参数")
    print("="*60)
    
    # 遍历所有参数组合
    for M in M_values:
        for N in N_values:
            print(f"\n运行策略: M={M}, N={N}")
            try:
                result_df, sharpe_ratio = moving_average_strategy('klineData.csv', M=M, N=N)
                
                # 记录关键指标
                final_cpnl = result_df['cpnl'].iloc[-1]
                total_signals = (result_df['open_signal'] != 0).sum()
                max_position = result_df['position'].abs().max()
                
                results_summary.append({
                    'M': M,
                    'N': N,
                    'final_cpnl': final_cpnl,
                    'sharpe_ratio': sharpe_ratio,
                    'total_signals': total_signals,
                    'max_position': max_position
                })
                
                print(f"  最终累计PNL: {final_cpnl:.6f}, Sharpe Ratio: {sharpe_ratio:.2f}")
                
            except Exception as e:
                print(f"  错误: {e}")
    
    # 保存汇总结果
    summary_df = pd.DataFrame(results_summary)
    import os
    os.makedirs('kline', exist_ok=True)
    summary_file = 'kline/strategy_summary.csv'
    summary_df.to_csv(summary_file, index=False)
    print("\n" + "="*60)
    print("参数遍历完成！")
    print(f"汇总结果已保存到: {summary_file}")
    print("="*60)
    
    # 找出最佳参数
    if len(summary_df) > 0:
        best_result = summary_df.loc[summary_df['final_cpnl'].idxmax()]
        print(f"\n最佳参数组合(按累计PNL):")
        print(f"  M = {best_result['M']:.0f}")
        print(f"  N = {best_result['N']:.0f}")
        print(f"  最终累计PNL = {best_result['final_cpnl']:.6f}")
        print(f"  Sharpe Ratio = {best_result['sharpe_ratio']:.2f}")
        
        # 生成 Sharpe Ratio 热力图
        print("\n生成 Sharpe Ratio 热力图...")
        
        # 创建透视表
        heatmap_data = summary_df.pivot(index='N', columns='M', values='sharpe_ratio')
        
        # 绘制热力图
        plt.figure(figsize=(14, 10))
        sns.heatmap(heatmap_data, annot=True, fmt='.2f', cmap='RdYlGn', 
                    center=0, cbar_kws={'label': 'Sharpe Ratio'})
        plt.title('Sharpe Ratio Heatmap', fontsize=16, fontweight='bold')
        plt.xlabel('M (均线周期)', fontsize=12)
        plt.ylabel('N (持仓时间)', fontsize=12)
        plt.tight_layout()
        
        # 保存热力图
        heatmap_file = 'kline/sharpe_ratio_heatmap.png'
        plt.savefig(heatmap_file, dpi=150)
        print(f"热力图已保存到: {heatmap_file}")
        plt.close()
        
        print("\n所有任务完成！")

    