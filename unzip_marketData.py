import os
import zipfile
import pandas as pd
import glob

SOURCE_DIR = './marketData/spot'
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
    #     df = pd.read_csv(csv_file, header=None, low_memory=False)
    #     all_dataframes.append(df)
    # merged_df = pd.concat(all_dataframes, ignore_index=True)
    # if merged_df.shape[1] >= 6:
    #     merged_df = merged_df.sort_values(by=5)
    # merged_df.to_csv(output_file, index=False, header=False)
    # print(f"合并完成，输出文件：{output_file}")

if __name__ == "__main__":
    merge_csv_files()