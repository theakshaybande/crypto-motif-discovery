"""Download Binance 1m data, compute features, and persist parquet output."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data_fetch import download_binance_1m_klines  # noqa: E402
from src.features import compute_features  # noqa: E402
from src.utils import data_path, load_binance_zip_files  # noqa: E402


def main() -> None:
    """Run baseline data ingestion and feature preparation."""
    symbol = "BTCUSDT"
    year = 2025
    months = [1, 2, 3]

    archives = download_binance_1m_klines(
        symbol=symbol,
        year=year,
        months=months,
        dest_dir=data_path("raw"),
    )
    if not archives:
        print("No archives downloaded. Check symbol/year/month availability.")
        return

    raw_df = load_binance_zip_files(archives)
    feature_df = compute_features(raw_df)

    month_label = f"{months[0]:02d}_{months[-1]:02d}"
    out_file = data_path("processed") / f"{symbol}-1m-{year}-{month_label}-features.parquet"
    feature_df.to_parquet(out_file, index=False)

    start = feature_df["open_time"].min() if "open_time" in feature_df.columns else None
    end = feature_df["open_time"].max() if "open_time" in feature_df.columns else None

    print("Download and feature generation complete.")
    print(f"Archives: {len(archives)}")
    print(f"Rows: {len(feature_df):,}")
    print(f"Time range: {start} -> {end}")
    print(f"Saved parquet: {Path(out_file).resolve()}")

    # TODO: support CLI args for symbol, interval, and date ranges.


if __name__ == "__main__":
    main()
