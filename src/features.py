"""Feature engineering helpers for OHLCV market data."""

from __future__ import annotations

import numpy as np
import pandas as pd


def compute_features(df: pd.DataFrame) -> pd.DataFrame:
    """Compute a small baseline feature set from raw OHLCV data.

    Expected input columns include:
    ``open``, ``high``, ``low``, ``close``, ``volume``.
    """
    required = {"open", "high", "low", "close", "volume"}
    missing = required - set(df.columns)
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise ValueError(f"DataFrame is missing required columns: {missing_list}")

    out = df.copy()

    numeric_cols = ["open", "high", "low", "close", "volume"]
    out[numeric_cols] = out[numeric_cols].apply(pd.to_numeric, errors="coerce")

    close = out["close"].replace(0.0, np.nan)
    out["log_return"] = np.log(close).diff()
    out["spread"] = (out["high"] - out["low"]) / close

    rolling_window = 60
    vol_mean = out["volume"].rolling(rolling_window, min_periods=20).mean()
    vol_std = out["volume"].rolling(rolling_window, min_periods=20).std()
    out["volume_zscore"] = (out["volume"] - vol_mean) / vol_std.replace(0.0, np.nan)

    out["hlc3"] = (out["high"] + out["low"] + out["close"]) / 3.0
    out["close_sma_30"] = out["close"].rolling(30, min_periods=10).mean()

    # TODO: add regime-aware and multi-scale volatility features.
    return out
