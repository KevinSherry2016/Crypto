"""Buying/Selling Pressure BTCUSDT N120 state-machine factor."""

from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from crypto_factor_runtime import run_factor


def calculate_raw_signal(data: pd.DataFrame) -> pd.Series:
    pressure = (data["close"] - data["low"]) / (data["high"] - data["low"] + 1e-9)
    return (pressure.rolling(120).mean() - 0.5) * 2


if __name__ == "__main__":
    run_factor(Path(__file__), "BTCUSDT", "Microstructure_BuyingSellingPressure", "N120", "state_machine", calculate_raw_signal)