数据：现货价格，期货价格，资金费率（每8小时更新一次）
现货价格：
https://data.binance.vision/?prefix=data/spot/daily/aggTrades/BTCUSDT/

期货价格：
https://data.binance.vision/?prefix=data/futures/um/daily/aggTrades/BTCUSDT/

资金费率：
https://fapi.binance.com/fapi/v1/fundingRate?symbol=BTCUSDT&startTime=1759276800000&endTime=1761868800000


币安api文档：
https://developers.binance.com/docs/zh-CN/binance-spot-api-docs/rest-api/general-api-information

注意：
1. 计算资费时，使用funding_rate * market_price
2. 计算资费时，以时刻为准。如果那一时刻有仓位，就收资费

moving_average_strategy
V1：
使用Z_Score标准化数据
观察期M，预测期N，，开仓阈值z_open

V2：
观察期M，开仓阈值z_open，平仓阈值z_close


Others

策略容量 交易费率 - > 万5 万2 BTC POT = 20

binance - > btc/usdt

每小时成交量 * 1% =

20万GMV，总共100万AUM

0.2倍杠杆（回撤不超过百分之20） 几百万美金 return 30+ 2 —— 3 天（48h——72h） POT > 60/70

aum 百万美金，算比较大

10名 —— 100名小币种

## 版本管理范围

仓库提交代码、文档和必要配置。行情数据与回测产物保留在本地，
由 `.gitignore` 排除：`CleanData/`、`marketData/`、`Evaluate_*/`、
`Result_*/`、`Production/*/Result/`、`moving_average_strategy_result/`
以及根目录的 `klineData.csv`。本地虚拟环境、Python 缓存和 `.env`
文件也不提交。忽略规则不会自动移除历史上已经跟踪的文件。
