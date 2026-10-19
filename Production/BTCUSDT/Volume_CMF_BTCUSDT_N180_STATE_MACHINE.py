"""Volume_CMF BTCUSDT N180 state-machine factor."""

from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from crypto_factor_runtime import run_factor


def calculate_raw_signal(data: pd.DataFrame) -> pd.Series:
    multiplier = ((data["close"] - data["low"]) - (data["high"] - data["close"])) / (data["high"] - data["low"] + 1e-8)
    return (multiplier * data["volume"]).rolling(180, min_periods=1).sum() / data["volume"].rolling(180, min_periods=1).sum()


if __name__ == "__main__":
    run_factor(Path(__file__), "BTCUSDT", "Volume_CMF", "N180", "state_machine", calculate_raw_signal)