"""Convert open_time/close_time columns in CleanData CSV files to YYYYMMDDHHMMSS.

Usage:
    python Utility/convert_cleandata_time_columns.py
    python Utility/convert_cleandata_time_columns.py --input-dir CleanData --recursive
"""

from __future__ import annotations

import argparse
from pathlib import Path
import re

import pandas as pd

TIME_COLUMNS = ("open_time", "close_time")
OUTPUT_TIME_FORMAT = "%Y%m%d%H%M%S"
FOURTEEN_DIGIT_RE = re.compile(r"^\d{14}$")


def _repair_close_time_from_open_time(df: pd.DataFrame) -> tuple[pd.Series, bool]:
    close_text = df["close_time"].astype("string")
    open_text = df["open_time"].astype("string")

    open_dt = pd.to_datetime(open_text, format=OUTPUT_TIME_FORMAT, errors="coerce", utc=True)
    close_dt = pd.to_datetime(close_text, format=OUTPUT_TIME_FORMAT, errors="coerce", utc=True)

    if open_dt.notna().sum() < 2:
        return close_text, False

    diffs = open_dt.diff().dt.total_seconds().dropna()
    positive_diffs = diffs[diffs > 0]
    bar_seconds = int(positive_diffs.median()) if not positive_diffs.empty else 3600
    bar_seconds = max(bar_seconds, 1)

    expected_close = open_dt + pd.to_timedelta(bar_seconds - 1, unit="s")

    comparable = open_dt.notna() & close_dt.notna()
    if comparable.any():
        mismatch_ratio = (close_dt[comparable] != expected_close[comparable]).mean()
    else:
        mismatch_ratio = 0.0

    if mismatch_ratio < 0.5:
        return close_text, False

    repaired = close_text.copy()
    valid_open = open_dt.notna()
    repaired.loc[valid_open] = expected_close[valid_open].dt.strftime(OUTPUT_TIME_FORMAT)
    return repaired, True


def _to_yyyymmddhhmmss(raw: pd.Series) -> pd.Series:
    text = raw.astype("string")
    numeric_all = pd.to_numeric(text, errors="coerce")

    result = text.copy()

    # Repair legacy broken values like 20240101000 (original epoch-ms value divided by 1000).
    legacy_broken = text.str.fullmatch(r"^\d{11}$", na=False) & numeric_all.notna()
    if legacy_broken.any():
        restored_ms = (numeric_all[legacy_broken].astype("Int64") * 1000).astype("Int64")
        result.loc[legacy_broken] = restored_ms.astype("string")

    as_14_digit = text.str.fullmatch(FOURTEEN_DIGIT_RE.pattern, na=False)
    parsed_14 = pd.to_datetime(text.where(as_14_digit), format=OUTPUT_TIME_FORMAT, errors="coerce", utc=True)
    plausible_14 = as_14_digit & parsed_14.notna() & parsed_14.dt.year.between(1990, 2100)

    # Repair values that look like accidental second-pass conversions (e.g. year 26xx).
    corrupted_14 = as_14_digit & parsed_14.notna() & (parsed_14.dt.year > 2100)
    if corrupted_14.any():
        recovered_ms = parsed_14[corrupted_14].map(lambda ts: int(ts.timestamp() * 1000)).astype("Int64")
        result.loc[corrupted_14] = recovered_ms.astype("string")

    pending = ~(plausible_14 | corrupted_14 | legacy_broken)
    numeric = pd.to_numeric(text.where(pending), errors="coerce")

    # Normalize all numeric timestamps to milliseconds first to avoid dtype-unit conflicts.
    normalized_ms = numeric.where(numeric.abs() >= 10**12, numeric * 1000)
    parsed = pd.to_datetime(normalized_ms, unit="ms", errors="coerce", utc=True)

    # Parse non-numeric datetime strings as a fallback.
    needs_fallback = pending & parsed.isna() & text.notna()
    if needs_fallback.any():
        fallback = pd.to_datetime(text[needs_fallback], errors="coerce", utc=True)
        parsed.loc[needs_fallback] = fallback

    formatted = parsed.dt.strftime(OUTPUT_TIME_FORMAT)
    result.loc[pending] = formatted.where(formatted.notna(), text[pending])
    return result


def _process_file(csv_path: Path) -> tuple[bool, list[str]]:
    df = pd.read_csv(csv_path, dtype="string")
    changed_cols: list[str] = []

    for col in TIME_COLUMNS:
        if col not in df.columns:
            continue

        converted = _to_yyyymmddhhmmss(df[col])
        if not converted.equals(df[col]):
            df[col] = converted
            changed_cols.append(col)

    if "open_time" in df.columns and "close_time" in df.columns:
        repaired_close, repaired = _repair_close_time_from_open_time(df)
        if repaired and not repaired_close.equals(df["close_time"]):
            df["close_time"] = repaired_close
            if "close_time" not in changed_cols:
                changed_cols.append("close_time")

    if not changed_cols:
        return False, []

    df.to_csv(csv_path, index=False, encoding="utf-8")
    return True, changed_cols


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert open_time/close_time in CleanData CSV files to YYYYMMDDHHMMSS.",
    )
    parser.add_argument(
        "--input-dir",
        default=str(Path(__file__).resolve().parent.parent / "CleanData"),
        help="Directory that contains CSV files (default: ./CleanData)",
    )
    parser.add_argument(
        "--pattern",
        default="*.csv",
        help="Glob pattern for input CSV files (default: *.csv)",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Search CSV files recursively",
    )
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    if not input_dir.exists() or not input_dir.is_dir():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    csv_iter = input_dir.rglob(args.pattern) if args.recursive else input_dir.glob(args.pattern)
    csv_files = sorted(p for p in csv_iter if p.is_file())

    if not csv_files:
        print(f"No CSV files found in {input_dir} with pattern {args.pattern}")
        return

    changed = 0
    scanned = 0
    for csv_path in csv_files:
        scanned += 1
        updated, columns = _process_file(csv_path)
        if updated:
            changed += 1
            cols_text = ", ".join(columns)
            print(f"Updated: {csv_path} ({cols_text})")
        else:
            print(f"Skipped: {csv_path} (no open_time/close_time changes)")

    print(f"Done. Scanned {scanned} file(s), updated {changed} file(s).")


if __name__ == "__main__":
    main()
