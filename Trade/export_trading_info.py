import csv
from pathlib import Path
from binance.client import Client

SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "ZECUSDT", "SOLUSDT", "QUSDT",
    "NEARUSDT", "BRUSDT", "XRPUSDT", "WLDUSDT", "HYPEUSDT",
    "AGTUSDT", "BTWUSDT", "GTCUSDT", "1000PEPEUSDT", "DOGEUSDT",
    "BNBUSDT", "SUIUSDT", "PUMPUSDT", "ARBUSDT", "ENAUSDT",
    "CTUSDT", "UNIUSDT", "PHAUSDT", "FILUSDT", "ADAUSDT",
    "TIAUSDT", "TAOUSDT", "LINKUSDT", "INJUSDT", "AVAXUSDT",
    "STRKUSDT", "QNTUSDT", "XMRUSDT", "APRUSDT", "AAVEUSDT",
    "PAXGUSDT", "SANDUSDT", "ONDOUSDT", "ZROUSDT", "DOTUSDT",
]

def export_trading_info(client, symbols):
    if not symbols:
        raise ValueError("SYMBOLS 不能为空。")
    markets = {m["symbol"]: m for m in client.futures_exchange_info()["symbols"]}
    for symbol in dict.fromkeys(symbols):
        if symbol not in markets or markets[symbol]["contractType"] != "PERPETUAL":
            raise ValueError(f"{symbol} 不是有效的 USD-M 永续合约。")
    rows = [
        {"symbol": symbol, "baseAsset": markets[symbol]["baseAsset"], **rule}
        for symbol in dict.fromkeys(symbols) for rule in markets[symbol]["filters"]
        if rule["filterType"] in ("LOT_SIZE", "MARKET_LOT_SIZE", "MIN_NOTIONAL")
    ]
    path = Path(__file__).resolve().parent.parent / "TradingInfo.csv"
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fields or ["symbol", "baseAsset", "filterType"])
        writer.writeheader()
        writer.writerows(rows)
    print("交易规则已保存：", path)


if __name__ == "__main__":
    client = Client(ping=False, requests_params={"timeout": 10})
    try:
        export_trading_info(client, SYMBOLS)
    finally:
        client.close_connection()
