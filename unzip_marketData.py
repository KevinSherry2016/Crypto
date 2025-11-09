import os
import zipfile
import pandas as pd
import glob

SOURCE_DIR = './marketData/klines'
MERGED_CSV = os.path.join(SOURCE_DIR, 'merged_data.csv')

def merge_csv_files(input_dir=SOURCE_DIR, output_file=MERGED_CSV):
    zip_files = sorted(glob.glob(os.path.join(input_dir, '*.zip')))
    temp_dir = os.path.join(input_dir, 'temp_unzip')
    os.makedirs(temp_dir, exist_ok=True)
    csv_files = []
    # 解压所有zip文件到临时目录
    for zip_file in zip_files:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            for file_name in zip_ref.namelist():
                if file_name.endswith('.csv'):
                    out_path = os.path.join(temp_dir, os.path.basename(file_name))
                    with zip_ref.open(file_name) as source, open(out_path, 'wb') as target:
                        target.write(source.read())
                    csv_files.append(out_path)
    if not csv_files:
        print("没有找到任何csv数据")
        return
    # # 合并所有csv文件
    # all_dataframes = []
    # for csv_file in sorted(csv_files):
    #     # 保留原始列名
    #     df = pd.read_csv(csv_file, low_memory=False)
    #     all_dataframes.append(df)
    
    # # 合并所有数据
    # merged_df = pd.concat(all_dataframes, ignore_index=True)
    
    # # 按照时间顺序排序（假设第一列是时间戳）
    # if 'open_time' in merged_df.columns:
    #     merged_df = merged_df.sort_values(by='open_time')
    # elif merged_df.shape[1] >= 1:
    #     # 如果没有列名，假设第一列是时间
    #     merged_df = merged_df.sort_values(by=merged_df.columns[0])
    
    # # 重置索引
    # merged_df = merged_df.reset_index(drop=True)
    
    # # 保存时保留列名
    # merged_df.to_csv(output_file, index=False)
    # print(f"合并完成，输出文件：{output_file}")

if __name__ == "__main__":
    merge_csv_files()
