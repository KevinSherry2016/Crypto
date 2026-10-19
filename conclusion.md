# BTC、ETH、SOL 因子与参数筛选结论

## 筛选口径

候选按各标的独立筛选；每个币对可同时推荐多个不同因子，而不限制为单一因子。全样本 `sharpeRatio` 用于衡量整体收益风险比；稳定性则以同一“因子名称 + 信号方式”内的所有参数为比较集合，在每个完整自然半年重算年化 Sharpe 并排名。优先选择平均半年度排名靠前、最差半年度也未显著落后的参数。

为避免参数孤岛，另检查相邻窗口参数的全样本 Sharpe：推荐参数必须位于一段相邻参数表现接近的区域，而不是仅某一个参数突出的单点。

## 计算结果

样本中共有五个完整自然半年：`2024H1`、`2024H2`、`2025H1`、`2025H2` 和 `2026H1`。下表的“平均/最差名次”是同一因子和信号方式的参数组内百分位，`top 12%` 表示平均处在该参数组前 12%。

“邻域中位 Sharpe”取参数相差 `10` 或 `20` 的相邻窗口的全样本 Sharpe 中位数；它接近当前参数 Sharpe，说明该结果位于参数高原。

### BTCUSDT

|优先级|因子|参数与信号方式|全样本 Sharpe|半年度相对名次|正 Sharpe 窗口|邻域中位 Sharpe|结论|
|---|---|---|---:|---|---:|---:|---|
|主推荐|`Volume_CMF`|`N180`, `state_machine`|1.660|平均 `top 24%`，最差 `top 55%`|5/5|1.550|最均衡的稳定候选；五个半年均为正，且 `N160-N180` 一带不是单点。|
|主推荐|`Microstructure_BuyingSellingPressure`|`N120`, `state_machine`|1.435|平均 `top 24%`，最差 `top 45%`|5/5|1.432|全样本 Sharpe 低于前者，但参数排名和平台性最好；邻域几乎等高。|
|进取候选|`Volume_OIPriceFlow`|`N90`, `raw`|1.866|平均 `top 27%`，最差 `top 60%`|4/5|1.750|全样本 Sharpe 最高，`N80-N100` 形成清晰平台；但 `2025H1` Sharpe 为 `-1.05`，不宜作为唯一配置。|

`Volume_MFI N30 state_machine` 的全样本 Sharpe 为 `1.729`，但最差半年度仅到 `top 60%`，且邻域 Sharpe 只有 `1.297`，因此未列入主推荐。

### ETHUSDT

|优先级|因子|参数与信号方式|全样本 Sharpe|半年度相对名次|正 Sharpe 窗口|邻域中位 Sharpe|结论|
|---|---|---|---:|---|---:|---:|---|
|主推荐|`Microstructure_BuyingSellingPressure`|`N110`, `raw`|1.885|平均 `top 12%`，最差 `top 20%`|4/5|1.729|半年度组内排名最稳定、最靠前；`N100-N130` 是连续高原。`2026H1` 略负（`-0.13`），但仍是该因子组前列。|
|主推荐|`Volume_OIPriceFlow`|`N100`, `state_machine`|2.102|平均 `top 27%`，最差 `top 50%`|5/5|1.766|三个标的中全样本 Sharpe 最强的单一主候选之一，五个半年全部为正；`N100-N120` 为可用平台。|
|备选参数|`Microstructure_BuyingSellingPressure`|`N120`, `raw`|1.776|平均 `top 16%`，最差 `top 30%`|4/5|1.714|与 `N110` 共同构成稳定高原，可用于降低单一窗口参数风险。|

### SOLUSDT

|优先级|因子|参数与信号方式|全样本 Sharpe|半年度相对名次|正 Sharpe 窗口|邻域中位 Sharpe|结论|
|---|---|---|---:|---|---:|---:|---|
|主推荐|`Volume_OIPriceFlow`|`N50`, `raw`|1.768|平均 `top 33%`，最差 `top 55%`|5/5|1.626|SOL 上全样本 Sharpe 最高且五个半年皆正的候选；位于 `N40-N60` 平台。|
|主推荐|`Volume_OIPriceFlow`|`N90`, `raw`|1.717|平均 `top 32%`，最差 `top 60%`|5/5|1.580|略低于 `N50`，但也处于 `N80-N100` 高原，可作为时间尺度不同的稳健替代。|
|次主推荐|`Volume_PriceVolumeCorrelation`|`N50`, `tanh`|1.580|平均 `top 35%`，最差 `top 80%`|5/5|1.406|第二个可选因子；`N40-N60` 邻域连续可用且五个半年均为正，但最差阶段的相对排名较弱，权重应低于 OI 资金流。|

`CrossSectional_Skewness N180 zscore` 的全样本 Sharpe 为 `1.636`，但 `2026H1` 为负且高原强度较弱（邻域中位 Sharpe `1.240`），不作为优先选择。

## 最终建议

- **BTC：** 优先 `Volume_CMF N180 state_machine` 与 `Microstructure_BuyingSellingPressure N120 state_machine`；追求更高全样本 Sharpe 时，可小比例加入 `Volume_OIPriceFlow N90 raw`，但应接受其阶段性失效风险。
- **ETH：** 优先 `Microstructure_BuyingSellingPressure N110 raw` 和 `Volume_OIPriceFlow N100 state_machine`；前者的相对排名更稳，后者的绝对 Sharpe 更高。
- **SOL：** 主因子为 `Volume_OIPriceFlow`，优先 `N50 raw`、以 `N90 raw` 作为窗口替代；可同时配置第二个因子 `Volume_PriceVolumeCorrelation N50 tanh`，但其最差半年度排名偏后，建议权重低于主因子。三项在五个完整半年度均为正。

上述结论基于已有回测结果，属于样本内筛选。实际使用时应保留最近一个或多个半年作为完全未参与调参的样本外验证，避免把同一段历史同时用于参数选择与绩效确认。