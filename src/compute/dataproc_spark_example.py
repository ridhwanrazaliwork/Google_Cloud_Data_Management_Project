import time
from pyspark.sql import SparkSession

# Re-initialize the session with an explicitly safe warehouse location path
spark = SparkSession.builder \
    .appName("UM-Multi-Engine-Benchmark") \
    .config("spark.sql.warehouse.dir", "file:///tmp/spark-warehouse") \
    .enableHiveSupport() \
    .getOrCreate()

print("Spark Session successfully bound to write-permissive warehouse directory.")

import time
from pyspark.sql.functions import col, count, avg

start_spark = time.time()

BRONZE_DATA_PATH = "gs://kaggle_silver_bucket/tripadvisor_cleaned/silver_tripadvisor.csv"

# 1. Read Raw Dataset
spark_df = spark.read.csv(BRONZE_DATA_PATH, header=True, inferSchema=True)

# 2. Run aggregations over real columns: location, type, and price_range
spark_metrics = spark_df.filter(col("location").isNotNull()) \
                         .groupBy("location", "type", "price_range") \
                         .agg(count("name").alias("total_restaurants")) \
                         .sort(col("total_restaurants").desc())

# Show a snippet in your notebook
spark_metrics.show(5)

# 3. Export Out to Medallion Gold Layer in Cloud Storage (GCS)
# This saves the metrics output as clean distributed parquet files
spark_metrics.write.mode("overwrite").parquet("gs://kaggle_gold_bucket/gold_spark_metrics/")

# 4. Export Out directly into BigQuery Warehouse
# Dataproc clusters have a built-in BigQuery connector configuration
spark_metrics.write.format("bigquery") \
    .option("table", "bigdatamanagement-497302.restaurant_gold_db.spark_restaurant_summary") \
    .option("temporaryGcsBucket", "dataproc_staging_kaggle") \
    .mode("overwrite") \
    .save()

end_spark = time.time()
print(f"⏱️ APACHE SPARK SYSTEM RUNTIME: {end_spark - start_spark} SECONDS")

# Place this at the absolute bottom of your Spark analytics cell
spark.stop()
print("Spark Session closed successfully. YARN containers released for subsequent Hive/Pig runs.")