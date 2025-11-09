import pandas as pd

# 配置参数
THRESHOLD = 0.0001  # 资费阈值
INPUT_FILE = 'fundingRate_with_prices.csv'
OUTPUT_FILE = 'fundingRate_with_strategy.csv'

def funding_arbitrage_strategy():
    """
    加密货币资费套利策略
    - 当fundingRate >= 阈值时：开仓期货空头+现货多头
    - 当fundingRate <= -阈值时：开仓期货多头+现货空头  
    - 当fundingRate方向反转时：平仓
    """
    
    # 读取数据
    df = pd.read_csv(INPUT_FILE)
    print(f"读取数据：{len(df)} 行")
    
    # 初始化仓位列
    df['futures_position'] = 0  # 正数表示多头，负数表示空头，0表示无仓位
    df['spot_position'] = 0     # 正数表示多头，负数表示空头，0表示无仓位

    for idx in range(len(df)):
        print(idx)
        funding_rate = float(df.iloc[idx]['fundingRate'])
        print(funding_rate)
        # 执行交易逻辑
        if funding_rate >= THRESHOLD:
            # fundingRate >= 阈值的情况
            df.iloc[idx, df.columns.get_loc('futures_position')] = -1
            df.iloc[idx, df.columns.get_loc('spot_position')] = 1
            print('futures:-1')
        elif funding_rate <= -THRESHOLD:
            # fundingRate <= -阈值的情况
                df.iloc[idx, df.columns.get_loc('futures_position')] = 1
                df.iloc[idx, df.columns.get_loc('spot_position')] = -1
                print('futures:1')
        else:
            # fundingRate在阈值范围内的情况
            #如果第一条数据，忽略
            if idx == 0:
                print('keep')
                df.iloc[idx, df.columns.get_loc('futures_position')] = 0
                df.iloc[idx, df.columns.get_loc('spot_position')] = 0
            else:
                if funding_rate > 0:
                    if df.iloc[(idx-1), df.columns.get_loc('futures_position')] < 0:
                        print('keep')
                        df.iloc[idx, df.columns.get_loc('futures_position')] = -1
                        df.iloc[idx, df.columns.get_loc('spot_position')] = 1
                    else:
                        df.iloc[idx, df.columns.get_loc('futures_position')] = 0
                        df.iloc[idx, df.columns.get_loc('spot_position')] = 0
                        print('position closed')
                elif funding_rate < 0:
                    if df.iloc[(idx-1), df.columns.get_loc('futures_position')] > 0:
                        print('keep')
                        df.iloc[idx, df.columns.get_loc('futures_position')] = 1
                        df.iloc[idx, df.columns.get_loc('spot_position')] = -1
                    else:
                        df.iloc[idx, df.columns.get_loc('futures_position')] = 0
                        df.iloc[idx, df.columns.get_loc('spot_position')] = 0
                        print('position closed')
                else:
                    df.iloc[idx, df.columns.get_loc('futures_position')] = df.iloc[(idx-1), df.columns.get_loc('futures_position')]
                    df.iloc[idx, df.columns.get_loc('spot_position')] = df.iloc[(idx-1), df.columns.get_loc('spot_position')]
                    
    # 输出结果
    # 将position列向下移动一行
    df['futures_position_shifted'] = df['futures_position'].shift(1).fillna(0)
    df['spot_position_shifted'] = df['spot_position'].shift(1).fillna(0)
    
    # 删除原来的position列，保留shifted列
    df = df.drop(['futures_position', 'spot_position'], axis=1)
    df = df.rename(columns={'futures_position_shifted': 'futures_position', 'spot_position_shifted': 'spot_position'})
    
    # 计算fundingRatePnL
    df['fundingRatePnL'] = df['fundingRate'] * df['markPrice'] * df['futures_position']*(-1)
    
    # 计算basisPnL
    df['lastSpotPrice'] = df['spotPrice'].shift(1)
    df['lastFuturesPrice'] = df['futuresPrice'].shift(1)
    
    # 对于第一行，用当前价格作为lastPrice
    df.loc[0, 'lastSpotPrice'] = df.loc[0, 'spotPrice']
    df.loc[0, 'lastFuturesPrice'] = df.loc[0, 'futuresPrice']
    
    df['basisPnL'] = (df['spot_position'] * ((df['spotPrice'] / df['lastSpotPrice']) - 1) + 
                      df['futures_position'] * ((df['futuresPrice'] / df['lastFuturesPrice']) - 1))
    
    # 计算totalPnL
    df['totalPnL'] = df['fundingRatePnL'] + df['basisPnL']
    
    # 计算累计totalPnL
    df['cumulative_totalPnL'] = df['totalPnL'].cumsum()
    
    # 删除辅助列
    df = df.drop(['lastSpotPrice', 'lastFuturesPrice'], axis=1)
    
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"策略结果已保存到：{OUTPUT_FILE}")
    
if __name__ == "__main__":
    funding_arbitrage_strategy()