"""Utilities for downloading Binance kline archives."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import requests
from tqdm import tqdm

BINANCE_VISION_BASE = "https://data.binance.vision"


def download_binance_1m_klines(
    symbol: str,
    year: int,
    months: Iterable[int | str],
    dest_dir: str | Path | None = None,
    overwrite: bool = False,
    timeout: int = 30,
) -> list[Path]:
    """Download Binance monthly 1m kline zip files to ``data/raw``.

    Args:
        symbol: Trading pair, for example ``BTCUSDT``.
        year: Four-digit year, for example ``2025``.
        months: Iterable of month values, for example ``[1, 2, 3]``.
        dest_dir: Destination directory. Defaults to ``<repo>/data/raw``.
        overwrite: If True, replace existing files.
        timeout: HTTP request timeout in seconds.

    Returns:
        List of successfully downloaded local zip file paths.

    Notes:
        Files are sourced from the public Binance Vision archive:
        ``https://data.binance.vision``.
    """
    if dest_dir is None:
        dest = Path(__file__).resolve().parents[1] / "data" / "raw"
    else:
        dest = Path(dest_dir).resolve()
    dest.mkdir(parents=True, exist_ok=True)

    downloaded: list[Path] = []
    clean_symbol = symbol.upper()

    for month in months:
        month_num = int(month)
        month_str = f"{month_num:02d}"
        filename = f"{clean_symbol}-1m-{year}-{month_str}.zip"
        url = (
            f"{BINANCE_VISION_BASE}/data/spot/monthly/klines/"
            f"{clean_symbol}/1m/{filename}"
        )
        out_path = dest / filename

        if out_path.exists() and not overwrite:
            print(f"Skipping existing file: {out_path}")
            downloaded.append(out_path)
            continue

        print(f"Downloading {url}")
        try:
            with requests.get(url, stream=True, timeout=timeout) as response:
                response.raise_for_status()
                total = int(response.headers.get("content-length", 0))
                with (
                    open(out_path, "wb") as f,
                    tqdm(
                        total=total,
                        unit="B",
                        unit_scale=True,
                        desc=filename,
                        leave=False,
                    ) as pbar,
                ):
                    for chunk in response.iter_content(chunk_size=64 * 1024):
                        if not chunk:
                            continue
                        f.write(chunk)
                        pbar.update(len(chunk))
        except requests.HTTPError as exc:
            if out_path.exists():
                out_path.unlink(missing_ok=True)
            print(f"Failed to download {filename}: {exc}")
            continue

        # TODO: validate checksums against Binance provided .CHECKSUM files.
        downloaded.append(out_path)

    return downloaded
