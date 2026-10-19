"""Price/Volume Correlation SOLUSDT N50 tanh factor."""

from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from crypto_factor_runtime import run_factor


def calculate_raw_signal(data: pd.DataFrame) -> pd.Series:
    return data["close"].pct_change(fill_method=None).rolling(50).corr(data["volume"].pct_change(fill_method=None))


if __name__ == "__main__":
    run_factor(Path(__file__), "SOLUSDT", "Volume_PriceVolumeCorrelation", "N50", "tanh", calculate_raw_signal)