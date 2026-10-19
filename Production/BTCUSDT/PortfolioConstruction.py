"""Build the BTCUSDT recommended-factor portfolio using reference-style normalization."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


SYMBOL = "BTCUSDT"
PORTFOLIO_NAME = "BTCUSDT_RecommendedPortfolio"
HOURS_PER_YEAR = 365 * 24
NORM_START_DATE = "20240101000000"
NORM_END_DATE = "20260630230000"
BASE_DIR = Path(__file__).resolve().parent
RESULT_DIR = BASE_DIR / "Result"
FACTOR_WEIGHTS = {
    "Volume_CMF_BTCUSDT_N180_STATE_MACHINE_position_normalized.csv": 0.50,
    "Microstructure_BuyingSellingPressure_BTCUSDT_N120_STATE_MACHINE_position_normalized.csv": 0.50,
}


def load_position(name: str) -> pd.Series:
    frame = pd.read_csv(RESULT_DIR / name, index_col=0)
    series = pd.to_numeric(frame[SYMBOL], errors="coerce").fillna(0.0)
    series.index = series.index.astype(str)
    return series


def main() -> None:
    RESULT_DIR.mkdir(exist_ok=True)
    positions = [load_position(name).rename(name) * weight for name, weight in FACTOR_WEIGHTS.items()]
    combined = pd.concat(positions, axis=1).fillna(0.0).sum(axis=1) / sum(abs(weight) for weight in FACTOR_WEIGHTS.values())
    market = pd.read_csv(BASE_DIR.parents[1] / "CleanData" / f"kline{SYMBOL}.csv")
    market.index = market["close_time"].astype(str)
    close = pd.to_numeric(market["close"], errors="coerce").reindex(combined.index).ffill()
    returns = close.pct_change(fill_method=None).fillna(0.0)
    raw_pnl = combined.shift(1).fillna(0.0) * returns
    sample_pnl = raw_pnl.loc[NORM_START_DATE:NORM_END_DATE]
    normalization_scale = sample_pnl.std() or 1.0
    standardized_position = combined / normalization_scale
    standardized_pnl = raw_pnl / normalization_scale
    cumulative_pnl = standardized_pnl.cumsum()
    volatility = standardized_pnl.loc[NORM_START_DATE:NORM_END_DATE].std() * np.sqrt(HOURS_PER_YEAR)
    sharpe = standardized_pnl.mean() / standardized_pnl.std() * np.sqrt(HOURS_PER_YEAR)
    metrics = {"symbol": SYMBOL, "portfolio": PORTFOLIO_NAME, "factor_weights": FACTOR_WEIGHTS, "normalization_scale": float(normalization_scale), "annualized_volatility": float(volatility), "sharpeRatio": float(sharpe), "maxDrawdown": float((cumulative_pnl - cumulative_pnl.cummax()).min())}
    standardized_position.to_frame(SYMBOL).to_csv(RESULT_DIR / f"{PORTFOLIO_NAME}_norm_Position.csv", encoding="utf-8-sig")
    pd.DataFrame({"PnL": standardized_pnl, "cumulativePnl": cumulative_pnl}).to_csv(RESULT_DIR / f"{PORTFOLIO_NAME}_norm_PnL.csv", encoding="utf-8-sig")
    standardized_position.abs().to_frame("GMV").to_csv(RESULT_DIR / f"{PORTFOLIO_NAME}_GMV.csv", encoding="utf-8-sig")
    dates = pd.to_datetime(standardized_pnl.index, format="%Y%m%d%H%M%S")
    figure, axis = plt.subplots(figsize=(14, 5))
    axis.plot(dates, cumulative_pnl, linewidth=1.5, color="#1f77b4")
    axis.set_title(f"{PORTFOLIO_NAME} | Sharpe: {sharpe:.2f} | Vol: {volatility:.2f}")
    axis.xaxis.set_major_locator(mdates.YearLocator())
    axis.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    figure.tight_layout()
    figure.savefig(RESULT_DIR / f"{PORTFOLIO_NAME}_cPnL.png", dpi=150)
    plt.close(figure)
    (RESULT_DIR / f"{PORTFOLIO_NAME}_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()