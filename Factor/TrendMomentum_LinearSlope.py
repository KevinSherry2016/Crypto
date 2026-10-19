# ==============================================================================
# Factor Category: TrendMomentum
# Factor Name: TrendMomentum_LinearSlope
# Description: factor signal definition
# ==============================================================================

import pandas as pd
import numpy as np
import os
from pathlib import Path
BACKTEST_START_DATE = '20100101'
SYMBOL = 'BTCUSDT'
N_LIST = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120]
EXCLUDED_SECTORS = ['Bond', 'StockIndex', 'Other', 'Others', 'Financial']
EXCLUDED_SYMBOLS = []
CUSTOM_GROUPS = [
    {
        'name': 'CustomSymbols',
        'symbols': []
    }
]


RUN_ALL = True
SECTOR_LIST = []
RUN_CUSTOM_SYMBOLS = True



def _default_paths_local(current_file):
    project_root = Path(current_file).resolve().parent.parent
    return project_root / "CleanData" / f"kline{SYMBOL}.csv", project_root / "Result"


def _prepare_crypto_dataframe_local(df):
    required = ["close_time", "open", "high", "low", "close", "volume"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"CleanData/kline{SYMBOL}.csv missing required columns: {missing}")

    numeric_cols = ["close_time", "open", "high", "low", "close", "volume", "quote_volume", "count", "oi", "OpenInterest"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["close_time", "close"]).copy()
    df = df.sort_values("close_time")
    df["trade_date"] = df["close_time"].astype(str)

    alias_map = {
        "open": "adj_open",
        "high": "adj_high",
        "low": "adj_low",
        "close": "adj_close",
        "volume": "adj_volume",
    }
    for raw_col, alias_col in alias_map.items():
        df[alias_col] = df[raw_col]

    if "vol" not in df.columns:
        df["vol"] = df["volume"]
    if "Volume" not in df.columns:
        df["Volume"] = df["volume"]

    if "oi" in df.columns and df["oi"].notna().any():
        oi_series = df["oi"]
    elif "OpenInterest" in df.columns and df["OpenInterest"].notna().any():
        oi_series = df["OpenInterest"]
    elif "quote_volume" in df.columns and df["quote_volume"].notna().any():
        oi_series = df["quote_volume"]
    elif "count" in df.columns and df["count"].notna().any():
        oi_series = df["count"]
    else:
        oi_series = df["volume"]

    df["oi"] = oi_series.astype(float)
    df["OpenInterest"] = df["oi"]
    df = df.set_index("trade_date")
    return df


def _load_btc_series_local(kline_path, calc_fn, symbol=SYMBOL):
    kline_path = Path(kline_path)
    if not kline_path.exists():
        raise FileNotFoundError(f"data file not found: {kline_path}")

    raw = pd.read_csv(kline_path)
    frame = _prepare_crypto_dataframe_local(raw)
    return calc_fn(frame).rename(symbol)


def _save_single_symbol_signal_local(signal, factor_name, param_str, output_dir, backtest_start_date, symbol=SYMBOL):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    signals = signal.to_frame().sort_index().fillna(0).astype(float)
    signals = signals[signals.index >= str(backtest_start_date)]

    raw_output_name = f"{factor_name}_{_safe_name(symbol)}_{param_str}_RAW_Position.csv"
    raw_output_path = output_dir / raw_output_name
    signals.to_csv(raw_output_path, encoding="utf-8-sig")
    print(f"Factor {factor_name} output saved: {raw_output_path}")
def _factor_name():
    return os.path.splitext(os.path.basename(__file__))[0]


def _safe_name(text):
    return ''.join(ch for ch in str(text) if ch.isalnum() or ch in ['_', '-', '.'])


def _param_str(n_value):
    return f"N{n_value}"


def _slope_normalized(arr):
    if np.isnan(arr).any():
        return np.nan
    x = np.arange(len(arr), dtype=float)
    x = x - x.mean()
    denom = (x ** 2).sum() + 1e-12
    slope = ((arr - arr.mean()) * x).sum() / denom
    return slope / (np.abs(arr).mean() + 1e-8)


def _calc_signal(df, n_value):
    close = df['adj_close']
    return close.rolling(window=n_value).apply(_slope_normalized, raw=True).fillna(0)



def _load_btc_signal(filepath, n_value):
    return _load_btc_series_local(
        filepath,
        lambda df: _calc_signal(df, n_value),
        symbol=SYMBOL,
    )


def main():
    kline_path, output_dir = _default_paths_local(__file__)

    print(f"Loading {_factor_name()} data from: {kline_path}")
    for n_value in N_LIST:
        signal = _load_btc_signal(kline_path, n_value)
        _save_single_symbol_signal_local(
            signal=signal,
            factor_name=_factor_name(),
            param_str=_param_str(n_value),
            output_dir=output_dir,
            backtest_start_date=BACKTEST_START_DATE,
            symbol=SYMBOL,
        )


if __name__ == "__main__":
    main()




