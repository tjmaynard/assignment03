-- Part 6 (stretch challenge): Create BigQuery external tables for merged data
--
-- These tables point to the denormalized files where hourly observations
-- have been pre-joined with site location data during the prepare step.
-- Each observation row already includes latitude, longitude, state, etc.
--
-- Use hive partitioning with the airnow_date partition key.


-- Merged Hourly + Sites — CSV (hive-partitioned)
CREATE OR REPLACE EXTERNAL TABLE air_quality.hourly_with_sites_csv (
    valid_date          STRING,
    valid_time          STRING,
    aqsid               STRING,
    site_name           STRING,
    gmt_offset          STRING,
    parameter_name      STRING,
    reporting_units     STRING,
    value               STRING,
    data_source         STRING,
    station_id          STRING,
    full_aqsid          STRING,
    status              STRING,
    agency_id           STRING,
    agency_name         STRING,
    epa_region          STRING,
    latitude            FLOAT64,
    longitude           FLOAT64,
    elevation           FLOAT64,
    country_fips        STRING,
    cbsa_id             STRING,
    cbsa_name           STRING,
    state_aqs_code      STRING,
    state_abbreviation  STRING,
    county_aqs_code     STRING,
    county_name         STRING
)
WITH PARTITION COLUMNS (
    airnow_date DATE
)
OPTIONS (
    format = 'CSV',
    uris = ['gs://cc-s26-assignment-3-maynard-data/air_quality/hourly_with_sites/csv/*'],
    skip_leading_rows = 1,
    hive_partition_uri_prefix = 'gs://cc-s26-assignment-3-maynard-data/air_quality/hourly_with_sites/csv'
);


-- Merged Hourly + Sites — JSON-L (hive-partitioned)
CREATE OR REPLACE EXTERNAL TABLE air_quality.hourly_with_sites_jsonl (
    valid_date          STRING,
    valid_time          STRING,
    aqsid               STRING,
    site_name           STRING,
    gmt_offset          STRING,
    parameter_name      STRING,
    reporting_units     STRING,
    value               STRING,
    data_source         STRING,
    station_id          STRING,
    full_aqsid          STRING,
    status              STRING,
    agency_id           STRING,
    agency_name         STRING,
    epa_region          STRING,
    latitude            FLOAT64,
    longitude           FLOAT64,
    elevation           FLOAT64,
    country_fips        STRING,
    cbsa_id             STRING,
    cbsa_name           STRING,
    state_aqs_code      STRING,
    state_abbreviation  STRING,
    county_aqs_code     STRING,
    county_name         STRING
)
WITH PARTITION COLUMNS (
    airnow_date DATE
)
OPTIONS (
    format = 'NEWLINE_DELIMITED_JSON',
    uris = ['gs://cc-s26-assignment-3-maynard-data/air_quality/hourly_with_sites/jsonl/*'],
    hive_partition_uri_prefix = 'gs://cc-s26-assignment-3-maynard-data/air_quality/hourly_with_sites/jsonl'
);


-- Merged Hourly + Sites — GeoParquet (hive-partitioned)
-- Note: Schema is inferred from Parquet metadata; geometry column is
-- exposed as GEOGRAPHY via the view below.
CREATE OR REPLACE EXTERNAL TABLE air_quality.hourly_with_sites_geoparquet
WITH PARTITION COLUMNS (
    airnow_date DATE
)
OPTIONS (
    format = 'PARQUET',
    uris = ['gs://cc-s26-assignment-3-maynard-data/air_quality/hourly_with_sites/geoparquet/*'],
    hive_partition_uri_prefix = 'gs://cc-s26-assignment-3-maynard-data/air_quality/hourly_with_sites/geoparquet'
);

-- View that exposes the geometry column as a proper GEOGRAPHY type
CREATE OR REPLACE VIEW air_quality.hourly_with_sites_geo AS
SELECT
    * EXCEPT (geometry),
    geometry AS geog
FROM air_quality.hourly_with_sites_geoparquet;