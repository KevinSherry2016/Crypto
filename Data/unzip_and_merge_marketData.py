import csv
import shutil
from pathlib import Path
from zipfile import ZipFile

# 在这里直接修改要处理的交易币对，无需命令行参数。
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

# Binance Kline CSV 默认 12 列。
DEFAULT_COLUMNS = [
    "open_time",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "close_time",
    "quote_asset_volume",
    "number_of_trades",
    "taker_buy_base_asset_volume",
    "taker_buy_quote_asset_volume",
    "ignore",
]


def extract_zip_files(input_dir: Path, extract_dir: Path, symbol: str) -> list[Path]:
    """解压 input_dir 下指定交易对的 zip，并返回解压出的 csv 文件列表。"""
    zip_files = sorted(input_dir.glob(f"{symbol}-*.zip"))
    if not zip_files:
        raise FileNotFoundError(f"No zip files found for {symbol} in: {input_dir}")

    extract_dir.mkdir(parents=True, exist_ok=True)
    extracted_csv_files: list[Path] = []

    for zip_path in zip_files:
        target_subdir = extract_dir / zip_path.stem
        target_subdir.mkdir(parents=True, exist_ok=True)

        with ZipFile(zip_path, "r") as zf:
            zf.extractall(target_subdir)

        extracted_csv_files.extend(sorted(target_subdir.rglob("*.csv")))

    return extracted_csv_files


def is_header_row(row: list[str]) -> bool:
    """粗略判断一行是否是表头。"""
    if not row:
        return False

    first = row[0].strip().lower()
    if first in {"open_time", "timestamp", "time"}:
        return True

    try:
        int(first)
        return False
    except ValueError:
        return True


def merge_csv_files(csv_files: list[Path], output_csv: Path) -> int:
    """将多个 csv 合并为一个文件，返回写入的数据行数。"""
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    rows_written = 0
    header_written = False

    with output_csv.open("w", newline="", encoding="utf-8") as out_f:
        writer = csv.writer(out_f)

        for csv_path in csv_files:
            with csv_path.open("r", newline="", encoding="utf-8") as in_f:
                reader = csv.reader(in_f)
                first_row = next(reader, None)
                if first_row is None:
                    continue

                if is_header_row(first_row):
                    if not header_written:
                        writer.writerow(first_row)
                        header_written = True
                else:
                    if not header_written:
                        writer.writerow(DEFAULT_COLUMNS)
                        header_written = True
                    writer.writerow(first_row)
                    rows_written += 1

                for row in reader:
                    if row:
                        writer.writerow(row)
                        rows_written += 1

    return rows_written


def main() -> None:
    if not isinstance(SYMBOLS, list) or not SYMBOLS or any(
        not isinstance(symbol, str) or not symbol.strip() for symbol in SYMBOLS
    ):
        raise ValueError('SYMBOLS must be a non-empty list (e.g. ["BTCUSDT", "ETHUSDT"])')
    symbols = list(dict.fromkeys(symbol.strip().upper() for symbol in SYMBOLS))
    if any(not symbol.isascii() or not symbol.isalnum() for symbol in symbols):
        raise ValueError("SYMBOLS must contain only letters and digits")

    input_dir = Path("./marketData")

    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory does not exist: {input_dir}")

    for symbol in symbols:
        extract_dir = input_dir / "unzipped" / symbol
        output_csv = Path("./CleanData") / f"kline{symbol}.csv"

        if not any(input_dir.glob(f"{symbol}-*.zip")):
            print(f"Skipping symbol: {symbol} (no zip files found in: {input_dir})")
            continue

        if extract_dir.exists():
            shutil.rmtree(extract_dir)

        csv_files = extract_zip_files(input_dir, extract_dir, symbol)
        rows = merge_csv_files(csv_files, output_csv)

        print(f"Processed symbol: {symbol}")
        print(f"Processed zip files from: {input_dir}")
        print(f"Extracted CSV files: {len(csv_files)}")
        print(f"Merged rows: {rows}")
        print(f"Output CSV: {output_csv}")


if __name__ == "__main__":
    main()
