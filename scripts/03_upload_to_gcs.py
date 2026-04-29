"""
    Script to upload prepared data files to Google Cloud Storage (GCS).

    This script uploads the transformed files from data/prepared/ to a
    GCS bucket, preserving the folder structure so that BigQuery can
    use wildcard URIs to create external tables across multiple files.

    Prerequisites:
        - Run `gcloud auth application-default login` to authenticate.
        - Create a GCS bucket (manually or in this script).

    Usage:
        python scripts/03_upload_to_gcs.py
"""

import pathlib

from google.cloud import storage


DATA_DIR = pathlib.Path(__file__).parent.parent / 'data'

# TODO: Update this to your bucket name
BUCKET_NAME = 'cc-s26-assignment-3-maynard-data'

GCS_PREFIX = 'air_quality'
PREPARED_DIR = DATA_DIR / 'prepared'


def upload_prepared_data():
    """Upload all prepared data files to GCS.

    Uploads the contents of data/prepared/ to the GCS bucket,
    preserving the folder structure under a prefix of 'air_quality/'.

    Expected GCS structure:
        gs://cc-s26-assignment-3-maynard-data/air_quality/hourly/2024-07-01.csv
        gs://cc-s26-assignment-3-maynard-data/air_quality/hourly/2024-07-01.jsonl
        gs://cc-s26-assignment-3-maynard-data/air_quality/hourly/2024-07-01.parquet
        ...
        gs://cc-s26-assignment-3-maynard-data/air_quality/sites/site_locations.csv
        gs://cc-s26-assignment-3-maynard-data/air_quality/sites/site_locations.jsonl
        gs://cc-s26-assignment-3-maynard-data/air_quality/sites/site_locations.geoparquet
    """
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)

    files = list(PREPARED_DIR.rglob('*'))
    uploadable = [f for f in files if f.is_file()]

    if not uploadable:
        print('No files found in data/prepared/ — nothing to upload.')
        return

    for local_path in uploadable:
        # Preserve folder structure
        relative = local_path.relative_to(PREPARED_DIR)
        blob_name = f'{GCS_PREFIX}/{relative.as_posix()}'

        blob = bucket.blob(blob_name)
        blob.upload_from_filename(local_path)
        print(f'  Uploaded: {local_path} → gs://{BUCKET_NAME}/{blob_name}')


if __name__ == '__main__':
    upload_prepared_data()
    print('Done.')
