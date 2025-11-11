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
使用Z_Score方法
观察期M，预测期N，，开仓阈值z_open
