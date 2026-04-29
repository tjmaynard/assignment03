"""
    Script to transform raw AirNow data files into BigQuery-compatible formats.

    This script reads the raw .dat files downloaded by 01_extract.py and converts
    them into CSV, JSON-L, and Parquet formats suitable for loading into
    BigQuery as external tables.

    Hourly observation data is converted to: CSV, JSON-L, Parquet
    Site location data is converted to: CSV, JSON-L, GeoParquet (with point geometry)

    Usage:
        python scripts/02_prepare.py
"""

import json
import pathlib

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point


DATA_DIR = pathlib.Path(__file__).parent.parent / 'data'

HOURLY_COLUMNS = [
    'valid_date',
    'valid_time',
    'aqsid',
    'site_name',
    'gmt_offset',
    'parameter_name',
    'reporting_units',
    'value',
    'data_source',
]

SITE_COLUMNS = [
    'station_id',
    'aqsid',
    'full_aqsid',
    'parameter',
    'monitor_type',
    'site_code',
    'site_name',
    'status',
    'agency_id',
    'agency_name',
    'epa_region',
    'latitude',
    'longitude',
    'elevation',
    'gmt_offset',
    'country_fips',
    'cbsa_id',
    'cbsa_name',
    'state_aqs_code',
    'state_abbreviation',
    'county_aqs_code',
    'county_name',
]

# Columns that uniquely identify a monitoring site (exclude per-parameter fields)
SITE_DEDUP_KEY = 'aqsid'
SITE_DROP_COLS = ['parameter', 'monitor_type']  # vary per site-parameter row


def _read_hourly_files(date_str) -> pd.DataFrame:
    """Read and concatenate all 24 HourlyData .dat files for a date."""
    raw_dir = DATA_DIR / 'raw' / date_str
    frames = []
    for hour in range(24):
        year, month, day = date_str.split('-')
        filename = f'HourlyData_{year}{month}{day}{hour:02d}.dat'
        filepath = raw_dir / filename
        if not filepath.exists():
            continue
        df = pd.read_csv(
            filepath,
            sep='|',
            header=None,
            names=HOURLY_COLUMNS,
            dtype=str,
            encoding='latin-1',   
        )
        frames.append(df)
    if not frames:
        raise FileNotFoundError(f'No hourly .dat files found for {date_str} in {raw_dir}')
    return pd.concat(frames, ignore_index=True)


def _read_site_locations() -> pd.DataFrame:
    """Read the most recent Monitoring_Site_Locations_V2.dat, deduplicated to one row per site."""
    # Pick the most recent date directory available under data/raw/
    raw_root = DATA_DIR / 'raw'
    date_dirs = sorted(raw_root.iterdir(), reverse=True)
    site_file = None
    for d in date_dirs:
        candidate = d / 'Monitoring_Site_Locations_V2.dat'
        if candidate.exists():
            site_file = candidate
            break
    if site_file is None:
        raise FileNotFoundError('No Monitoring_Site_Locations_V2.dat found under data/raw/')

    df = pd.read_csv(
        site_file,
        sep='|',
        header=None,
        names=SITE_COLUMNS,
        dtype=str,
        encoding='utf-8',
    )

    # Cast numeric fields
    for col in ('latitude', 'longitude', 'elevation', 'gmt_offset'):
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Deduplicate: one row per site (keep first occurrence of each aqsid,
    # dropping per-parameter columns that differ across rows for the same site)
    df = (
        df
        .drop(columns=SITE_DROP_COLS)
        .drop_duplicates(subset=[SITE_DEDUP_KEY])
        .reset_index(drop=True)
    )
    return df


# --- Hourly observation data ---

def prepare_hourly_csv(date_str):
    """Convert raw hourly .dat files for a date to a single CSV file.

    Reads all 24 HourlyData_*.dat files from data/raw/<date>/,
    combines them into a single dataset, assigns column names,
    and writes to data/prepared/hourly/<date>.csv.

    Args:
        date_str: Date string in 'YYYY-MM-DD' format.
    """
    out_dir = DATA_DIR / 'prepared' / 'hourly'
    out_dir.mkdir(parents=True, exist_ok=True)

    df = _read_hourly_files(date_str)
    df.to_csv(out_dir / f'{date_str}.csv', index=False)


def prepare_hourly_jsonl(date_str):
    out_dir = DATA_DIR / 'prepared' / 'hourly'
    out_dir.mkdir(parents=True, exist_ok=True)

    df = _read_hourly_files(date_str)
    df = df.apply(lambda col: col.str.strip().str.replace(r'[\r\n\x00]+', ' ', regex=True)
                  if col.dtype == object else col)

    # Replace all NaN/None with None so json.dumps writes null not NaN
    df = df.fillna(value='')

    out_path = out_dir / f'{date_str}.jsonl'
    with out_path.open('w', encoding='utf-8') as fh:
        for record in df.to_dict(orient='records'):
            fh.write(json.dumps(record, ensure_ascii=True) + '\n')


def prepare_hourly_parquet(date_str):
    """Convert raw hourly .dat files for a date to Parquet format.

    Reads all 24 HourlyData_*.dat files from data/raw/<date>/,
    combines them, and writes to data/prepared/hourly/<date>.parquet.

    Args:
        date_str: Date string in 'YYYY-MM-DD' format.
    """
    out_dir = DATA_DIR / 'prepared' / 'hourly'
    out_dir.mkdir(parents=True, exist_ok=True)

    df = _read_hourly_files(date_str)
    df.to_parquet(out_dir / f'{date_str}.parquet', index=False)


# --- Site location data ---

def prepare_site_locations_csv():
    """Convert monitoring site locations to CSV.

    Reads the Monitoring_Site_Locations_V2.dat file, deduplicates
    so there is one row per site (the raw file has one row per
    site-parameter combination), and writes to
    data/prepared/sites/site_locations.csv.

    Use the most recent date's file from data/raw/.
    """
    out_dir = DATA_DIR / 'prepared' / 'sites'
    out_dir.mkdir(parents=True, exist_ok=True)

    df = _read_site_locations()
    df.to_csv(out_dir / 'site_locations.csv', index=False)


def prepare_site_locations_jsonl():
    """Convert monitoring site locations to newline-delimited JSON.

    Reads the Monitoring_Site_Locations_V2.dat file, deduplicates
    so there is one row per site (the raw file has one row per
    site-parameter combination), and writes to
    data/prepared/sites/site_locations.jsonl.

    Use the most recent date's file from data/raw/.
    """
    out_dir = DATA_DIR / 'prepared' / 'sites'
    out_dir.mkdir(parents=True, exist_ok=True)

    df = _read_site_locations()
    out_path = out_dir / 'site_locations.jsonl'
    with out_path.open('w', encoding='utf-8') as fh:
        for record in df.where(pd.notna(df), other=None).to_dict(orient='records'):
            fh.write(json.dumps(record) + '\n')


def prepare_site_locations_geoparquet():
    """Convert monitoring site locations to GeoParquet with point geometry.

    Reads the Monitoring_Site_Locations_V2.dat file, deduplicates
    so there is one row per site (the raw file has one row per
    site-parameter combination), creates point geometries from
    latitude and longitude, and writes to
    data/prepared/sites/site_locations.geoparquet.

    Use the most recent date's file from data/raw/.
    """
    out_dir = DATA_DIR / 'prepared' / 'sites'
    out_dir.mkdir(parents=True, exist_ok=True)

    df = _read_site_locations()

    # Drop rows without valid coordinates before building geometries
    df = df.dropna(subset=['latitude', 'longitude'])

    geometry = [Point(lon, lat) for lon, lat in zip(df['longitude'], df['latitude'])]
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')
    gdf.to_parquet(out_dir / 'site_locations.geoparquet', index=False)


if __name__ == '__main__':
    import datetime

    # Prepare site locations (only need to do this once)
    print('Preparing site locations...')
    prepare_site_locations_csv()
    prepare_site_locations_jsonl()
    prepare_site_locations_geoparquet()

    # Prepare hourly data for each day in July 2024 (backfill)
    start_date = datetime.date(2024, 7, 1)
    end_date = datetime.date(2024, 7, 31)

    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.isoformat()
        print(f'Preparing hourly data for {date_str}...')
        prepare_hourly_csv(date_str)
        prepare_hourly_jsonl(date_str)
        prepare_hourly_parquet(date_str)
        current_date += datetime.timedelta(days=1)

    print('Done.')