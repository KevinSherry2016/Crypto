# Factor 因子说明

本文按 `Factor/` 中当前的 24 个脚本整理，描述各因子的输入、计算含义和回看周期。因子使用 CleanData 的原始行情列：`open`、`high`、`low`、`close`、`volume`、`quote_volume`、`count`、`taker_buy_volume`、`taker_buy_quote_volume`。

## 均值回归

| 因子 | 输入列 | 计算说明 | 回看区间 |
|---|---|---|---|
| MeanReversion_NoiseFader.py | `close` | −最近 N 根 K 线首尾价格变化方向 ×（1 − 效率比）；效率比为首尾净价格变化绝对值除以区间内 N − 1 个单期价格变化绝对值之和。 | 最近 N 根 K 线 |
| MeanReversion_RollingDeviation.py | `close` | 最近 N 根收盘价均值 − 当前收盘价，表示价格相对近期均值的反向偏离。 | 最近 N 根 K 线 |
| MeanReversion_ShortTermReversal.py | `close` | 前一根到当前 K 线的收益率取反。 | 最近 2 根 K 线 |
| MeanReversion_VWAPDistance.py | `high`、`low`、`close`、`volume` | 以最近 N 根 K 线的典型价格和成交量计算滚动 VWAP，返回 −（收盘价/VWAP − 1）。 | 最近 N 根 K 线 |

## 微观结构

| 因子 | 输入列 | 计算说明 | 回看区间 |
|---|---|---|---|
| Microstructure_BuyingSellingPressure.py | `close`、`high`、`low` | 2 ×（收盘价 − 最低价）/（最高价 − 最低价）− 1，衡量收盘位置方向。 | 最近 1 根 K 线 |
| Microstructure_CloseLocationChange.py | `close`、`high`、`low` | 当根收盘位置指标减去前一根收盘位置指标。 | 最近 2 根 K 线 |
| Microstructure_WickImbalance.py | `open`、`high`、`low`、`close` | （下影线长度 − 上影线长度）/（最高价 − 最低价）。 | 最近 1 根 K 线 |
| Microstructure_TakerVolumeImbalance.py | `volume`、`taker_buy_volume` | 2 × 主动买入成交量/总成交量 − 1，即主动买入量与主动卖出量之差占总成交量的比例；正值表示主动买入占优，范围为 [-1, 1]。 | 最近 1 根 K 线 |
| Microstructure_TakerImbalanceChange.py | `volume`、`taker_buy_volume` | 当前主动买卖成交量不平衡度减去上一根的不平衡度；正值表示主动买入占比提升，范围为 [-2, 2]。 | 最近 2 根 K 线 |
| Microstructure_CloseVWAPDeviation.py | `close`、`volume`、`quote_volume` | 收盘价/当根真实成交均价 − 1；真实成交均价为总成交额/总成交量。与使用典型价格近似的滚动 VWAP 因子不同，正值表示收盘价高于当根成交均价。 | 最近 1 根 K 线 |
| Microstructure_RangeExpansionBalance.py | `high`、`low` | 向上扩张幅度为 max（当前最高价 − 前一根最高价，0），向下扩张幅度为 max（前一根最低价 − 当前最低价，0）；返回两者之差除以两根 K 线的联合振幅。正值表示向上扩张占优、偏多，负值表示向下扩张占优、偏空；无扩张或两侧扩张相等时为 0，联合振幅为 0 或数据缺失时保留缺失值。 | 最近 2 根 K 线 |

## 趋势动量

| 因子 | 输入列 | 计算说明 | 回看区间 |
|---|---|---|---|
| TrendMomentum_DonchianChannel.py | `high`、`low`、`close` | （收盘价 − 最近 N 根最低价）/（最近 N 根最高价 − 最近 N 根最低价）− 0.5。 | 最近 N 根 K 线 |
| TrendMomentum_DualMACrossover.py | `close` | N_fast 根均价/N 根均价 − 1，衡量快慢均线相对位置；N_fast 为快线周期，N 为慢线周期，且 N_fast < N。 | 最近 N 根 K 线 |
| TrendMomentum_EMASpreadChange.py | `close` | 计算周期为 N_fast 与 N_slow 的 EMA 相对差值，再计算该差值的单根变化。 | 从序列起点至当前的全部 K 线（EMA 递推） |
| TrendMomentum_LinearSlope.py | `close` | 在最近 N 根收盘价上计算线性回归斜率。 | 最近 N 根 K 线 |
| TrendMomentum_MACD.py | `close` | MACD 差值为 EMA(N_fast) − EMA(N_slow)；信号线为该差值的 EMA(N_signal)；返回 2 ×（差值 − 信号线）。 | 从序列起点至当前的全部 K 线（EMA 递推） |
| TrendMomentum_MovingAverageBias.py | `close` | 收盘价/最近 N 根均价 − 1，衡量价格相对均值的比例偏离。 | 最近 N 根 K 线 |
| TrendMomentum_RollingPriceDeviation.py | `close` | 当前收盘价 − 最近 N 根收盘价均值，保留价格单位的偏离值。 | 最近 N 根 K 线 |
| TrendMomentum_RSI.py | `close` | 以最近 N 根 K 线内 N − 1 个单期变化的平均上涨幅度和平均下跌幅度计算 RSI，再返回（RSI − 50）/50，范围为 [-1, 1]，原指标 50 对应 0；未定义值仍保留为缺失值。 | 最近 N 根 K 线 |
| TrendMomentum_TimeSeriesMomentum.py | `close` | 最近 N 根 K 线首尾收盘价的收益率，即当前收盘价相对 N − 1 期之前收盘价的收益率。 | 最近 N 根 K 线 |

## 成交量

| 因子 | 输入列 | 计算说明 | 回看区间 |
|---|---|---|---|
| Volume_CMF.py | `close`、`high`、`low`、`volume` | 计算收盘位置资金流乘数与成交量的乘积，并以最近 N 根资金流量总和除以最近 N 根成交量总和。 | 最近 N 根 K 线 |
| Volume_MFI.py | `high`、`low`、`close`、`volume` | 根据典型价格涨跌将成交额分为正、负资金流；最近 N 根 K 线中的首根用于判断下一根的涨跌，汇总后续 N − 1 根的资金流并计算 MFI，再返回（MFI − 50）/50，范围为 [-1, 1]，原指标 50 对应 0；未定义值仍保留为缺失值。 | 最近 N 根 K 线 |
| Volume_RollingTakerQuoteImbalance.py | `quote_volume`、`taker_buy_quote_volume` | 2 × 最近 N 根主动买入成交额之和/最近 N 根总成交额之和 − 1；正值表示区间内主动买入成交额占优，范围为 [-1, 1]。 | 最近 N 根 K 线 |
| Volume_DirectionalAverageTradeSizeSpread.py | `close`、`quote_volume`、`count` | 按单期收盘收益率将最近 N 根 K 线中的后续 N − 1 根分为上涨组和下跌组，分别计算组内总成交额/总成交笔数，再返回上涨组均值 − 下跌组均值。平盘不进入任一组，缺少一组时保留缺失值；衡量平均每笔成交额，不是订单规模。 | 最近 N 根 K 线 |
