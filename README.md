# crypto-motif-discovery

A lightweight research project for discovering repeating motifs in cryptocurrency time series.

## Purpose

This repo provides a minimal end-to-end workflow for:

- downloading Binance 1-minute OHLCV data,
- preparing engineered features,
- running Matrix Profile motif discovery with STUMPY.

## Quick Start

1. Create and activate a Python 3.10 virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Download and prepare data:

```bash
python scripts/download_data.py
```

4. Explore notebooks:

- `notebooks/01_download_and_prepare.ipynb`
- `notebooks/02_matrix_profile.ipynb`

## Notes

- Raw and processed datasets are ignored by git by default.
- TODO: add tests, config-driven symbols/intervals, and richer feature engineering.
