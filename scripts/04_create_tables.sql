-- Part 4: Create BigQuery external tables
--
-- Create these tables in a dataset named `air_quality`.
-- Use wildcard URIs for the hourly data tables so a single table
-- spans all 31 days of files.
--
-- After creating the tables, verify they work by running:
--     SELECT count(*) FROM air_quality.<table_name>;


-- Hourly Observations — CSV
CREATE OR REPLACE EXTERNAL TABLE air_quality.hourly_observations_csv (
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
OPTIONS (
    format = 'CSV',
    uris = ['gs://cc-s26-assignment-3-maynard-data/air_quality/hourly/*.csv'],
    skip_leading_rows = 1
);


-- Hourly Observations — JSON-L
CREATE OR REPLACE EXTERNAL TABLE air_quality.hourly_observations_jsonl (
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
OPTIONS (
    format = 'NEWLINE_DELIMITED_JSON',
    uris = ['gs://cc-s26-assignment-3-maynard-data/air_quality/hourly/*.jsonl']
);


-- Hourly Observations — Parquet
CREATE OR REPLACE EXTERNAL TABLE air_quality.hourly_observations_parquet
OPTIONS (
    format = 'PARQUET',
    uris = ['gs://cc-s26-assignment-3-maynard-data/air_quality/hourly/*.parquet']
);


-- Site Locations — CSV
CREATE OR REPLACE EXTERNAL TABLE air_quality.site_locations_csv (
    station_id          STRING,
    aqsid               STRING,
    full_aqsid          STRING,
    site_name           STRING,
    status              STRING,
    agency_id           STRING,
    agency_name         STRING,
    epa_region          STRING,
    latitude            FLOAT64,
    longitude           FLOAT64,
    elevation           FLOAT64,
    gmt_offset          FLOAT64,
    country_fips        STRING,
    cbsa_id             STRING,
    cbsa_name           STRING,
    state_aqs_code      STRING,
    state_abbreviation  STRING,
    county_aqs_code     STRING,
    county_name         STRING
)
OPTIONS (
    format = 'CSV',
    uris = ['gs://cc-s26-assignment-3-maynard-data/air_quality/sites/site_locations.csv'],
    skip_leading_rows = 1
);


-- Site Locations — JSON-L
CREATE OR REPLACE EXTERNAL TABLE air_quality.site_locations_jsonl (
    station_id          STRING,
    aqsid               STRING,
    full_aqsid          STRING,
    site_name           STRING,
    status              STRING,
    agency_id           STRING,
    agency_name         STRING,
    epa_region          STRING,
    latitude            FLOAT64,
    longitude           FLOAT64,
    elevation           FLOAT64,
    gmt_offset          FLOAT64,
    country_fips        STRING,
    cbsa_id             STRING,
    cbsa_name           STRING,
    state_aqs_code      STRING,
    state_abbreviation  STRING,
    county_aqs_code     STRING,
    county_name         STRING
)
OPTIONS (
    format = 'NEWLINE_DELIMITED_JSON',
    uris = ['gs://cc-s26-assignment-3-maynard-data/air_quality/sites/site_locations.jsonl']
);


-- Site Locations — GeoParquet
CREATE OR REPLACE EXTERNAL TABLE air_quality.site_locations_geoparquet
OPTIONS (
    format = 'PARQUET',
    uris = ['gs://cc-s26-assignment-3-maynard-data/air_quality/sites/site_locations.geoparquet']
);

-- GeoParquet view with proper GEOGRAPHY type
CREATE OR REPLACE VIEW air_quality.site_locations_geo AS
SELECT
    * EXCEPT (geometry),
    geometry AS geog
FROM air_quality.site_locations_geoparquet;

SELECT COUNT(*) FROM air_quality.hourly_observations_csv;

SELECT COUNT(*) FROM air_quality.hourly_observations_jsonl;

SELECT COUNT(*) FROM air_quality.hourly_observations_parquet;


-- Cross-table join query
-- Average PM2.5 value by state for 2024-07-01,
-- joining hourly observations with site locations for lat/lon and state.
SELECT
    s.state_abbreviation,
    ROUND(AVG(CAST(o.value AS FLOAT64)), 2)  AS avg_pm25,
    COUNT(*)                                  AS observation_count
FROM
    air_quality.hourly_observations_parquet AS o
    INNER JOIN air_quality.site_locations_geo AS s
        ON o.aqsid = s.aqsid
WHERE
    o.parameter_name = 'PM2.5'
    AND o.valid_date  = '07/01/24'
    AND o.value NOT IN ('-999', '')
GROUP BY
    s.state_abbreviation
ORDER BY
    avg_pm25 DESC;