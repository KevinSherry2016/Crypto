"""Count records in merged CleanData/kline*.csv files (header excluded).

Run: python Data\\check_merged_marketData.py
Output: Result/market_data_record_counts.csv with symbol,record_count columns.
Empty files and header-only files have zero records; blank rows are ignored.
Paths are relative to the repository root, not the current working directory.
"""

import csv
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = ROOT_DIR / "CleanData"
OUTPUT_CSV = ROOT_DIR / "Result" / "market_data_record_counts.csv"


def count_records(csv_path: Path) -> int:
    """Count non-blank data rows in a merged CSV containing a header."""
    with csv_path.open("r", newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.reader(csv_file)
        next(reader, None)
        return sum(1 for row in reader if any(field.strip() for field in row))


def main() -> None:
    if not INPUT_DIR.is_dir():
        raise FileNotFoundError(f"Input directory does not exist: {INPUT_DIR}")

    csv_files = sorted(path for path in INPUT_DIR.glob("kline*.csv") if path.is_file())
    if not csv_files:
        raise FileNotFoundError(f"No merged kline CSV files found in: {INPUT_DIR}")

    counts = [
        (csv_path.stem.removeprefix("kline"), count_records(csv_path))
        for csv_path in csv_files
    ]

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8-sig") as output_file:
        writer = csv.writer(output_file)
        writer.writerow(["symbol", "record_count"])
        writer.writerows(counts)

    print(f"Checked symbols: {len(counts)}")
    print(f"Total records: {sum(count for _, count in counts)}")
    print(f"Output CSV: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
