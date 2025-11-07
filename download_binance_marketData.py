import datetime
import os
import sys
import time
from urllib.parse import urljoin
import urllib.request
import urllib.error

BASE_ROOT = 'https://data.binance.vision/'
PREFIX = 'data/{market}/{interval}/{datatype}/{symbol}/'
FNAME_PATTERN = '{symbol}-{datatype}-{date}.zip'
HEADERS = { 'User-Agent': 'binance-downloader/1.0' }

START_PARAM = '20251001'
END_PARAM = '20251010'
SYMBOL_PARAM = 'BTCUSDT'
DEST_PARAM = 'marketData'
MARKET_PARAM = 'futures/um'
INTERVAL_PARAM = 'daily'
DATATYPE_PARAM = 'aggTrades'

def parse_yyyymmdd(s):
    try:
        return datetime.datetime.strptime(s, '%Y%m%d').date()
    except ValueError:
        raise ValueError('Date must be YYYYMMDD')


def daterange(start_date, end_date):
    d = start_date
    while d <= end_date:
        yield d
        d += datetime.timedelta(days=1)


def build_url(symbol, date_obj):
    date_str = date_obj.strftime('%Y-%m-%d')
    market = MARKET_PARAM
    interval = INTERVAL_PARAM
    datatype = DATATYPE_PARAM
    prefix = PREFIX.format(market=market, interval=interval, datatype=datatype, symbol=symbol)
    fname = FNAME_PATTERN.format(symbol=symbol, datatype=datatype, date=date_str)
    path = prefix + fname
    return urljoin(BASE_ROOT, path), fname


def url_exists(url, timeout=15):
    req = urllib.request.Request(url, headers=HEADERS, method='HEAD')
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status < 400
    except urllib.error.HTTPError as he:
        if he.code == 404:
            return False
        return False
    except Exception:
        return False


def download(url, dest_path, overwrite=True, retries=2, timeout=120):
    if os.path.exists(dest_path) and not overwrite:
        return 'skipped'
    tmp = dest_path + '.part'
    attempt = 0
    while attempt <= retries:
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=timeout) as resp, open(tmp, 'wb') as out:
                while True:
                    chunk = resp.read(1 << 20)
                    if not chunk:
                        break
                    out.write(chunk)
            os.replace(tmp, dest_path)
            return 'downloaded'
        except urllib.error.HTTPError as he:
            if he.code == 404:
                return 'missing'
            attempt += 1
            time.sleep(1 + attempt)
        except Exception as e:
            attempt += 1
            time.sleep(1 + attempt)
    return 'failed'


def main():
    if not START_PARAM:
        print('START_PARAM must be set at the top of the script (YYYYMMDD)', file=sys.stderr)
        sys.exit(2)
    try:
        start_date = parse_yyyymmdd(START_PARAM)
    except Exception:
        print('START_PARAM has invalid format; must be YYYYMMDD', file=sys.stderr)
        sys.exit(2)

    if END_PARAM:
        try:
            end_date = parse_yyyymmdd(END_PARAM)
        except Exception:
            print('END_PARAM has invalid format; must be YYYYMMDD', file=sys.stderr)
            sys.exit(2)
    else:
        end_date = datetime.date.today()

    if not SYMBOL_PARAM:
        print('SYMBOL_PARAM must be set at the top of the script', file=sys.stderr)
        sys.exit(2)

    if not MARKET_PARAM:
        print('MARKET_PARAM must be set at the top of the script (e.g. "spot" or "futures/um")', file=sys.stderr)
        sys.exit(2)

    if not INTERVAL_PARAM:
        print('INTERVAL_PARAM must be set at the top of the script (e.g. "daily")', file=sys.stderr)
        sys.exit(2)

    if not DATATYPE_PARAM:
        print('DATA_PARAM must be set at the top of the script (e.g. "aggTrades")', file=sys.stderr)
        sys.exit(2)

    symbol = SYMBOL_PARAM
    dest = DEST_PARAM

    os.makedirs(dest, exist_ok=True)

    planned = []
    for d in daterange(start_date, end_date):
        url, fname = build_url(symbol, d)
        planned.append((d, url, fname))

    print(f'Planned files for {symbol} from {start_date} to {end_date}:')
    for d, url, fname in planned:
        print('  ', fname, '-', url)

    print('\nStarting downloads into', dest)
    for d, url, fname in planned:
        dest_path = os.path.join(dest, fname)
        exists = url_exists(url)
        if not exists:
            print('missing:', fname)
            continue
        status = download(url, dest_path)
        print(status + ':', fname)

    print('All done.')


if __name__ == '__main__':
    main()
