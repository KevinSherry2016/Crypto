数据：现货价格，期货价格，资金费率（每8小时更新一次），手续费，滑点（百分之多少）
现货价格：
https://data.binance.vision/?prefix=data/spot/daily/aggTrades/BTCUSDT/

期货价格：
https://data.binance.vision/?prefix=data/futures/um/daily/aggTrades/BTCUSDT/

资金费率：
https://fapi.binance.com/fapi/v1/fundingRate?symbol=BTCUSDT&startTime=1759276800000&endTime=1761868800000

现货BTC借贷利率：
0.5~3%

币安api文档：
https://developers.binance.com/docs/zh-CN/binance-spot-api-docs/rest-api/general-api-information

注意：
1. 计算资费时，使用funding_rate * market_price
2. 计算资费时，以快照时间为准。如果那一时刻有仓位，就收资费
