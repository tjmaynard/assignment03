# Assignment 03 Responses

## Part 4: BigQuery External Tables

### Hourly Observations — CSV External Table SQL

```sql
-- Paste your CREATE EXTERNAL TABLE statement here (use a wildcard URI)

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

```

### Hourly Observations — JSON-L External Table SQL

```sql
-- Paste your CREATE EXTERNAL TABLE statement here (use a wildcard URI)

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

```

### Hourly Observations — Parquet External Table SQL

```sql
-- Paste your CREATE EXTERNAL TABLE statement here (use a wildcard URI)

CREATE OR REPLACE EXTERNAL TABLE air_quality.hourly_observations_parquet
OPTIONS (
    format = 'PARQUET',
    uris = ['gs://cc-s26-assignment-3-maynard-data/air_quality/hourly/*.parquet']
);

```

### Site Locations — CSV External Table SQL

```sql
-- Paste your CREATE EXTERNAL TABLE statement here

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

```

### Site Locations — JSON-L External Table SQL

```sql
-- Paste your CREATE EXTERNAL TABLE statement here

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

```

### Site Locations — GeoParquet External Table SQL

```sql
-- Paste your CREATE EXTERNAL TABLE statement here

CREATE OR REPLACE EXTERNAL TABLE air_quality.site_locations_geoparquet
OPTIONS (
    format = 'PARQUET',
    uris = ['gs://cc-s26-assignment-3-maynard-data/air_quality/sites/site_locations.geoparquet']
);

```

### Cross-Table Join Query

```sql
-- Paste your query that joins hourly observations with site locations here

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

```

---

## Part 5: Hive-Partitioned External Tables

### Hourly Observations — CSV (hive-partitioned)

```sql
-- Paste your CREATE EXTERNAL TABLE statement with hive partitioning options

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

```

### Hourly Observations — JSON-L (hive-partitioned)

```sql
-- Paste your CREATE EXTERNAL TABLE statement with hive partitioning options

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

```

### Hourly Observations — Parquet (hive-partitioned)

```sql
-- Paste your CREATE EXTERNAL TABLE statement with hive partitioning options

CREATE OR REPLACE EXTERNAL TABLE air_quality.hourly_observations_parquet_hive
WITH PARTITION COLUMNS (
    airnow_date DATE
)
OPTIONS (
    format = 'PARQUET',
    uris = ['gs://cc-s26-assignment-3-maynard-data/air_quality/hourly/parquet/*'],
    hive_partition_uri_prefix = 'gs://cc-s26-assignment-3-maynard-data/air_quality/hourly/parquet'
);

```

---

## Part 6: Analysis & Reflection

### 1. File Sizes

**Hourly data (single day):**

| Format  | File Size |
|---------|-----------|
| CSV     |  17.9 MB  |
| JSON-L  |  46.9 MB  |
| Parquet |  816.1 KB |

**Site locations:**

| Format     | File Size |
|------------|-----------|
| CSV        |  943.4 KB |
| JSON-L     |  3.0 MB   |
| GeoParquet |  481.3 KB |

**Analysis:**

> [Your answer here — which is smallest/largest and why?]

For the hourly data (referenced 2024-07-01), Parquet is significantly smaller than CSV and JSON-L. For site locations, GeoParquet is smaller than CSV and JSON-L. This is because (Geo)Parquet is a columnar, compressed format that stores data more efficiently and avoids repeating field names, whereas CSV and JSON-L are row-based and largely uncompressed, resulting in much larger file sizes.

### 2. Format Anatomy

> [Pick two formats and describe their structure. What are the key differences?]

CSV is a simple, row-based format where each line represents a record and columns are separated by commas, with little built-in structure beyond a header row. Conversely, Parquet follows a columnar structure, includes schema and data types, and uses compression to reduce file size. The key difference is that CSV requires reading entire rows with minimal structure, while Parquet enables more efficient storage and querying by scanning only the columns needed.

### 3. Choosing Formats for BigQuery

> [Why is Parquet preferred over CSV or JSON-L? Consider performance and cost.]

Parquet is preferred in BigQuery because it is a columnar format, which allows queries to scan only the columns they need instead of the entire dataset. This significantly improves performance and reduces query costs. Additionally, Parquet’s built-in compression results in smaller storage sizes and less data processed during queries, further lowering costs compared to CSV or JSON-L.

### 4. Pipeline vs. Warehouse Joins

> [You kept hourly data and site locations as separate tables and joined them in BigQuery. What if you had joined them during the prepare step instead (denormalization)? What are the trade-offs of each approach?]

Keeping hourly data and site locations as separate tables makes the workflow more flexible and avoids repeating the same site information for every hourly record. It also makes updates easier, since changes to site locations only need to be made in one table. If the tables were joined during the prepare step, the final dataset would be easier to query in BigQuery because all fields would already be in one place. However, this denormalized approach would increase file size, duplicate site information many times, and make updates less efficient. Thus, for this analysis, keeping them separate is optimal.

#### Stretch Challenge (optional)

If you implemented the stretch challenge (scripts `06_prepare`, `06_upload_to_gcs`, `06_create_tables.sql`), paste your SQL statements here:

```sql
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

```

```sql
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

```

```sql
-- Merged Hourly + Sites — GeoParquet (hive-partitioned)

CREATE OR REPLACE EXTERNAL TABLE air_quality.hourly_with_sites_geoparquet
WITH PARTITION COLUMNS (
    airnow_date DATE
)
OPTIONS (
    format = 'PARQUET',
    uris = ['gs://cc-s26-assignment-3-maynard-data/air_quality/hourly_with_sites/geoparquet/*'],
    hive_partition_uri_prefix = 'gs://cc-s26-assignment-3-maynard-data/air_quality/hourly_with_sites/geoparquet'
);

```

### 5. Choosing a Data Source

For each person below, which air quality data source (AirNow hourly files, AirNow API, AQS bulk downloads, or AQS API) would you recommend, and why?

**a) A parent who wants a dashboard showing current air quality near their child's school:**

I would recommend the AirNow API. Since the parent is only interested in current air quality conditions near their child’s school, this approach avoids unnecessary data extraction of other areas. Additionally, the API’s near-real-time query capabilities make it well-suited for this use case, as it can easily support a dashboard that updates with the latest AQI data.

**b) An environmental justice advocate identifying neighborhoods with chronically poor air quality over the past decade:**

I would recommend AQS bulk downloads. Since the environmental justice advocate would need large amounts of historical data, bulk access to long-term, quality-controlled AQI data is essential for analyzing trends and identifying neighborhoods with chronically poor air quality over time.

**c) A school administrator who needs automated morning alerts when AQI exceeds a threshold:**

I would recommend the AirNow API. Since the school administrator is only concerned with AQI data for a short period of time each day, this approach minimizes unnecessary data extraction. Additionally, the API’s near-real-time query capabilities make it well-suited for this use case, as the administrator can retrieve current conditions and issue alerts the same morning if thresholds are exceeded.

