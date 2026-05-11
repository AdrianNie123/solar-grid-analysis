"""Data ingestion utilities for CEC DGStats, CAISO, DeepSolar, and crosswalk files."""

import logging
from pathlib import Path
from typing import Optional
import pandas as pd

log = logging.getLogger(__name__)

RAW_DIR = Path(__file__).parent.parent / "data" / "raw"

# ── DGStats ──────────────────────────────────────────────────────────────────

DGSTATS_COLS = [
    "application_id",
    "app_approved_date",
    "sector",
    "program_type",
    "system_size_dc",
    "zip_code",
    "utility",
    "cost",
    "battery_storage",
]

DGSTATS_FILTERS = {
    "sector": ["Residential"],
    "program_type": ["NEM", "NBT"],
}


def load_dgstats(csv_path: Path) -> pd.DataFrame:
    """Read raw DGStats CSV and apply sector/program_type filters."""
    df = pd.read_csv(csv_path, usecols=lambda c: c in DGSTATS_COLS, low_memory=False)
    df = df[df["sector"].isin(DGSTATS_FILTERS["sector"])]
    df = df[df["program_type"].isin(DGSTATS_FILTERS["program_type"])]
    df["app_approved_date"] = pd.to_datetime(df["app_approved_date"], errors="coerce")
    df = df[
        (df["app_approved_date"] >= "2015-01-01")
        & (df["app_approved_date"] <= "2023-12-31")
    ]
    log.info("DGStats loaded: %d rows after filters", len(df))
    return df


# ── CAISO via gridstatus ──────────────────────────────────────────────────────


def fetch_caiso_month(year: int, month: int, cache_dir: Optional[Path] = None) -> pd.DataFrame:
    """
    Fetch one month of CAISO hourly data via gridstatus.
    Caches the result as a parquet shard if cache_dir is provided.
    """
    import gridstatus  # noqa: PLC0415

    shard_path = None
    if cache_dir is not None:
        shard_path = cache_dir / f"caiso_{year}_{month:02d}.parquet"
        if shard_path.exists():
            return pd.read_parquet(shard_path)

    iso = gridstatus.CAISO()
    start = f"{year}-{month:02d}-01"
    # last day of month
    end = pd.Timestamp(start) + pd.offsets.MonthEnd(1)
    df = iso.get_fuel_mix(start=start, end=end.strftime("%Y-%m-%d"), verbose=False)

    if shard_path is not None:
        shard_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(shard_path)

    return df


def fetch_caiso_all(start_year: int = 2015, end_year: int = 2023) -> pd.DataFrame:
    """Fetch all CAISO monthly shards and concatenate."""
    cache_dir = RAW_DIR / "caiso_shards"
    shards = []
    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            log.info("Fetching CAISO %d-%02d", year, month)
            shard = fetch_caiso_month(year, month, cache_dir=cache_dir)
            shards.append(shard)
    return pd.concat(shards, ignore_index=True)


# ── DeepSolar ────────────────────────────────────────────────────────────────


def load_deepsolar(csv_path: Path) -> pd.DataFrame:
    """Read DeepSolar CA tract CSV and filter to California (FIPS 06)."""
    df = pd.read_csv(csv_path, low_memory=False)
    # California state FIPS prefix
    df = df[df["fips"].astype(str).str.startswith("6")]
    log.info("DeepSolar loaded: %d CA tracts", len(df))
    return df


# ── ZIP–Tract crosswalk ───────────────────────────────────────────────────────


def load_zip_tract_crosswalk(path: Path) -> pd.DataFrame:
    """Load HUD or IPUMS ZIP-to-tract relationship file."""
    df = pd.read_csv(path, dtype={"zip": str, "tract": str})
    # Normalize ZIP to 5-char string with leading zeros
    df["zip"] = df["zip"].str.zfill(5)
    # Filter to CA tracts (FIPS prefix 06)
    df = df[df["tract"].str.startswith("06")]
    log.info("Crosswalk loaded: %d ZIP-tract pairs", len(df))
    return df
