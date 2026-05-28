-- Set local directories and memory limits
SET hive.exec.scratchdir=/tmp/hive/scratch;
SET hive.metastore.warehouse.dir=/tmp/hive/warehouse;
SET hive.query.results.cache.enabled=false;
SET tez.am.resource.memory.mb=512;
SET hive.tez.container.size=512;
SET hive.exec.reducers.bytes.per.reducer=268435456;

CREATE DATABASE IF NOT EXISTS ta_final_db;
USE ta_final_db;

DROP TABLE IF EXISTS tripadvisor_clean_table;

CREATE EXTERNAL TABLE tripadvisor_clean_table (
    name STRING, street_address STRING, location STRING, type STRING,
    reviews STRING, no_of_reviews STRING, comments STRING, contact_number STRING,
    trip_advisor_url STRING, menu STRING, price_range STRING
) ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' 
STORED AS TEXTFILE
LOCATION 'gs://kaggle_silver_bucket/tripadvisor_cleaned/';

-- Location of the file must be in folder format, dont point it to the csv file.

SELECT location, type, price_range, COUNT(name) as total_restaurants
FROM tripadvisor_clean_table
WHERE location IS NOT NULL AND location != 'location'
GROUP BY location, type, price_range
ORDER BY total_restaurants DESC