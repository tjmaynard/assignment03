"""
    Stretch challenge: Upload merged hourly + site location data to GCS.

    This script uploads the denormalized (merged) files produced by
    06_prepare.py to GCS with a hive-partitioned folder structure.

    Prerequisites:
        - Run `gcloud auth application-default login` to authenticate.
        - Part 6 prepare script (06_prepare.py) should be complete.

    Usage:
        python scripts/06_upload_to_gcs.py
"""

import pathlib

from google.cloud import storage


DATA_DIR = pathlib.Path(__file__).parent.parent / 'data'

BUCKET_NAME = 'cc-s26-assignment-3-maynard-data'

MERGED_DIR = DATA_DIR / 'prepared' / 'hourly_with_sites'

FORMAT_SUBFOLDERS = {
    '.csv':         'csv',
    '.jsonl':       'jsonl',
    '.geoparquet':  'geoparquet',
}

FORMAT_FILENAMES = {
    '.csv':         'data.csv',
    '.jsonl':       'data.jsonl',
    '.geoparquet':  'data.geoparquet',
}


def upload_merged_data():
    """Upload merged hourly data to GCS with hive-partitioned folder structure.

    Expected GCS structure:
        gs://<bucket>/air_quality/hourly_with_sites/csv/airnow_date=2024-07-01/data.csv
        gs://<bucket>/air_quality/hourly_with_sites/jsonl/airnow_date=2024-07-01/data.jsonl
        gs://<bucket>/air_quality/hourly_with_sites/geoparquet/airnow_date=2024-07-01/data.geoparquet
    """
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)

    files = [f for f in MERGED_DIR.iterdir() if f.is_file()]

    if not files:
        print('No merged files found in data/prepared/hourly_with_sites/ — nothing to upload.')
        return

    for local_path in sorted(files):
        ext      = local_path.suffix    
        date_str = local_path.stem      

        if ext not in FORMAT_SUBFOLDERS:
            print(f'  Skipping unknown format: {local_path.name}')
            continue

        format_folder = FORMAT_SUBFOLDERS[ext]
        filename      = FORMAT_FILENAMES[ext]

        # gs://<bucket>/air_quality/hourly_with_sites/csv/airnow_date=2024-07-01/data.csv
        blob_name = f'air_quality/hourly_with_sites/{format_folder}/airnow_date={date_str}/{filename}'

        blob = bucket.blob(blob_name)
        blob.upload_from_filename(local_path)
        print(f'  Uploaded: {local_path.name} → gs://{BUCKET_NAME}/{blob_name}')


if __name__ == '__main__':
    upload_merged_data()
    print('Done.')
