"""
    Script to re-upload prepared data to GCS using hive-partitioned folder structure.

    This script takes the same prepared files from Part 2 and uploads them
    to GCS with a hive-partitioned directory layout. Instead of flat files like:
        air_quality/hourly/2024-07-01.csv

    Files are organized as:
        air_quality/hourly/csv/airnow_date=2024-07-01/data.csv

    This enables BigQuery to automatically detect the partition key
    (airnow_date) and use it for query pruning, so queries filtering
    by date only scan the relevant files.

    This is a backfill of the upload step — you don't need to re-download
    or re-transform anything. You're just re-uploading the same files
    with a different folder structure.

    Prerequisites:
        - Run `gcloud auth application-default login` to authenticate.
        - Parts 1-3 should be complete (data already prepared and uploaded once).

    Usage:
        python scripts/05_upload_to_gcs.py
"""

import pathlib

from google.cloud import storage


DATA_DIR = pathlib.Path(__file__).parent.parent / 'data'

BUCKET_NAME = 'cc-s26-assignment-3-maynard-data'

HOURLY_DIR = DATA_DIR / 'prepared' / 'hourly'

# Map file extension to the format subfolder name
FORMAT_SUBFOLDERS = {
    '.csv':     'csv',
    '.jsonl':   'jsonl',
    '.parquet': 'parquet',
}

# Map file extension to the filename BigQuery will see inside the partition folder
FORMAT_FILENAMES = {
    '.csv':     'data.csv',
    '.jsonl':   'data.jsonl',
    '.parquet': 'data.parquet',
}


def upload_with_hive_partitioning():
    """Upload prepared hourly data to GCS with hive-partitioned folder structure.

    For each date's prepared files, upload them to GCS with the following
    folder structure:
        gs://<bucket>/air_quality/hourly/csv/airnow_date=2024-07-01/data.csv
        gs://<bucket>/air_quality/hourly/jsonl/airnow_date=2024-07-01/data.jsonl
        gs://<bucket>/air_quality/hourly/parquet/airnow_date=2024-07-01/data.parquet

    The site locations files don't need hive partitioning (they're not
    date-partitioned), so you can re-upload them as-is or skip them.
    """
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)

    # Collect all hourly files (e.g. 2024-07-01.csv, 2024-07-01.jsonl, ...)
    hourly_files = [f for f in HOURLY_DIR.iterdir() if f.is_file()]

    if not hourly_files:
        print('No hourly files found in data/prepared/hourly/ — nothing to upload.')
        return

    for local_path in sorted(hourly_files):
        ext = local_path.suffix               
        date_str = local_path.stem            

        if ext not in FORMAT_SUBFOLDERS:
            print(f'  Skipping unknown format: {local_path.name}')
            continue

        format_folder = FORMAT_SUBFOLDERS[ext]       
        filename      = FORMAT_FILENAMES[ext]        

        # gs://<bucket>/air_quality/hourly/csv/airnow_date=2024-07-01/data.csv
        blob_name = f'air_quality/hourly/{format_folder}/airnow_date={date_str}/{filename}'

        blob = bucket.blob(blob_name)
        blob.upload_from_filename(local_path)
        print(f'  Uploaded: {local_path.name} → gs://{BUCKET_NAME}/{blob_name}')


if __name__ == '__main__':
    upload_with_hive_partitioning()
    print('Done.')