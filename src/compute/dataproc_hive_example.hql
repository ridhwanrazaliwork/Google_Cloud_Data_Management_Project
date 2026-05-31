-- ============================================================================
-- HIVE PIPELINE: TRIPADVISOR (DIRECT RAW QUERY - NO CTAS)
-- ============================================================================

SET hive.exec.scratchdir=/tmp/hive/scratch;
SET hive.metastore.warehouse.dir=/tmp/hive/warehouse;
SET hive.query.results.cache.enabled=false;
SET tez.am.resource.memory.mb=2048;
SET hive.tez.container.size=2048;
SET hive.exec.reducers.bytes.per.reducer=268435456;
SET hive.cli.print.header=true;

DROP TABLE IF EXISTS tripadvisor_raw;

CREATE EXTERNAL TABLE tripadvisor_raw (
    name STRING, street_address STRING, location STRING, type STRING,
    reviews STRING, no_of_reviews STRING, comments STRING, contact_number STRING,
    trip_advisor_url STRING, menu STRING, price_range STRING
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES ("separatorChar" = ",", "quoteChar" = "\"")
STORED AS TEXTFILE
LOCATION 'gs://kaggle_silver_bucket/tripadvisor_cleaned/'
TBLPROPERTIES ("skip.header.line.count"="1");

-- ============================================================================
-- ANALYSIS 1: AVG RATING BY PRICE RANGE
-- ============================================================================

SELECT '=== ANALYSIS 1: AVG RATING BY PRICE RANGE ===' AS step;
SELECT
    price_range,
    ROUND(AVG(CAST(SPLIT(reviews, ' ')[0] AS DOUBLE)), 2) AS avg_rating,
    COUNT(*) AS restaurant_count,
    ROUND(STDDEV(CAST(SPLIT(reviews, ' ')[0] AS DOUBLE)), 2) AS rating_stddev
FROM tripadvisor_raw
WHERE price_range IS NOT NULL AND price_range != ''
  AND reviews IS NOT NULL AND reviews != 'Reviews'
GROUP BY price_range
ORDER BY avg_rating DESC;

-- ============================================================================
-- ANALYSIS 2: TOP 10 HIGHEST RATED RESTAURANTS
-- ============================================================================

SELECT '=== ANALYSIS 2: TOP 10 HIGHEST RATED RESTAURANTS ===' AS step;
SELECT
    name, location, type,
    CAST(SPLIT(reviews, ' ')[0] AS DOUBLE) AS rating,
    CAST(REGEXP_REPLACE(no_of_reviews, '[^0-9]', '') AS INT) AS review_count,
    price_range
FROM tripadvisor_raw
WHERE reviews IS NOT NULL AND reviews != 'Reviews'
  AND CAST(SPLIT(reviews, ' ')[0] AS DOUBLE) > 0
ORDER BY CAST(SPLIT(reviews, ' ')[0] AS DOUBLE) DESC,
         CAST(REGEXP_REPLACE(no_of_reviews, '[^0-9]', '') AS INT) DESC
LIMIT 10;

-- ============================================================================
-- ANALYSIS 3: RESTAURANT COUNT BY CITY (TOP 20)
-- ============================================================================

SELECT '=== ANALYSIS 3: TOP 20 CITIES BY RESTAURANT COUNT ===' AS step;
SELECT
    SPLIT(location, ',')[0] AS city,
    TRIM(SPLIT(location, ',')[1]) AS state_location,
    COUNT(*) AS restaurant_count,
    ROUND(AVG(CAST(SPLIT(reviews, ' ')[0] AS DOUBLE)), 2) AS avg_rating
FROM tripadvisor_raw
WHERE reviews IS NOT NULL AND reviews != 'Reviews'
  AND SPLIT(location, ',')[0] IS NOT NULL AND SPLIT(location, ',')[0] != ''
GROUP BY SPLIT(location, ',')[0], TRIM(SPLIT(location, ',')[1])
ORDER BY restaurant_count DESC
LIMIT 20;

-- ============================================================================
-- ANALYSIS 4: RATING BY CUISINE TYPE
-- ============================================================================

SELECT '=== ANALYSIS 4: TOP 20 CUISINE TYPES ===' AS step;
SELECT
    TRIM(cuisine) AS cuisine_type,
    ROUND(AVG(CAST(SPLIT(reviews, ' ')[0] AS DOUBLE)), 2) AS avg_rating,
    COUNT(*) AS restaurant_count,
    ROUND(AVG(CAST(REGEXP_REPLACE(no_of_reviews, '[^0-9]', '') AS INT)), 0) AS avg_reviews
FROM tripadvisor_raw
LATERAL VIEW OUTER EXPLODE(SPLIT(type, ',')) type_table AS cuisine
WHERE reviews IS NOT NULL AND reviews != 'Reviews'
  AND TRIM(cuisine) != '' AND TRIM(cuisine) != 'Type'
GROUP BY TRIM(cuisine)
ORDER BY restaurant_count DESC
LIMIT 20;

-- ============================================================================
-- ANALYSIS 5: TOP 10 MOST REVIEWED RESTAURANTS
-- ============================================================================

SELECT '=== ANALYSIS 5: TOP 10 MOST REVIEWED RESTAURANTS ===' AS step;
SELECT
    name, location, type,
    CAST(REGEXP_REPLACE(no_of_reviews, '[^0-9]', '') AS INT) AS review_count,
    CAST(SPLIT(reviews, ' ')[0] AS DOUBLE) AS rating,
    price_range
FROM tripadvisor_raw
WHERE reviews IS NOT NULL AND reviews != 'Reviews'
  AND CAST(REGEXP_REPLACE(no_of_reviews, '[^0-9]', '') AS INT) > 0
ORDER BY CAST(REGEXP_REPLACE(no_of_reviews, '[^0-9]', '') AS INT) DESC
LIMIT 10;

-- ============================================================================
-- ANALYSIS 6: TOP RATED PER PRICE RANGE (WINDOW FUNCTION)
-- ============================================================================

SELECT '=== ANALYSIS 6: TOP RATED PER PRICE RANGE ===' AS step;
SELECT
    price_range, name, location, rating, review_count
FROM (
    SELECT
        price_range, name, location,
        CAST(SPLIT(reviews, ' ')[0] AS DOUBLE) AS rating,
        CAST(REGEXP_REPLACE(no_of_reviews, '[^0-9]', '') AS INT) AS review_count,
        ROW_NUMBER() OVER (PARTITION BY price_range ORDER BY CAST(SPLIT(reviews, ' ')[0] AS DOUBLE) DESC, CAST(REGEXP_REPLACE(no_of_reviews, '[^0-9]', '') AS INT) DESC) AS rn
    FROM tripadvisor_raw
    WHERE reviews IS NOT NULL AND reviews != 'Reviews'
      AND price_range IS NOT NULL AND price_range != ''
      AND CAST(SPLIT(reviews, ' ')[0] AS DOUBLE) > 0
) ranked
WHERE rn = 1
ORDER BY rating DESC;

SELECT '=== PIPELINE COMPLETE ===' AS step;
