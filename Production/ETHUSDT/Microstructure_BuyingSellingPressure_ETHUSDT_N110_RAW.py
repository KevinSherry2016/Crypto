"""Buying/Selling Pressure ETHUSDT N110 raw factor."""

from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from crypto_factor_runtime import run_factor


def calculate_raw_signal(data: pd.DataFrame) -> pd.Series:
    pressure = (data["close"] - data["low"]) / (data["high"] - data["low"] + 1e-9)
    return (pressure.rolling(110).mean() - 0.5) * 2


if __name__ == "__main__":
    run_factor(Path(__file__), "ETHUSDT", "Microstructure_BuyingSellingPressure", "N110", "raw", calculate_raw_signal)