"""Data ingestion utilities for IOU interconnection apps, CAISO, DeepSolar, and crosswalk files."""

import logging
from pathlib import Path
from typing import Optional
import pandas as pd

log = logging.getLogger(__name__)

RAW_DIR = Path(__file__).parent.parent / "data" / "raw"

# ── DGStats ───────────────────────────────────────────────────────────────────

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


# ── CAISO — load (via gridstatus) + CEC monthly generation actuals ────────────

# CEC Excel files vary in layout year-to-year; this map covers the most common
# column name variants. Keys are candidate CEC column names, values are our
# internal names.  Extend if a new year's file uses different headers.
_CEC_COL_CANDIDATES = {
    "solar": ["Solar", "Solar PV", "Solar Photovoltaic", "Small Solar PV",
              "Utility-Scale Solar PV", "Distributed Solar PV", "SOLAR"],
    "wind": ["Wind", "Wind Total", "Wind Turbine", "WIND"],
    "total": ["Total", "Net Generation (GWh)", "Total Net Generation",
              "Total Generation", "Total In-State Generation"],
    "month": ["Month", "MONTH", "month", "Period", "PERIOD"],
    "year": ["Year", "YEAR", "year"],
}


def _parse_cec_wide_annual(df: pd.DataFrame, year_cols: list, fname: str, sheet: str):
    """Handle CEC wide-format files: Region | Fuel Type | 2009 | … | 2024.

    Returns a long DataFrame with columns year, month (1–12), solar_gwh,
    wind_gwh, total_generation_gwh — one row per (year, month).  Annual GWh
    values are divided evenly across 12 months (the only option without
    monthly breakdowns in this CEC publication).
    """
    region_col = next((c for c in df.columns if "region" in c.lower()), None)
    fuel_col = next((c for c in df.columns if "fuel" in c.lower()), None)
    if region_col is None or fuel_col is None:
        log.debug("Wide-format skip '%s'/%s — missing Region/Fuel columns", fname, sheet)
        return None

    ca_mask = df[region_col].astype(str).str.strip().str.lower() == "california"
    ca = df[ca_mask].copy()
    if ca.empty:
        log.debug("Wide-format skip '%s'/%s — no California rows", fname, sheet)
        return None

    ca[fuel_col] = ca[fuel_col].astype(str).str.strip().str.lower()

    # Also capture the California Total row (Region is NaN, Fuel Type = "california total")
    total_mask = df[fuel_col].astype(str).str.strip().str.lower() == "california total"
    ca_total = df[total_mask].copy()

    solar_row = ca[ca[fuel_col].str.contains("solar", na=False)]
    wind_row = ca[ca[fuel_col].str.contains("wind", na=False)]
    if solar_row.empty or wind_row.empty:
        log.debug("Wide-format skip '%s'/%s — no Solar/Wind rows for California", fname, sheet)
        return None

    rows = []
    for yc in year_cols:
        yr = int(float(str(yc)))
        sol_val = pd.to_numeric(solar_row[yc].values[0], errors="coerce")
        wnd_val = pd.to_numeric(wind_row[yc].values[0], errors="coerce")
        tot_val = float("nan")
        if not ca_total.empty:
            tot_val = pd.to_numeric(ca_total[yc].values[0], errors="coerce")

        if pd.isna(sol_val) or pd.isna(wnd_val):
            continue
        for mo in range(1, 13):
            rows.append({
                "year": yr,
                "month": mo,
                "solar_gwh": sol_val / 12.0,
                "wind_gwh": wnd_val / 12.0,
                "total_generation_gwh": tot_val / 12.0 if not pd.isna(tot_val) else float("nan"),
            })

    if not rows:
        return None

    result = pd.DataFrame(rows)
    log.info(
        "Wide-format CEC '%s'/%s: %d years → %d monthly rows (annual÷12)",
        fname, sheet, len(year_cols), len(result),
    )
    return result


def load_cec_monthly_generation(data_dir: Path) -> pd.DataFrame:
    """Read CEC monthly electricity generation Excel files from data_dir/raw/cec/.

    The CEC Almanac publishes 'Monthly Electricity Generation by Energy Source'
    (https://www.energy.ca.gov/data-reports/energy-almanac).  Download the Excel
    file(s) covering 2015–2023 and place them in data_dir/raw/cec/.

    Expected output columns:
      year (int), month (int), solar_gwh (float), wind_gwh (float),
      total_generation_gwh (float)

    The loader tries common CEC column name variants automatically.  If your file
    uses different headers, update _CEC_COL_CANDIDATES at the top of this module.
    """
    cec_dir = Path(data_dir) / "raw" / "cec"
    excel_files = sorted(cec_dir.glob("*.xlsx")) + sorted(cec_dir.glob("*.xls"))
    if not excel_files:
        raise FileNotFoundError(
            f"No Excel files found in {cec_dir}. Download CEC generation data "
            f"from https://www.energy.ca.gov/data-reports/energy-almanac and "
            f"place the file(s) there."
        )

    chunks = []
    for f in excel_files:
        log.info("Reading CEC file %s", f.name)
        # Try each sheet; skip sheets that don't parse cleanly
        xl = pd.ExcelFile(f)
        for sheet in xl.sheet_names:
            try:
                raw = xl.parse(sheet, header=0)
            except Exception:
                continue
            if raw.empty or len(raw.columns) < 3:
                continue
            chunks.append((f.name, sheet, raw))

    if not chunks:
        raise ValueError(f"Could not parse any sheets from Excel files in {cec_dir}")

    records = []
    for fname, sheet, df in chunks:
        df.columns = [str(c).strip() for c in df.columns]

        # Some CEC files have a blank first Excel row, so pandas assigns "Unnamed: N"
        # headers and the real header (Region | Fuel Type | 2009 | …) sits in row 0.
        # Detect this pattern and re-promote that row to the header.
        first_row = df.iloc[0].astype(str).str.strip().tolist()
        if any(v in first_row for v in ("Region", "Fuel Type")):
            df.columns = first_row
            df = df.iloc[1:].reset_index(drop=True)

        # Detect wide annual format: CEC files with year integers (e.g. 2009, 2010…) as
        # column headers and fuel-type rows (Region | Fuel Type | 2009 | … | 2024).
        # Year columns can appear as '2009', '2009.0', or integer 2009.
        def _is_year_col(c):
            try:
                yr = int(float(str(c)))
                return 2000 <= yr <= 2040 and str(float(str(c))) in (str(c), str(c) + '.0', str(yr))
            except (ValueError, TypeError):
                return False
        year_cols = [c for c in df.columns if _is_year_col(c)]
        if year_cols and any(c in ("Region", "Fuel Type") for c in df.columns):
            sub = _parse_cec_wide_annual(df, year_cols, fname, sheet)
            if sub is not None:
                records.append(sub)
            continue

        # --- Long / monthly format (original logic) ---
        yr_col = next((c for c in df.columns for v in _CEC_COL_CANDIDATES["year"] if v.lower() == c.lower()), None)
        mo_col = next((c for c in df.columns for v in _CEC_COL_CANDIDATES["month"] if v.lower() == c.lower()), None)
        sol_col = next((c for c in df.columns for v in _CEC_COL_CANDIDATES["solar"] if v.lower() in c.lower()), None)
        wnd_col = next((c for c in df.columns for v in _CEC_COL_CANDIDATES["wind"] if v.lower() in c.lower()), None)
        tot_col = next((c for c in df.columns for v in _CEC_COL_CANDIDATES["total"] if v.lower() in c.lower()), None)

        if sol_col is None or wnd_col is None:
            log.debug("Skipping sheet '%s' in %s — no solar/wind columns found", sheet, fname)
            continue
        if mo_col is None and yr_col is None:
            log.debug("Skipping sheet '%s' in %s — no year/month columns found", sheet, fname)
            continue

        keep = {c: c for c in [yr_col, mo_col, sol_col, wnd_col, tot_col] if c is not None}
        sub = df[list(keep.keys())].copy()
        sub = sub.rename(columns={
            yr_col: "year", mo_col: "month",
            sol_col: "solar_gwh", wnd_col: "wind_gwh",
        })
        if tot_col:
            sub = sub.rename(columns={tot_col: "total_generation_gwh"})
        else:
            sub["total_generation_gwh"] = float("nan")

        for col in ["year", "month", "solar_gwh", "wind_gwh", "total_generation_gwh"]:
            sub[col] = pd.to_numeric(sub[col], errors="coerce")

        sub = sub.dropna(subset=["year", "month", "solar_gwh", "wind_gwh"])
        sub["year"] = sub["year"].astype(int)
        sub["month"] = sub["month"].astype(int)
        records.append(sub)

    if not records:
        raise ValueError(
            f"Could not locate solar/wind/month columns in any sheet of CEC files in {cec_dir}. "
            f"Check _CEC_COL_CANDIDATES in data_ingestion.py against your file's actual headers."
        )

    result = pd.concat(records, ignore_index=True)
    result = result.drop_duplicates(subset=["year", "month"]).sort_values(["year", "month"]).reset_index(drop=True)
    log.info("CEC monthly generation loaded: %d rows (expected 108 for 2015–2023)", len(result))
    return result


def fetch_caiso_month(year: int, month: int, cache_dir: Optional[Path] = None, _iso=None) -> pd.DataFrame:
    """Fetch one month of CAISO hourly load via gridstatus get_load_hourly (CA ISO-TAC)."""
    shard_path = None
    if cache_dir is not None:
        shard_path = cache_dir / f"caiso_load_{year}_{month:02d}.parquet"
        if shard_path.exists():
            return pd.read_parquet(shard_path)

    if _iso is None:
        import gridstatus  # noqa: PLC0415
        _iso = gridstatus.CAISO()

    start = pd.Timestamp(f"{year}-{month:02d}-01")
    end = (start + pd.offsets.MonthEnd(1) + pd.Timedelta("1d")).strftime("%Y-%m-%d")

    raw = _iso.get_load_hourly(start.strftime("%Y-%m-%d"), end=end, verbose=False)
    raw = raw[raw["TAC Area Name"] == "CA ISO-TAC"].copy()
    raw["interval_start_utc"] = pd.to_datetime(raw["Interval Start"], utc=True)
    df = raw[["interval_start_utc", "Load"]].rename(columns={"Load": "demand_mw"})

    if shard_path is not None:
        shard_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(shard_path, index=False)

    return df


def fetch_caiso_all(start_year: int = 2015, end_year: int = 2023,
                    data_dir: Optional[Path] = None) -> pd.DataFrame:
    """Fetch CAISO monthly load (gridstatus) and merge with CEC monthly generation.

    Phase 1 (~2 min): 108 monthly gridstatus load calls → aggregate to monthly GWh.
    Phase 2 (seconds): read CEC monthly generation Excel files.
    Phase 3 (seconds): left-join on (year, month), compute net_load_gwh,
                       net_load_ratio, monthly_ramp_gwh.
    Phase 4 (seconds): QC assertions.

    Returns monthly DataFrame with columns:
      year, month, demand_gwh, solar_gwh, wind_gwh, total_generation_gwh,
      net_load_gwh, net_load_ratio, monthly_ramp_gwh
    """
    import gridstatus  # noqa: PLC0415

    if data_dir is None:
        data_dir = RAW_DIR.parent  # project data/ directory

    cache_dir = RAW_DIR / "caiso_shards"
    merged_path = cache_dir / "caiso_monthly_merged.parquet"
    if merged_path.exists():
        log.info("Loading cached caiso_monthly_merged.parquet")
        return pd.read_parquet(merged_path)

    iso = gridstatus.CAISO()

    # ── Phase 1: monthly load ────────────────────────────────────────────────
    n_months = (end_year - start_year + 1) * 12
    log.info("CAISO Phase 1: fetching %d monthly load shards via gridstatus", n_months)
    load_shards = []
    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            log.info("  load %d-%02d", year, month)
            shard = fetch_caiso_month(year, month, cache_dir=cache_dir, _iso=iso)
            load_shards.append(shard)
    load_hourly = pd.concat(load_shards, ignore_index=True)

    # Aggregate hourly MW → monthly GWh
    load_hourly["interval_start_utc"] = pd.to_datetime(load_hourly["interval_start_utc"], utc=True)
    load_hourly["year"] = load_hourly["interval_start_utc"].dt.year
    load_hourly["month"] = load_hourly["interval_start_utc"].dt.month
    load_monthly = (
        load_hourly.groupby(["year", "month"])["demand_mw"]
        .sum()
        .reset_index()
        # sum of hourly MW values equals MWh; divide by 1000 for GWh
        .rename(columns={"demand_mw": "demand_gwh"})
    )
    load_monthly["demand_gwh"] = load_monthly["demand_gwh"] / 1000.0
    load_monthly = load_monthly[
        (load_monthly["year"] >= start_year) & (load_monthly["year"] <= end_year)
    ]
    log.info("Phase 1 done: %d monthly demand rows", len(load_monthly))

    # ── Phase 2: CEC monthly generation ────────────────────────────────────
    log.info("CAISO Phase 2: loading CEC monthly generation from data/raw/cec/")
    cec = load_cec_monthly_generation(data_dir)
    cec_path = cache_dir / "cec_monthly_raw.parquet"
    cache_dir.mkdir(parents=True, exist_ok=True)
    cec.to_parquet(cec_path, index=False)
    log.info("Phase 2 done: %d CEC rows", len(cec))

    # ── Phase 3: merge + net load ────────────────────────────────────────────
    log.info("CAISO Phase 3: merging and computing net load")
    merged = load_monthly.merge(cec, on=["year", "month"], how="left")
    for col in ["solar_gwh", "wind_gwh"]:
        merged[col] = pd.to_numeric(merged[col], errors="coerce").fillna(0.0)
    merged["net_load_gwh"] = merged["demand_gwh"] - merged["solar_gwh"] - merged["wind_gwh"]
    merged["net_load_ratio"] = merged["net_load_gwh"] / merged["demand_gwh"].replace(0, float("nan"))
    merged = merged.sort_values(["year", "month"]).reset_index(drop=True)
    merged["monthly_ramp_gwh"] = merged["net_load_gwh"].diff().abs()

    # ── Phase 4: QC ─────────────────────────────────────────────────────────
    n_years = end_year - start_year + 1
    expected_rows = n_years * 12
    log.info(
        "QC: %d rows (expected %d); nulls: demand=%d solar=%d wind=%d; "
        "net_load_ratio range [%.3f, %.3f]",
        len(merged), expected_rows,
        merged["demand_gwh"].isna().sum(),
        merged["solar_gwh"].isna().sum(),
        merged["wind_gwh"].isna().sum(),
        merged["net_load_ratio"].min(),
        merged["net_load_ratio"].max(),
    )

    merged.to_parquet(merged_path, index=False)
    log.info("Saved caiso_monthly_merged.parquet")
    return merged


# ── DeepSolar ────────────────────────────────────────────────────────────────


def load_deepsolar(csv_path: Path) -> pd.DataFrame:
    """Read DeepSolar CA tract CSV and filter to California (FIPS 06)."""
    df = pd.read_csv(csv_path, low_memory=False, encoding="latin-1")
    # California state FIPS prefix
    df = df[df["fips"].astype(str).str.startswith("6")]
    log.info("DeepSolar loaded: %d CA tracts", len(df))
    return df


# ── ZIP–Tract crosswalk ───────────────────────────────────────────────────────


def load_zip_tract_crosswalk(path: Path) -> pd.DataFrame:
    """Load HUD ZIP-to-tract relationship file (CSV or XLSX)."""
    path = Path(path)
    if path.suffix in (".xlsx", ".xls"):
        df = pd.read_excel(path, dtype={"ZIP": str, "TRACT": str})
        # HUD XLSX uses uppercase column names
        df = df.rename(columns={"ZIP": "zip", "TRACT": "tract", "RES_RATIO": "res_ratio"})
    else:
        df = pd.read_csv(path, dtype={"zip": str, "tract": str})

    df["zip"] = df["zip"].astype(str).str.zfill(5)
    df["tract"] = df["tract"].astype(str).str.zfill(11)
    # Filter to CA tracts (state FIPS 06)
    df = df[df["tract"].str.startswith("06")]
    log.info("Crosswalk loaded: %d CA ZIP-tract pairs", len(df))
    return df


# ── IOU Interconnection Applications (replaces CEC DGStats) ──────────────────

_INTERCONNECT_COL_MAP = {
    "Application Id": "application_id",
    "App Approved Date": "app_approved_date",
    "Customer Sector": "sector",
    "NEM Tariff": "program_type",
    "System Size DC": "system_size_dc",
    "Service Zip": "zip_code",
    "Utility": "utility",
    "Total System Cost": "cost",
    "Storage Capacity (kWh)": "battery_storage",
    "Technology Type": "_tech_type",
    "Application Status": "_app_status",
    "Interconnection Program": "_program",
}

_UTILITY_MAP = {"PGE": "PG&E", "SCE": "SCE", "SDGE": "SDG&E"}

_NEM_TARIFF_MAP = {"1.0": "NEM", "2.0": "NEM", "3.0": "NBT", "NBT": "NBT"}


def load_interconnection_apps(data_dir: Path) -> pd.DataFrame:
    """Read all IOU interconnection CSVs and produce the same schema as load_dgstats().

    Filters to residential NEM/NBT photovoltaic installs (Interconnected status)
    with a valid CA Service Zip, approved 2015–2023.
    """
    csv_paths = sorted(Path(data_dir).glob("*.csv"))
    if not csv_paths:
        raise FileNotFoundError(f"No CSV files found in {data_dir}")

    chunks = []
    for p in csv_paths:
        log.info("Reading %s", p.name)
        df = pd.read_csv(
            p,
            usecols=lambda c: c in _INTERCONNECT_COL_MAP,
            dtype=str,
            low_memory=False,
            encoding="latin-1",
        )
        df = df.rename(columns=_INTERCONNECT_COL_MAP)
        chunks.append(df)

    df = pd.concat(chunks, ignore_index=True)

    # Basic filters
    df = df[df["sector"].str.strip() == "Residential"]
    df = df[df["_app_status"].str.strip() == "Interconnected"]
    df = df[df["_tech_type"].str.contains("Photovoltaic", case=False, na=False)]
    df = df[df["zip_code"].str.strip().ne("")]

    # Standardize utility names
    df["utility"] = df["utility"].str.strip().map(_UTILITY_MAP).fillna(df["utility"].str.strip())

    # Date parsing and range filter
    df["app_approved_date"] = pd.to_datetime(df["app_approved_date"], errors="coerce")
    df = df[df["app_approved_date"].notna()]
    df = df[
        (df["app_approved_date"] >= "2015-01-01")
        & (df["app_approved_date"] <= "2023-12-31")
    ]

    # program_type: map NEM Tariff values; post-NBT-date rows without a tariff get 'NBT'
    df["program_type"] = (
        df["program_type"].str.strip().map(_NEM_TARIFF_MAP).fillna("NEM")
    )

    # Numeric columns
    df["system_size_dc"] = pd.to_numeric(df["system_size_dc"], errors="coerce")
    df["cost"] = pd.to_numeric(df["cost"], errors="coerce")
    df["battery_storage"] = pd.to_numeric(df["battery_storage"], errors="coerce").fillna(0.0)

    # Drop helper columns and deduplicate
    df = df.drop(columns=["_tech_type", "_app_status", "_program"], errors="ignore")
    df = df.drop_duplicates(subset=["application_id"])

    log.info("Interconnection apps loaded: %d residential NEM rows", len(df))
    return df


# ── Utility territory shapefile ───────────────────────────────────────────────

_CA_IOU_ACRONYMS = {"PG&E", "SCE", "SDG&E"}


def load_utility_territories(shp_path: Path):
    """Read the HIFLD ElectricLoadServingEntities shapefile and return CA IOUs in EPSG:4326."""
    import geopandas as gpd  # noqa: PLC0415

    gdf = gpd.read_file(shp_path)
    gdf = gdf[gdf["Acronym"].isin(_CA_IOU_ACRONYMS)].copy()
    # Alias for notebook 04 which expects a 'utility_name' column
    gdf["utility_name"] = gdf["Utility"]
    gdf = gdf.to_crs(epsg=4326)
    log.info("Utility territories loaded: %d features (CA IOUs)", len(gdf))
    return gdf
