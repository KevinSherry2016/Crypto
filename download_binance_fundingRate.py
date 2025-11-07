import csv
import datetime
import json
import sys
from urllib.parse import urlencode
import urllib.request
import urllib.error

API_BASE = 'https://fapi.binance.com/fapi/v1/fundingRate'

START_PARAM = '20251001000000'  # format: YYYYMMDDHHMMSS
END_PARAM = '20251010235959'    # format: YYYYMMDDHHMMSS
SYMBOL_PARAM = 'BTCUSDT'        # example: BTCUSDT

def parse_time_arg(s):
    if s is None:
        return None
    s = str(s).strip()
    if len(s) == 14 and s.isdigit():
        try:
            dt = datetime.datetime.strptime(s, '%Y%m%d%H%M%S')
            epoch_ms = int(dt.replace(tzinfo=datetime.timezone.utc).timestamp() * 1000)
            return epoch_ms
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


def write_csv(records, outpath):
    if not records:
        with open(outpath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['note'])
            writer.writerow(['no records returned'])
        return
    keys = set()
    for r in records:
        keys.update(r.keys())
    preferred = ['symbol', 'fundingTime', 'fundingRate']
    other = [k for k in sorted(keys) if k not in preferred]
    fieldnames = [k for k in preferred if k in keys] + other

    with open(outpath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in records:
            row = {k: r.get(k, '') for k in fieldnames}
            writer.writerow(row)


def main():
    if not SYMBOL_PARAM:
        print('SYMBOL_PARAM must be set at the top of the script', file=sys.stderr)
        sys.exit(2)
    try:
        start_ms = parse_time_arg(START_PARAM)
        end_ms = parse_time_arg(END_PARAM)
    except ValueError as e:
        print('Invalid time argument:', e, file=sys.stderr)
        sys.exit(2)

    if start_ms is None or end_ms is None:
        print('START_PARAM and END_PARAM must be provided at the top of the script', file=sys.stderr)
        sys.exit(2)

    print(f'Fetching fundingRate for {SYMBOL_PARAM} from {start_ms} to {end_ms}...')
    try:
        recs = fetch_funding_rate(SYMBOL_PARAM, start_ms, end_ms)
    except Exception as e:
        print('Failed to fetch data:', e, file=sys.stderr)
        sys.exit(1)

    out_default = f'fundingRate.csv'
    outpath = out_default
    print(f'Writing {len(recs)} records to {outpath}...')
    try:
        write_csv(recs, outpath)
    except Exception as e:
        print('Failed to write CSV:', e, file=sys.stderr)
        sys.exit(1)
    print('Done.')


if __name__ == '__main__':
    main()
