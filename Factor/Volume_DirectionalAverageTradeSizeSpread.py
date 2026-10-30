# ==============================================================================
# Factor Category: Volume
# Factor Name: Volume_DirectionalAverageTradeSizeSpread
# Description: difference of average execution value in up and down bars
# ==============================================================================

import os
from pathlib import Path

import pandas as pd

BACKTEST_START_DATE = "20100101"
SYMBOL = "BTCUSDT"


def _default_paths_local(current_file):
    root = Path(current_file).resolve().parent.parent
    return root / "CleanData" / f"kline{SYMBOL}.csv", root / "Result"


def _prepare_crypto_dataframe_local(df):
    required = ["close_time", "close", "quote_volume", "count"]
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f"CleanData/kline{SYMBOL}.csv missing required columns: {missing}")
    df = df.copy()
    for column in required:
        df[column] = pd.to_numeric(df[column], errors="raise")
    df = df.dropna(subset=["close_time"]).sort_values("close_time")
    df.index = df["close_time"].astype(str)
    return df


def _factor_name():
    return os.path.splitext(os.path.basename(__file__))[0]


def _param_str():
    return "N21"


def _calc_signal(df):
    returns = df["close"] / df["close"].shift(1).replace(0, float("nan")) - 1
    valid = returns.notna() & df["quote_volume"].notna() & df["count"].notna()
    up_quote = df["quote_volume"].where(returns > 0, 0.0).where(valid).rolling(20).sum()
    down_quote = df["quote_volume"].where(returns < 0, 0.0).where(valid).rolling(20).sum()
    up_count = df["count"].where(returns > 0, 0.0).where(valid).rolling(20).sum()
    down_count = df["count"].where(returns < 0, 0.0).where(valid).rolling(20).sum()
    return up_quote / up_count.replace(0, float("nan")) - down_quote / down_count.replace(0, float("nan"))


def _load_btc_signal(filepath):
    frame = _prepare_crypto_dataframe_local(pd.read_csv(filepath))
    return _calc_signal(frame).rename(SYMBOL)


def _save_single_symbol_signal_local(signal, factor_name, param_str, output_dir, backtest_start_date, symbol=SYMBOL):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    signals = signal.to_frame().sort_index().astype(float)
    signals = signals[signals.index >= str(backtest_start_date)]
    output_path = output_dir / f"{factor_name}_{symbol}_{param_str}_RAW_Position.csv"
    signals.to_csv(output_path, encoding="utf-8-sig")
    print(f"Factor {factor_name} output saved: {output_path}")


def main():
    kline_path, output_dir = _default_paths_local(__file__)
    _save_single_symbol_signal_local(
        _load_btc_signal(kline_path), _factor_name(), _param_str(), output_dir,
        BACKTEST_START_DATE, symbol=SYMBOL,
    )


if __name__ == "__main__":
    main()
