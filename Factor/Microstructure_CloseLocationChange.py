# ==============================================================================
# Factor Category: Microstructure
# Factor Name: Microstructure_CloseLocationChange
# Description: factor signal definition
# ==============================================================================

import pandas as pd
import numpy as np
import os
from pathlib import Path
BACKTEST_START_DATE = '20100101'
SYMBOL = 'BTCUSDT'
def _default_paths_local(current_file):
    project_root = Path(current_file).resolve().parent.parent
    return project_root / "CleanData" / f"kline{SYMBOL}.csv", project_root / "Result"


def _prepare_crypto_dataframe_local(df):
    required = ["close_time", "open", "high", "low", "close", "volume"]
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f"CleanData/kline{SYMBOL}.csv missing required columns: {missing}")

    for column in required:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    df = df.dropna(subset=["close_time", "close"]).sort_values("close_time").copy()
    df.index = df["close_time"].astype(str)
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

    signals = signal.to_frame().sort_index().astype(float)
    signals = signals[signals.index >= str(backtest_start_date)]

    raw_output_name = f"{factor_name}_{_safe_name(symbol)}_{param_str}_RAW_Position.csv"
    raw_output_path = output_dir / raw_output_name
    signals.to_csv(raw_output_path, encoding="utf-8-sig")
    print(f"Factor {factor_name} output saved: {raw_output_path}")
def _factor_name():
    return os.path.splitext(os.path.basename(__file__))[0]


def _safe_name(text):
    return ''.join(ch for ch in str(text) if ch.isalnum() or ch in ['_', '-', '.'])


def _param_str():
    return "N20"

def _calc_signal(df):
    close, high, low = df["close"], df["high"], df["low"]
    location = ((close-low)-(high-close))/(high-low).replace(0, float("nan"))
    return location.diff()

def _load_btc_signal(filepath):
    return _load_btc_series_local(filepath, _calc_signal, symbol=SYMBOL)

def main():
    kline_path, output_dir = _default_paths_local(__file__)
    print(f"Loading {_factor_name()} data from: {kline_path}")
    signal = _load_btc_signal(kline_path)
    _save_single_symbol_signal_local(
        signal=signal,
        factor_name=_factor_name(),
        param_str=_param_str(),
        output_dir=output_dir,
        backtest_start_date=BACKTEST_START_DATE,
        symbol=SYMBOL,
    )


if __name__ == "__main__":
    main()




