# ==============================================================================
# Factor Category: CrossSectional
# Factor Name: CrossSectional_Skewness
# Description: factor signal definition
# ==============================================================================

import os
from pathlib import Path

import pandas as pd


BACKTEST_START_DATE = "20100101"
N_LIST = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120]
SYMBOL = "BTCUSDT"


def _factor_name():
    return os.path.splitext(os.path.basename(__file__))[0]


def _safe_name(text):
    return "".join(ch for ch in str(text) if ch.isalnum() or ch in ["_", "-", "."])


def _param_str(n_value):
    return f"N{n_value}"


def _calc_signal(df, n_value):
    close = df["close"]
    ret = close.pct_change()
    return ret.rolling(window=n_value).skew()


def _load_btc_signal(filepath, n_value):
    if not filepath.exists():
        raise FileNotFoundError(f"data file not found: {filepath}")

    df = pd.read_csv(filepath)
    if "close_time" not in df.columns or "close" not in df.columns:
        raise ValueError("kline file must include columns: close_time, close")

    df["close_time"] = pd.to_numeric(df["close_time"], errors="coerce")
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df = df.dropna(subset=["close_time", "close"]).copy()

    # Use close_time as trade_date for crypto bars.
    df["trade_date"] = df["close_time"].astype(str)
    df = df.sort_values("close_time")
    df.set_index("trade_date", inplace=True)

    return _calc_signal(df, n_value).rename(SYMBOL)


def _run_and_save(signal, n_value, output_dir):
    signals = signal.to_frame().sort_index().fillna(0).astype(float)
    signals = signals[signals.index >= str(BACKTEST_START_DATE)]

    output_dir.mkdir(parents=True, exist_ok=True)
    raw_output_name = f"{_factor_name()}_{_safe_name(SYMBOL)}_{_param_str(n_value)}_RAW_Position.csv"
    raw_output_path = output_dir / raw_output_name
    signals.to_csv(raw_output_path, encoding="utf-8-sig")

    print(f"Factor {_factor_name()} output saved: {raw_output_path}")


def main():
    project_root = Path(__file__).resolve().parent.parent
    kline_path = project_root / "CleanData" / f"kline{SYMBOL}.csv"
    output_dir = project_root / "Result"

    print(f"Loading {_factor_name()} data from: {kline_path}")
    for n_value in N_LIST:
        signal = _load_btc_signal(kline_path, n_value)
        _run_and_save(signal, n_value, output_dir)


if __name__ == "__main__":
    main()


