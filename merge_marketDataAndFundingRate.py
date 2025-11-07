import pandas as pd
import os
import glob
from datetime import datetime, timezone
import re

# 配置路径
FUNDING_FILE = 'fundingRate.csv'
SPOT_DIR = 'marketData/spot/temp_unzip'
FUTURES_DIR = 'marketData/futures/temp_unzip'

# 读取 fundingRate.csv
funding_df = pd.read_csv(FUNDING_FILE)

def get_date_str(ts):
    dt = datetime.fromtimestamp(ts // 1000, timezone.utc)
    return dt.strftime('%Y-%m-%d')

def extract_date_from_filename(filename):
    # 提取文件名中的日期部分
    match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
    return match.group(1) if match else None

def find_price_in_files_with_ts(folder, target_ts, skip_header=False):
    date_str = get_date_str(target_ts)
    all_files = sorted(glob.glob(os.path.join(folder, '*.csv')))
    # 只从对应日期的文件开始查找
    files_to_search = [f for f in all_files if extract_date_from_filename(f) and extract_date_from_filename(f) >= date_str]
    for csv_file in files_to_search:
        file_date = extract_date_from_filename(csv_file)
        if file_date and file_date >= date_str:
            with open(csv_file, 'r') as f:
                if skip_header:
                    next(f)
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) < 6:
                        continue
                    ts = int(parts[5])
                    price = float(parts[1])
                    # 判断是现货还是期货
                    if folder == SPOT_DIR:
                        cmp_ts = target_ts * 1000
                    else:
                        cmp_ts = target_ts
                    if ts >= cmp_ts:
                        return price, ts
    # 如果当前文件没找到，则继续下一个文件
    return None, None

spot_price_col = []
futures_price_col = []
spot_ts_col = []
futures_ts_col = []

total = len(funding_df)
for idx, row in funding_df.iterrows():
    funding_time = int(row['fundingTime'])
    print(f'处理第 {idx+1}/{total} 行，fundingTime={funding_time} ...')
    spot_price, spot_ts = find_price_in_files_with_ts(SPOT_DIR, funding_time)
    futures_price, futures_ts = find_price_in_files_with_ts(FUTURES_DIR, funding_time, skip_header=True)
    spot_price_col.append(spot_price)
    futures_price_col.append(futures_price)
    spot_ts_col.append(spot_ts)
    futures_ts_col.append(futures_ts)

funding_df['spotPrice'] = spot_price_col
funding_df['futuresPrice'] = futures_price_col
funding_df['spotPrice_ts'] = spot_ts_col
funding_df['futuresPrice_ts'] = futures_ts_col

funding_df.to_csv('fundingRate_with_prices.csv', index=False)
print('处理完成，结果已保存为 fundingRate_with_prices.csv')
