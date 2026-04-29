-- Part 5: Create BigQuery external tables with hive partitioning
--
-- Create new external tables that use the hive-partitioned folder
-- structure from 05_upload_to_gcs. BigQuery can automatically detect
-- the partition key (airnow_date) from folder names like:
--     airnow_date=2024-07-01/data.csv
--
-- This allows BigQuery to prune partitions when filtering by date,
-- so queries like WHERE airnow_date = '2024-07-15' only scan one
-- day's file instead of all 31.


-- Hourly Observations — CSV (hive-partitioned)
CREATE OR REPLACE EXTERNAL TABLE air_quality.hourly_observations_csv_hive (
    valid_date       STRING,
    valid_time       STRING,
    aqsid            STRING,
    site_name        STRING,
    gmt_offset       STRING,
    parameter_name   STRING,
    reporting_units  STRING,
    value            STRING,
    data_source      STRING
)
WITH PARTITION COLUMNS (
    airnow_date DATE
)
OPTIONS (
    format = 'CSV',
    uris = ['gs://cc-s26-assignment-3-maynard-data/air_quality/hourly/csv/*'],
    skip_leading_rows = 1,
    hive_partition_uri_prefix = 'gs://cc-s26-assignment-3-maynard-data/air_quality/hourly/csv'
);


-- Hourly Observations — JSON-L (hive-partitioned)
CREATE OR REPLACE EXTERNAL TABLE air_quality.hourly_observations_jsonl_hive (
    valid_date       STRING,
    valid_time       STRING,
    aqsid            STRING,
    site_name        STRING,
    gmt_offset       STRING,
    parameter_name   STRING,
    reporting_units  STRING,
    value            STRING,
    data_source      STRING
)
WITH PARTITION COLUMNS (
    airnow_date DATE
)
OPTIONS (
    format = 'NEWLINE_DELIMITED_JSON',
    uris = ['gs://cc-s26-assignment-3-maynard-data/air_quality/hourly/jsonl/*'],
    hive_partition_uri_prefix = 'gs://cc-s26-assignment-3-maynard-data/air_quality/hourly/jsonl'
);


-- Hourly Observations — Parquet (hive-partitioned)
CREATE OR REPLACE EXTERNAL TABLE air_quality.hourly_observations_parquet_hive
WITH PARTITION COLUMNS (
    airnow_date DATE
)
OPTIONS (
    format = 'PARQUET',
    uris = ['gs://cc-s26-assignment-3-maynard-data/air_quality/hourly/parquet/*'],
    hive_partition_uri_prefix = 'gs://cc-s26-assignment-3-maynard-data/air_quality/hourly/parquet'
);