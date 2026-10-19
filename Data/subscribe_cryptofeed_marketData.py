"""
Subscribe to real-time market data via cryptofeed, print every message received
and append it to CSV files under realTimeData/.
Edit the parameters below to change exchange / channel / symbols.
"""
import csv
import os

from cryptofeed import FeedHandler
from cryptofeed.exchanges import EXCHANGE_MAP

EXCHANGE = 'BINANCE'       # key of cryptofeed.exchanges.EXCHANGE_MAP, e.g. BINANCE / BINANCE_FUTURES / OKX
CHANNEL = 'candles'        # trades / ticker / l2_book / candles
SYMBOLS = ['BTC-USDT', 'ETH-USDT', 'SOL-USDT']  # cryptofeed symbol format, e.g. BTC-USDT, BTC-USDT-PERP for futures
CANDLE_INTERVAL = '1m'     # only used when CHANNEL is candles, e.g. 1m / 5m / 1h / 1d
CANDLE_CLOSED_ONLY = True  # True = only closed bars, False = also in-progress bar updates
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'realTimeData')


def save_message(data, receipt_timestamp):
    row = data.to_dict(numeric_type=str)
    row['receipt_timestamp'] = receipt_timestamp
    name = f'{EXCHANGE}_{CHANNEL}_{data.symbol}'
    if CHANNEL == 'candles':
        name += f'_{CANDLE_INTERVAL}'
    path = os.path.join(OUTPUT_DIR, f'{name}.csv')
    write_header = not os.path.exists(path)
    with open(path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(row))
        if write_header:
            writer.writeheader()
        writer.writerow(row)


async def on_message(data, receipt_timestamp):
    print(f'[{receipt_timestamp:.6f}] {data}', flush=True)
    save_message(data, receipt_timestamp)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    feed = EXCHANGE_MAP[EXCHANGE](
        symbols=SYMBOLS,
        channels=[CHANNEL],
        callbacks={CHANNEL: on_message},
        candle_interval=CANDLE_INTERVAL,
        candle_closed_only=CANDLE_CLOSED_ONLY,
    )
    fh = FeedHandler()
    fh.add_feed(feed)
    fh.run()


if __name__ == '__main__':
    main()
