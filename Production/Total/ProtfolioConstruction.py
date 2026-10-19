"""Build a BTCUSDT, ETHUSDT, and SOLUSDT inverse-volatility portfolio."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PORTFOLIO_NAME = "Total_RecommendedPortfolio"
HOURS_PER_YEAR = 365 * 24
HOURS_PER_DAY = 24
NORM_START_DATE = "20240101000000"
NORM_END_DATE = "20260630230000"
BASE_DIR = Path(__file__).resolve().parent
PRODUCTION_DIR = BASE_DIR.parent
RESULT_DIR = BASE_DIR / "Result"
ASSET_WEIGHT_RATIOS = {
    "BTCUSDT": 1.0,
    "ETHUSDT": 1.0,
    "SOLUSDT": 1.0,
}
PORTFOLIO_FILES = {
    "BTCUSDT": {
        "pnl": PRODUCTION_DIR / "BTCUSDT" / "Result" / "BTCUSDT_RecommendedPortfolio_norm_PnL.csv",
        "position": PRODUCTION_DIR / "BTCUSDT" / "Result" / "BTCUSDT_RecommendedPortfolio_norm_Position.csv",
    },
    "ETHUSDT": {
        "pnl": PRODUCTION_DIR / "ETHUSDT" / "Result" / "ETHUSDT_RecommendedPortfolio_norm_PnL.csv",
        "position": PRODUCTION_DIR / "ETHUSDT" / "Result" / "ETHUSDT_RecommendedPortfolio_norm_Position.csv",
    },
    "SOLUSDT": {
        "pnl": PRODUCTION_DIR / "SOLUSDT" / "Result" / "SOLUSDT_RecommendedPortfolio_norm_PnL.csv",
        "position": PRODUCTION_DIR / "SOLUSDT" / "Result" / "SOLUSDT_RecommendedPortfolio_norm_Position.csv",
    },
}


def load_series(path: Path, column: str, name: str) -> pd.Series:
    frame = pd.read_csv(path, index_col=0)
    series = pd.to_numeric(frame[column], errors="coerce")
    series.index = series.index.astype(str)
    return series.rename(name)


def calculate_manual_weights(symbols: pd.Index) -> pd.Series:
    ratios = pd.Series(ASSET_WEIGHT_RATIOS, dtype=float).reindex(symbols)
    if ratios.isna().any() or (ratios < 0).any() or ratios.sum() <= 0:
        raise ValueError("Manual asset weight ratios must be non-negative and sum to a positive value.")
    return ratios / ratios.sum()


def main() -> None:
    RESULT_DIR.mkdir(exist_ok=True)
    pnls = pd.concat(
        [load_series(files["pnl"], "PnL", symbol) for symbol, files in PORTFOLIO_FILES.items()],
        axis=1,
        join="inner",
    ).dropna()
    positions = pd.concat(
        [load_series(files["position"], symbol, symbol) for symbol, files in PORTFOLIO_FILES.items()],
        axis=1,
        join="inner",
    ).reindex(pnls.index).fillna(0.0)

    weights = calculate_manual_weights(pnls.columns)
    raw_pnl = pnls.mul(weights, axis=1).sum(axis=1)
    weighted_positions = positions.mul(weights, axis=1)
    sample_pnl = raw_pnl.loc[NORM_START_DATE:NORM_END_DATE]
    normalization_scale = sample_pnl.std()
    if not normalization_scale or np.isnan(normalization_scale):
        raise ValueError("The combined portfolio has no valid volatility in the normalization window.")

    normalized_pnl = raw_pnl / normalization_scale
    normalized_positions = weighted_positions / normalization_scale
    cumulative_pnl = normalized_pnl.cumsum()
    sharpe = normalized_pnl.mean() / normalized_pnl.std() * np.sqrt(HOURS_PER_YEAR)
    max_drawdown = (cumulative_pnl - cumulative_pnl.cummax()).min()
    gmv = normalized_positions.abs().sum(axis=1)
    turnover = normalized_positions.diff().abs().sum(axis=1).fillna(0.0)
    total_turnover = turnover.sum()
    holding_period_hours = (gmv.sum() / total_turnover) * 2 if total_turnover else float("nan")
    holding_period_days = holding_period_hours / HOURS_PER_DAY
    pot = (normalized_pnl.sum() / total_turnover) * 10000 if total_turnover else float("nan")
    metrics = {
        "portfolio": PORTFOLIO_NAME,
        "weighting_method": "manual_ratio",
        "asset_weight_ratios": ASSET_WEIGHT_RATIOS,
        "normalization_window": [NORM_START_DATE, NORM_END_DATE],
        "asset_weights": {symbol: float(value) for symbol, value in weights.items()},
        "final_normalization_scale": float(normalization_scale),
        "sharpeRatio": float(sharpe),
        "pot": float(pot),
        "holdingPeriod": float(holding_period_days),
        "holdingPeriodHours": float(holding_period_hours),
        "maxDrawdown": float(max_drawdown),
    }

    pd.DataFrame({"PnL": normalized_pnl, "cumulativePnl": cumulative_pnl}).to_csv(
        RESULT_DIR / f"{PORTFOLIO_NAME}_norm_PnL.csv", encoding="utf-8-sig"
    )
    normalized_positions.to_csv(RESULT_DIR / f"{PORTFOLIO_NAME}_norm_Position.csv", encoding="utf-8-sig")
    gmv.to_frame("GMV").to_csv(RESULT_DIR / f"{PORTFOLIO_NAME}_GMV.csv", encoding="utf-8-sig")
    turnover.to_frame("turnover").to_csv(RESULT_DIR / f"{PORTFOLIO_NAME}_turnover.csv", encoding="utf-8-sig")
    weights.to_frame("weight").to_csv(
        RESULT_DIR / f"{PORTFOLIO_NAME}_asset_weights.csv", encoding="utf-8-sig"
    )
    dates = pd.to_datetime(normalized_pnl.index, format="%Y%m%d%H%M%S")
    figure, axis = plt.subplots(figsize=(14, 5))
    axis.plot(dates, cumulative_pnl, linewidth=1.5, color="#1f77b4")
    axis.set_title(
        f"{PORTFOLIO_NAME} | Sharpe: {sharpe:.2f} | POT: {pot:.2f} | Hold: {holding_period_days:.1f}d"
    )
    axis.xaxis.set_major_locator(mdates.YearLocator())
    axis.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    figure.tight_layout()
    figure.savefig(RESULT_DIR / f"{PORTFOLIO_NAME}_cPnL.png", dpi=150)
    plt.close(figure)
    (RESULT_DIR / f"{PORTFOLIO_NAME}_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()