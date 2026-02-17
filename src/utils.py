"""Shared path and data loading helpers."""

from __future__ import annotations

from pathlib import Path
from zipfile import ZipFile
import pandas as pd


# -----------------------------------------------------------------------------
# Binance Kline Schema (official column order)
# -----------------------------------------------------------------------------

BINANCE_KLINE_COLUMNS = [
    "open_time",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "close_time",
    "quote_asset_volume",
    "number_of_trades",
    "taker_buy_base_asset_volume",
    "taker_buy_quote_asset_volume",
    "ignore",
]


# -----------------------------------------------------------------------------
# Project Paths
# -----------------------------------------------------------------------------

def project_root() -> Path:
    """Return the repository root directory."""
    return Path(__file__).resolve().parents[1]


def data_path(kind: str) -> Path:
    """Return data directory path by kind: 'raw' or 'processed'."""
    if kind not in {"raw", "processed"}:
        raise ValueError("kind must be either 'raw' or 'processed'")
    path = project_root() / "data" / kind
    path.mkdir(parents=True, exist_ok=True)
    return path


# -----------------------------------------------------------------------------
# Binance Zip Readers
# -----------------------------------------------------------------------------

def read_binance_zip(zip_path: str | Path) -> pd.DataFrame:
    """
    Load a single Binance kline zip archive into a DataFrame.
    Ensures:
        - Correct column ordering
        - Strict dtype enforcement
        - Proper timestamp conversion
        - Sorting by open_time
    """
    zip_path = Path(zip_path)

    with ZipFile(zip_path) as zf:
        csv_members = [name for name in zf.namelist() if name.endswith(".csv")]
        if not csv_members:
            raise ValueError(f"No CSV file found inside archive: {zip_path}")

        with zf.open(csv_members[0]) as fh:
            df = pd.read_csv(
                fh,
                header=None,
                names=BINANCE_KLINE_COLUMNS,
                dtype={
                    "open_time": "int64",
                    "close_time": "int64",
                },
            )

    # ---- Convert timestamps (CRITICAL) ----
    df["open_time"] = pd.to_datetime(df["open_time"], unit="us", utc=True)
    df["close_time"] = pd.to_datetime(df["close_time"], unit="us", utc=True)


    # ---- Force numeric types safely ----
    numeric_cols = [
        "open",
        "high",
        "low",
        "close",
        "volume",
        "quote_asset_volume",
        "number_of_trades",
        "taker_buy_base_asset_volume",
        "taker_buy_quote_asset_volume",
    ]

    df[numeric_cols] = df[numeric_cols].apply(
        pd.to_numeric, errors="coerce"
    )

    # ---- Basic sanity check ----
    if df["open_time"].dt.year.min() < 2017:
        raise ValueError("Timestamp conversion failed — check data integrity.")

    return df.sort_values("open_time").reset_index(drop=True)


def load_binance_zip_files(paths: list[str | Path]) -> pd.DataFrame:
    """Load and concatenate multiple Binance zip archives."""
    frames = [read_binance_zip(path) for path in paths]

    if not frames:
        return pd.DataFrame(columns=BINANCE_KLINE_COLUMNS)

    combined = pd.concat(frames, ignore_index=True)
    return combined.sort_values("open_time").reset_index(drop=True)


# -----------------------------------------------------------------------------
# Parquet Loader
# -----------------------------------------------------------------------------

def load_multiple_parquets(paths: list[str | Path]) -> pd.DataFrame:
    """Load and concatenate multiple parquet files."""
    frames = [pd.read_parquet(path) for path in paths]

    if not frames:
        return pd.DataFrame()

    combined = pd.concat(frames, ignore_index=True)

    if "open_time" in combined.columns:
        combined = combined.sort_values("open_time")

    return combined.reset_index(drop=True)
