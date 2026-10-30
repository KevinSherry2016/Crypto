Data/
download_binance_marketData.py：下载binance行情数据
download_binance_fundingRate.py：下载binance资金费率数据
unzip_and_merge_marketData.py：解压并合并binance行情数据
subscribe_cryptofeed_marketData.py：接收实时行情数据
check_merged_marketData.py：检查行情数据
convert_cleandata_time_columns.py：将行情数据Unix时间戳进行转换


策略容量 交易费率 - > 万5 万2 BTC POT = 20

binance - > btc/usdt

每小时成交量 * 1% =

20万GMV，总共100万AUM

0.2倍杠杆（回撤不超过百分之20） 几百万美金 return 30+ 2 —— 3 天（48h——72h） POT > 60/70

aum 百万美金，算比较大

10名 —— 100名小币种

API密钥
5TuntjtR4eKGj4BpWR4dmnFp2KCtnJVg3nrDDtLw57Aex9san6exRzu9fSqH3n7G

加密密钥
CYMMn5JUfWeRgdxJzaXX6Fe4jQh4g1G51HvqYLfNnB2gbiwXxvbyWhnBBs1d9Fg9


1. KYC验证，需要不受限地区的地址证明
2. API管理，生成Key和Secret。添加IP白名单，自定义交易币对，授权各类操作
3. 将合约交易改为单向持仓，保证金方式设置为联合保证金
4. 查询各个交易币对的交易规则，包括最小开仓数量，金额，步长
5. 现货账户、资金账户向合约账户转使得有足够保证金。
