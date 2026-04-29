"""
    Script to extract AirNow data files for a range of dates.

    This script downloads hourly air quality observation data and monitoring
    site location data from the EPA's AirNow program. Files are saved into
    a date-organized folder structure under data/raw/.

    AirNow files are hosted at:
        https://files.airnowtech.org/?prefix=airnow/

    Usage:
        python scripts/01_extract.py
"""

import pathlib
import urllib.request


DATA_DIR = pathlib.Path(__file__).parent.parent / 'data'

BASE_URL = 'https://files.airnowtech.org/airnow'


def download_data_for_date(date_str):
    """Download AirNow data files for a single date.

    Downloads all 24 HourlyData files (hours 00-23) and the
    Monitoring_Site_Locations_V2.dat file for the specified date,
    saving them into data/raw/YYYY-MM-DD/.

    Args:
        date_str: Date string in 'YYYY-MM-DD' format. For example, '2024-07-01'.
    """
    # Parse date components from 'YYYY-MM-DD'
    year, month, day = date_str.split('-')
    date_compact = f'{year}{month}{day}'           
    date_folder  = f'{year}/{date_compact}'         

    # Output directory: data/raw/YYYY-MM-DD/
    out_dir = DATA_DIR / 'raw' / date_str
    out_dir.mkdir(parents=True, exist_ok=True)

    # Build list of files to download: 24 hourly files + site locations
    files_to_download = [
        f'HourlyData_{date_compact}{hour:02d}.dat'
        for hour in range(24)
    ] + ['Monitoring_Site_Locations_V2.dat']

    for filename in files_to_download:
        url = f'{BASE_URL}/{date_folder}/{filename}'
        dest = out_dir / filename
        if dest.exists():
            print(f'  Already exists, skipping: {filename}')
            continue
        try:
            urllib.request.urlretrieve(url, dest)
            print(f'  Downloaded: {filename}')
        except urllib.error.HTTPError as e:
            print(f'  HTTP {e.code} for {filename} — skipping')
        except urllib.error.URLError as e:
            print(f'  Network error for {filename}: {e.reason} — skipping')


if __name__ == '__main__':
    import datetime

    # Download data for July 2024
    start_date = datetime.date(2024, 7, 1)
    end_date   = datetime.date(2024, 7, 31)

    current_date = start_date
    while current_date <= end_date:
        print(f'Downloading data for {current_date}...')
        download_data_for_date(current_date.isoformat())
        current_date += datetime.timedelta(days=1)

    print('Done.')
    