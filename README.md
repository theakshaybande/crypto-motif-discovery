# Crypto Motif Discovery

Research repository for finding repeated intraday structure (motifs) in crypto time series using Matrix Profile methods.

This project currently focuses on:
- BTCUSDT spot market data from Binance Vision
- 1-minute OHLCV candles
- Jan-Mar 2025 sample period
- univariate motif discovery on log returns
- volatility regime context around detected motifs

## Why This Project Exists

Crypto markets produce recurring microstructure patterns (volatility bursts, mean-reversion clusters, momentum pulses) that are hard to identify with simple indicators.

Matrix Profile provides a robust way to scan long time series for:
- motifs (highly similar repeated subsequences)
- discords (rare or anomalous subsequences)

This repository is a reproducible baseline pipeline to:
1. pull exchange data,
2. create core features,
3. run motif detection,
4. analyze motif behavior across volatility regimes.

## Current Results Snapshot

From the current notebook/script run state in this repo:
- Data coverage: `2025-01-01 00:00:00+00:00` to `2025-03-31 23:59:00+00:00`
- Total rows: `129,600` (3 months of 1-minute candles)
- Processed artifact: `data/processed/BTCUSDT-1m-2025-01_03-features.parquet`
- Matrix Profile window: `m = 60` minutes
- Best motif pair indices: `13710` and `61230`
- Minimum motif distance: `2.7217`
- Motif timestamps (Notebook 03 outputs):
`2025-01-10 12:30:00+00:00` and `2025-02-12 12:30:00+00:00`

## Repository Structure

```text
crypto-motif-discovery/
|-- data/
|   |-- raw/                  # downloaded Binance monthly zip files
|   `-- processed/            # feature parquet outputs
|-- notebooks/
|   |-- 01_download_and_prepare.ipynb
|   |-- 02_matrix_profile.ipynb
|   `-- 03_volatility_regimes.ipynb
|-- scripts/
|   `-- download_data.py      # end-to-end ingestion + feature build
|-- src/
|   |-- data_fetch.py         # Binance Vision downloader
|   |-- features.py           # feature engineering
|   |-- utils.py              # paths, zip readers, parquet loaders
|   `-- init.py               # package marker (see notes below)
|-- requirements.txt
`-- README.md
```

## End-to-End Pipeline

### 1. Data Acquisition

`src/data_fetch.py` downloads monthly Binance Vision archives from:
`https://data.binance.vision/data/spot/monthly/klines/{SYMBOL}/1m/`

The default script setup in `scripts/download_data.py` is:
- symbol: `BTCUSDT`
- year: `2025`
- months: `[1, 2, 3]`

### 2. Data Loading and Normalization

`src/utils.py`:
- reads CSV from each zip archive
- applies Binance kline column schema
- converts timestamps to UTC datetimes
- enforces numeric dtypes for OHLCV and trade volume fields
- concatenates and sorts by `open_time`

### 3. Feature Engineering

`src/features.py` computes baseline features:
- `log_return = log(close).diff()`
- `spread = (high - low) / close`
- `volume_zscore` using rolling mean/std over 60 bars (`min_periods=20`)
- `hlc3 = (high + low + close) / 3`
- `close_sma_30` with rolling mean over 30 bars (`min_periods=10`)

### 4. Motif Discovery

`notebooks/02_matrix_profile.ipynb` applies STUMPY:
- input signal: `log_return` series
- algorithm: `stumpy.stump` (STOMP family)
- subsequence window: `m = 60`
- similarity metric: z-normalized Euclidean distance

Low matrix profile values indicate strong repeated patterns.

### 5. Volatility Regime Context

`notebooks/03_volatility_regimes.ipynb`:
- computes rolling realized volatility (`rolling_vol_60 = std(log_return, m=60)`)
- labels regimes by empirical quantiles:
`Low Vol` (< 33rd pct), `Normal` (33rd-66th), `High Vol` (> 66th)
- overlays motif windows on price/regime plots
- compares motif occurrences against regime labels

## Quick Start

### Prerequisites

- Python 3.10+ (3.12 also works in the current environment)
- pip

### Setup (Windows PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Setup (macOS/Linux)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Build Dataset + Features

```bash
python scripts/download_data.py
```

Expected console summary includes:
- number of archives used
- total rows
- time range
- saved parquet path

### Run Notebooks

```bash
jupyter lab
```

Recommended execution order:
1. `notebooks/01_download_and_prepare.ipynb`
2. `notebooks/02_matrix_profile.ipynb`
3. `notebooks/03_volatility_regimes.ipynb`

## Output Artifacts

Raw inputs (ignored by git):
- `data/raw/BTCUSDT-1m-2025-01.zip`
- `data/raw/BTCUSDT-1m-2025-02.zip`
- `data/raw/BTCUSDT-1m-2025-03.zip`

Processed output (ignored by git):
- `data/processed/BTCUSDT-1m-2025-01_03-features.parquet`

## Customization

### Change symbol/date range

Edit `scripts/download_data.py`:
- `symbol`
- `year`
- `months`

### Programmatic usage

```python
from src.data_fetch import download_binance_1m_klines
from src.features import compute_features
from src.utils import data_path, load_binance_zip_files

archives = download_binance_1m_klines("ETHUSDT", 2025, [1, 2], dest_dir=data_path("raw"))
raw_df = load_binance_zip_files(archives)
feat_df = compute_features(raw_df)
feat_df.to_parquet(data_path("processed") / "ETHUSDT-1m-2025-01_02-features.parquet", index=False)
```

### Change motif horizon

In `notebooks/02_matrix_profile.ipynb`, modify:
- `m = 60`

Examples:
- `m = 15` for micro-patterns
- `m = 120` for broader intraday structure

## Limitations (Current State)

- Script configuration is hardcoded (no CLI args yet).
- No automated test suite yet.
- Checksum validation for Binance downloads is not implemented.
- Motif discovery is currently univariate (`log_return` only).
- `src/init.py` is named `init.py`; standard package style would be `__init__.py`.
- No trading strategy or execution model is implemented.

## Roadmap

Planned improvements:
- CLI/config-driven ingestion (symbol, interval, date ranges)
- multi-scale motif experiments (`m` grid search)
- discord analysis and anomaly labeling
- multivariate motif discovery
- stronger feature library (regime-aware and microstructure features)
- benchmark metrics and reproducibility reports
- unit tests and CI checks

## Reproducibility Notes

- Data files are intentionally git-ignored (`data/raw`, `data/processed`).
- Notebook outputs depend on the exact downloaded archives and feature transforms.
- Matrix Profile is deterministic for fixed input series and window length.

## Disclaimer

This is a research project for time-series analysis and pattern discovery.
It is not financial advice.

## Acknowledgments

- Binance Vision public market data archives
- STUMPY for Matrix Profile computation
