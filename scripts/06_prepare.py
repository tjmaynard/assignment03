"""
    Stretch challenge: Prepare merged hourly + site location data.

    This script joins the hourly observation data with site location data
    during the prepare step (denormalization), producing files where
    each observation row includes the site's latitude, longitude, and
    other geographic metadata.

    This is the alternative to the approach in Part 4, where hourly data
    and site locations were kept as separate tables and joined at query
    time in BigQuery.

    This is a backfill of the prepare step — you're re-processing the
    same raw data you already downloaded, but with a different
    transformation that produces a richer output.

    Usage:
        python scripts/06_prepare.py
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

# Site columns to drop before merging (per-parameter fields or
# duplicates that already exist in the hourly data)
SITE_DROP_COLS = ['parameter', 'monitor_type', 'site_code', 'site_name', 'gmt_offset']


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
    raw_root = DATA_DIR / 'raw'
    site_file = None
    for d in sorted(raw_root.iterdir(), reverse=True):
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
        encoding='latin-1',
    )

    for col in ('latitude', 'longitude', 'elevation'):
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df = (
        df
        .drop(columns=SITE_DROP_COLS)
        .drop_duplicates(subset=['aqsid'])
        .reset_index(drop=True)
    )
    return df


def _merge(date_str) -> pd.DataFrame:
    """Join hourly observations with site locations on aqsid."""
    hourly = _read_hourly_files(date_str)
    sites  = _read_site_locations()

    merged = hourly.merge(sites, on='aqsid', how='left')

    # Clean and fill NaN for string columns only — numeric columns
    # (latitude, longitude, elevation) keep NaN so pyarrow can handle them
    str_cols = merged.select_dtypes(include='str').columns
    merged[str_cols] = (
        merged[str_cols]
        .apply(lambda col: col.str.strip().str.replace(r'[\r\n\x00]+', ' ', regex=True))
    )
    merged[str_cols] = merged[str_cols].fillna('')

    return merged


def prepare_merged_csv(date_str):
    """Merge hourly observations with site locations and write as CSV.

    Reads the hourly .dat files for the given date and the site locations
    file, joins them on AQSID, and writes to
    data/prepared/hourly_with_sites/<date>.csv.

    Args:
        date_str: Date string in 'YYYY-MM-DD' format.
    """
    out_dir = DATA_DIR / 'prepared' / 'hourly_with_sites'
    out_dir.mkdir(parents=True, exist_ok=True)

    df = _merge(date_str)
    df.to_csv(out_dir / f'{date_str}.csv', index=False)


def prepare_merged_jsonl(date_str):
    """Merge hourly observations with site locations and write as JSON-L.

    Reads the hourly .dat files for the given date and the site locations
    file, joins them on AQSID, and writes to
    data/prepared/hourly_with_sites/<date>.jsonl.

    Args:
        date_str: Date string in 'YYYY-MM-DD' format.
    """
    out_dir = DATA_DIR / 'prepared' / 'hourly_with_sites'
    out_dir.mkdir(parents=True, exist_ok=True)

    df = _merge(date_str)
    out_path = out_dir / f'{date_str}.jsonl'
    with out_path.open('w', encoding='utf-8') as fh:
        for record in df.to_dict(orient='records'):
            fh.write(json.dumps(record, ensure_ascii=True) + '\n')


def prepare_merged_geoparquet(date_str):
    """Merge hourly observations with site locations and write as GeoParquet.

    Reads the hourly .dat files for the given date and the site locations
    file, joins them on AQSID, creates point geometries from the site's
    latitude and longitude, and writes to
    data/prepared/hourly_with_sites/<date>.geoparquet.

    Args:
        date_str: Date string in 'YYYY-MM-DD' format.
    """
    out_dir = DATA_DIR / 'prepared' / 'hourly_with_sites'
    out_dir.mkdir(parents=True, exist_ok=True)

    df = _merge(date_str)

    # Build point geometry; rows with no coordinates get a null geometry
    geometry = [
        Point(lon, lat) if pd.notna(lon) and pd.notna(lat) else None
        for lon, lat in zip(df['longitude'], df['latitude'])
    ]
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')
    gdf.to_parquet(out_dir / f'{date_str}.geoparquet', index=False)


if __name__ == '__main__':
    import datetime

    # Backfill: prepare merged data for each day in July 2024
    start_date = datetime.date(2024, 7, 1)
    end_date   = datetime.date(2024, 7, 31)

    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.isoformat()
        print(f'Preparing merged data for {date_str}...')
        prepare_merged_csv(date_str)
        prepare_merged_jsonl(date_str)
        prepare_merged_geoparquet(date_str)
        current_date += datetime.timedelta(days=1)

    print('Done.')
    