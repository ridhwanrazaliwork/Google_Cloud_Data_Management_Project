# -*- coding: utf-8 -*-
"""
Spark Pipeline: TripAdvisor Restaurant Recommendation Analysis
Dataset: TripAdvisor_RestauarantRecommendation.csv
Platform: Google Cloud Dataproc
Comparison: Same 6 analytical queries as Hive pipeline
"""

from pyspark.sql import SparkSession, Window
from pyspark.sql.functions import *
from pyspark.sql.types import *
import time

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("TripAdvisorRestaurantAnalysis") \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
    .getOrCreate()

print("=" * 80)
print("SPARK PIPELINE: TRIPADVISOR RESTAURANT RECOMMENDATION ANALYSIS")
print("=" * 80)

start_time = time.time()

# ============================================================================
# STEP 1: DATA INGESTION
# ============================================================================
print("\n[1] Loading data from GCS...")

INPUT_PATH = "gs://kaggle_silver_bucket/tripadvisor_cleaned/silver_tripadvisor.csv"

try:
    df = spark.read \
        .option("header", "true") \
        .option("inferSchema", "true") \
        .option("quote", "\"") \
        .option("escape", "\"") \
        .csv(INPUT_PATH)

    print(f"Loaded {df.count():,} records with {len(df.columns)} columns")
except Exception as e:
    print(f"Error loading data: {e}")
    sys.exit(1)

# ============================================================================
# STEP 2: DATA EXPLORATION
# ============================================================================
print("\n[2] Data Exploration...")

df.printSchema()
df.select("name", "location", "type", "reviews", "no_of_reviews", "price_range").show(5, truncate=False)

# ============================================================================
# STEP 3: DATA CLEANING & TRANSFORMATION
# ============================================================================
print("\n[3] Data Cleaning & Transformation...")

df_cleaned = df \
    .withColumn("rating",
                split(col("reviews"), " ").getItem(0).cast("double")) \
    .withColumn("review_count",
                regexp_replace(col("no_of_reviews"), "[^0-9]", "").cast("int")) \
    .withColumn("city",
                trim(split(col("location"), ",").getItem(0))) \
    .withColumn("state_location",
                trim(split(col("location"), ",").getItem(1))) \
    .withColumn("cuisine_list",
                split(col("type"), ",")) \
    .filter(col("reviews").isNotNull() & (col("reviews") != "Reviews"))

df_cleaned.cache()
print(f"Cleaned dataset: {df_cleaned.count():,} records")

# Register temp view for SQL
df_cleaned.createOrReplaceTempView("restaurants")

# ============================================================================
# STEP 4: ANALYTICAL QUERIES
# ============================================================================
print("\n[4] Executing Analytical Queries...")

# --- ANALYSIS 1: Average Rating by Price Range ---
print("\n--- Analysis 1: Average Rating by Price Range ---")
avg_rating_by_price = spark.sql("""
    SELECT
        price_range,
        ROUND(AVG(rating), 2) AS avg_rating,
        COUNT(*) AS restaurant_count,
        ROUND(STDDEV(rating), 2) AS rating_stddev
    FROM restaurants
    WHERE price_range IS NOT NULL AND price_range != ''
    GROUP BY price_range
    ORDER BY avg_rating DESC
""")
avg_rating_by_price.show(truncate=False)

# --- ANALYSIS 2: Top 10 Highest Rated Restaurants ---
print("\n--- Analysis 2: Top 10 Highest Rated Restaurants ---")
top_rated = spark.sql("""
    SELECT
        name, location, type, rating, review_count, price_range
    FROM restaurants
    WHERE rating > 0
    ORDER BY rating DESC, review_count DESC
    LIMIT 10
""")
top_rated.show(truncate=False)

# --- ANALYSIS 3: Restaurant Count by City ---
print("\n--- Analysis 3: Top 20 Cities by Restaurant Count ---")
restaurants_by_city = spark.sql("""
    SELECT
        city, state_location,
        COUNT(*) AS restaurant_count,
        ROUND(AVG(rating), 2) AS avg_rating
    FROM restaurants
    WHERE city IS NOT NULL AND city != ''
    GROUP BY city, state_location
    ORDER BY restaurant_count DESC
    LIMIT 20
""")
restaurants_by_city.show(truncate=False)

# --- ANALYSIS 4: Rating Distribution by Cuisine Type ---
print("\n--- Analysis 4: Top 20 Cuisine Types by Restaurant Count ---")
cuisine_analysis = spark.sql("""
    SELECT
        TRIM(cuisine) AS cuisine_type,
        ROUND(AVG(rating), 2) AS avg_rating,
        COUNT(*) AS restaurant_count,
        ROUND(AVG(review_count), 0) AS avg_reviews
    FROM restaurants
    LATERAL VIEW OUTER EXPLODE(SPLIT(type, ',')) type_table AS cuisine
    WHERE TRIM(cuisine) != '' AND TRIM(cuisine) != 'Type'
    GROUP BY TRIM(cuisine)
    ORDER BY restaurant_count DESC
    LIMIT 20
""")
cuisine_analysis.show(truncate=False)

# --- ANALYSIS 5: Most Reviewed Restaurants ---
print("\n--- Analysis 5: Top 10 Most Reviewed Restaurants ---")
most_reviewed = spark.sql("""
    SELECT
        name, location, type, review_count, rating, price_range
    FROM restaurants
    WHERE review_count > 0
    ORDER BY review_count DESC
    LIMIT 10
""")
most_reviewed.show(truncate=False)

# --- ANALYSIS 6: Top Rated Restaurant per Price Range ---
print("\n--- Analysis 6: Top Rated Restaurant per Price Range ---")
top_per_price = spark.sql("""
    SELECT
        price_range, name, location, rating, review_count
    FROM (
        SELECT
            price_range, name, location, rating, review_count,
            ROW_NUMBER() OVER (
                PARTITION BY price_range
                ORDER BY rating DESC, review_count DESC
            ) AS rn
        FROM restaurants
        WHERE price_range IS NOT NULL AND price_range != '' AND rating > 0
    ) ranked
    WHERE rn = 1
    ORDER BY rating DESC
""")
top_per_price.show(truncate=False)

# ============================================================================
# ============================================================================
# PERFORMANCE METRICS
# ============================================================================
print("\n[6] Pipeline Performance Metrics...")

end_time = time.time()
print(f"Pipeline runtime: {end_time - start_time:.2f} seconds")

print("\n" + "=" * 80)
print("SPARK PIPELINE COMPLETED SUCCESSFULLY")
print("=" * 80)

spark.stop()
