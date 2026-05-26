-- 1. Load the raw data from the newly isolated GCS folder
raw_data = LOAD 'gs://kaggle_bronze_bucket/tripadvisor_raw/' USING PigStorage(',') 
    AS (
        name:chararray, 
        street_address:chararray, 
        location:chararray, 
        type:chararray, 
        reviews:chararray, 
        no_of_reviews:chararray, 
        comments:chararray, 
        contact_number:chararray, 
        trip_advisor_url:chararray, 
        menu:chararray, 
        price_range:chararray
    );

-- 2. Clean the data (Filter out nulls and the CSV header row)
filtered_data = FILTER raw_data BY location IS NOT NULL AND location != 'location';

-- 3. Project only the required columns (This saves massive amounts of RAM during the shuffle)
projected_data = FOREACH filtered_data GENERATE location, type, price_range, name;

-- 4. Group the data by our analytical dimensions
grouped_data = GROUP projected_data BY (location, type, price_range);

-- 5. Calculate the aggregate metrics (This triggers the heavy MapReduce phase)
final_metrics = FOREACH grouped_data GENERATE 
    FLATTEN(group) AS (location, type, price_range), 
    COUNT(projected_data.name) AS total_restaurants;

-- 6. Sort the results
sorted_metrics = ORDER final_metrics BY total_restaurants DESC;

-- 7. Limit to top 5 and print to the screen
limited_metrics = LIMIT sorted_metrics 5;
DUMP limited_metrics;