"""OI Price Flow SOLUSDT N50 raw factor."""

from pathlib import Path
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from crypto_factor_runtime import run_factor


def calculate_raw_signal(data: pd.DataFrame) -> pd.Series:
    oi = data.get("oi", data.get("OpenInterest", data.get("quote_volume", data["volume"]))).astype(float)
    return (np.sign(data["close"].pct_change()) * oi.pct_change()).rolling(50).mean()


if __name__ == "__main__":
    run_factor(Path(__file__), "SOLUSDT", "Volume_OIPriceFlow", "N50", "raw", calculate_raw_signal)