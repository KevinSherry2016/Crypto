import csv
import datetime
import json
import sys
from urllib.parse import urlencode
import urllib.request
import urllib.error

API_BASE = 'https://fapi.binance.com/fapi/v1/fundingRate'
START_PARAM = '20240101000000'  # format: YYYYMMDDHHMMSS
END_PARAM = '20251031235959'    # format: YYYYMMDDHHMMSS
SYMBOL_PARAM = 'BTCUSDT'        # example: BTCUSDT
MAX_DAYS = 30


def parse_time_arg(s):
    if s is None:
        return None
    s = str(s).strip()
    if len(s) == 14 and s.isdigit():
        try:
            dt = datetime.datetime.strptime(s, '%Y%m%d%H%M%S')
            epoch_ms = int(dt.replace(tzinfo=datetime.timezone.utc).timestamp() * 1000)
            return dt, epoch_ms
        except Exception:
            raise ValueError('time must be in YYYYMMDDHHMMSS format')
    raise ValueError('time must be in YYYYMMDDHHMMSS format')


def fetch_funding_rate(symbol, start_ms, end_ms, timeout=30):
    params = {
        'symbol': symbol,
        'startTime': str(start_ms),
        'endTime': str(end_ms),
    }
    url = API_BASE + '?' + urlencode(params)
    req = urllib.request.Request(url, headers={'User-Agent': 'binance-funding-csv/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
            return json.loads(data.decode('utf-8'))
    except urllib.error.HTTPError as he:
        body = he.read().decode('utf-8', errors='ignore')
        raise RuntimeError(f'HTTP error {he.code}: {body}')
    except Exception as e:
        raise


def write_csv(records, outpath, write_header=True):
    if not records:
        return
    keys = set()
    for r in records:
        keys.update(r.keys())
    preferred = ['symbol', 'fundingTime', 'fundingRate']
    other = [k for k in sorted(keys) if k not in preferred]
    fieldnames = [k for k in preferred if k in keys] + other + ['fundingTime_str']

    with open(outpath, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        for r in records:
            row = {k: r.get(k, '') for k in fieldnames}
            # 增加格式化时间戳
            try:
                ts = int(r.get('fundingTime', 0))
                dt = datetime.datetime.fromtimestamp(ts / 1000, datetime.timezone.utc)
                row['fundingTime_str'] = dt.strftime('%Y%m%d%H%M%S')
            except Exception:
                row['fundingTime_str'] = ''
            writer.writerow(row)


def main():
    if not SYMBOL_PARAM:
        print('SYMBOL_PARAM must be set at the top of the script', file=sys.stderr)
        sys.exit(2)
    try:
        start_dt, start_ms = parse_time_arg(START_PARAM)
        end_dt, end_ms = parse_time_arg(END_PARAM)
    except ValueError as e:
        print('Invalid time argument:', e, file=sys.stderr)
        sys.exit(2)

    if start_ms is None or end_ms is None:
        print('START_PARAM and END_PARAM must be provided at the top of the script', file=sys.stderr)
        sys.exit(2)

    print(f'Fetching fundingRate for {SYMBOL_PARAM} from {start_dt} to {end_dt}...')
    outpath = 'fundingRate.csv'
    first_batch = True
    batch_start = start_dt
    batch_num = 1
    while batch_start < end_dt:
        batch_end = batch_start + datetime.timedelta(days=MAX_DAYS)
        if batch_end > end_dt:
            batch_end = end_dt
        batch_start_ms = int(batch_start.replace(tzinfo=datetime.timezone.utc).timestamp() * 1000)
        batch_end_ms = int(batch_end.replace(tzinfo=datetime.timezone.utc).timestamp() * 1000)
        print(f'Batch {batch_num}: {batch_start} ~ {batch_end}')
        print(f'  Request params: start_ms={batch_start_ms}, end_ms={batch_end_ms}')
        try:
            recs = fetch_funding_rate(SYMBOL_PARAM, batch_start_ms, batch_end_ms)
        except Exception as e:
            print('Failed to fetch data:', e, file=sys.stderr)
            sys.exit(1)
        print(f'  Got {len(recs)} records')
        write_csv(recs, outpath, write_header=first_batch)
        print(f'  Written to {outpath} (header={first_batch})')
        first_batch = False
        batch_start = batch_end
        batch_num += 1
    print(f'All batches done. Output: {outpath}')

if __name__ == '__main__':
    main()
