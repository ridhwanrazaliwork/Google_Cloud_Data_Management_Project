# Team Task Allocation - 8 People (Minimal Dependencies)

## Dependency Map Analysis
```
Person 1 (Intro) → [INDEPENDENT]
Person 2 (Architecture) → [INDEPENDENT]
Person 3 (IAM + Ingestion) → Produces: Bronze CSV in GCS
Person 4 (Data Cleaning) → Depends on: Person 3 ✓ (clear input/output)
Person 5 (Apache Tools) → Depends on: Person 4 ✓ (clear input: Silver CSV)
Person 6 (Dashboard) → Depends on: Person 5 ✓ (clear input: Gold results in BigQuery)
Person 7 (Results Analysis) → Depends on: Person 5 ✓ (uses Person 5 output)
Person 8 (Conclusion) → Depends on: All completed ✓ (synthesis only)
```

**Key Advantage:** Linear dependency chain, not parallel or circular
- If Person 3 delays → Only Person 4 waits
- If Person 4 delays → Only Person 5 waits
- Other people can work independently

---

## Person-by-Person Detailed Breakdown

### **PERSON 1 - Introduction, Abstract, Problem Statements**
**Workload:** 🟢 **LIGHT**
**Independence:** ✅ **FULLY INDEPENDENT** (no technical dependencies)

#### Deliverables:
- Abstract (200-250 words)
- Keywords (5 keywords separated by semicolons)
- Introduction
  - Domain context (tourism/hospitality)
  - Business problem
  - Project motivation
- Problem Statements (3 defined)
  1. Data ingestion & quality challenge
  2. Business intelligence extraction challenge
  3. Compute engine performance benchmarking challenge

#### Report (~1.5-2 pages)
```
Page 1: Abstract + Keywords

Page 1.5-2: Introduction
  - Tourism domain overview
  - Why big data matters
  - Project objectives

Page 2-2.5: Problem Statements
  - Problem 1: Ingestion & Quality
  - Problem 2: Business Intelligence
  - Problem 3: Compute Performance Benchmark
```

#### Presentation (1 min)
- Quick hook on domain/problem
- 3 problems in 30 sec
- Why this project matters

#### Can start: **Immediately** ✅
#### Blocks: **Nobody** ✅

---

### **PERSON 2 - Architecture & Framework Explanation**
**Workload:** 🟢 **LIGHT**
**Independence:** ✅ **FULLY INDEPENDENT** (no technical dependencies)

#### Deliverables:
- Architecture diagrams (Mermaid or visual or excalidraw)
- Framework explanation (Medallion architecture)
- GCP service stack diagram
- Data flow pipeline visualization

#### Report (~1.5-2 pages)
```
Page 3: Framework Design & Medallion Architecture
  - Bronze layer (raw data)
  - Silver layer (cleaned data)
  - Gold layer (curated/aggregated data)
  - Visual diagram

Page 3.5-4: GCP Service Stack
  - Cloud Run (ingestion)
  - Cloud Storage (landing zones)
  - Dataproc (compute)
  - BigQuery (warehouse)
  - Looker Studio (BI)
  - Diagram showing all services

Expected flow that we might have:

1. **Ingestion (Bronze Layer)**  
   - Kaggle API → Cloud Run (Flask app) → Raw CSV stored in `gs://kaggle_bronze/`

2. **Quality Engineering (Silver Layer)**  
   - Clean using either:  
     - Cloud DataPrep (no‑code, deduplication, null removal) **or**  
     - PySpark + Great Expectations (programmatic) in dataproc **or** Bigquery
  
   - Output to `gs://kaggle_silver/`

3. **Metric Engineering (Gold Layer)**  
   - Dataproc cluster (e2-highmem-4) processes silver data via PySpark, Hive, or Pig  
   - Curated results written to BigQuery (`restaurant_gold_db`)

4. **Consumption**  
   - Looker Studio dashboard connected directly to BigQuery

```

#### Presentation (1 min)
- Show 3-layer architecture
- Explain each layer purpose
- Show GCP service relationships

#### Can start: **Immediately** ✅
#### Blocks: **Nobody** ✅

---

### **PERSON 3 (RIDHWAN) - IAM, Access Management & Ingestion**
**Workload:** 🔴 ** HEAVY**
**Independence:** ✅ **INDEPENDENT** (first in data pipeline chain)
**Output:** `gs://kaggle_bronze_bucket/bronze_tripadvisor.csv`

#### Technical Responsibilities:

**1. IAM & Service Account Setup** 

```bash
for ROLE in storage.admin secretmanager.secretAccessor dataproc.editor metastore.editor bigquery.admin; do \
  gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
    --role="roles/${ROLE}"; \
done
```


**2. Secret Manager Setup**
- Store `kaggle.json` in Secret Manager
- Path: `projects/{PROJECT_ID}/secrets/kaggle-json/versions/latest`
- Create access credentials for team members

**3. Cloud Run Ingestion Deployment** 

**4. Test & Validate Ingestion**
- Deploy Cloud Run function
- Test curl request
- Verify CSV uploaded to Bronze bucket
- Document row count & column count output

#### Report (~2-2.5 pages)
```
Page 5: IAM & Access Management
  - Service account creation
  - Role-based access control (RBAC)
  - Roles assigned (storage.admin, secretmanager, dataproc.editor, bigquery.admin)
  - Team member access credentials
  - Security best practices

Page 5.5-6: Data Ingestion Pipeline
  - Cloud Run Flask app architecture
  - Secret Manager integration (Kaggle credentials)
  - Kaggle API authentication flow
  - GCS Bronze bucket output
  - Sample output: Row count, column count
  - Execution logs & error handling
```

#### Presentation (1.5 min)
- Show IAM role assignments
- Demo Cloud Run function call
- "Kaggle → Cloud Run → GCS Bronze (automated)"
- Show output: X rows, Y columns in Bronze bucket

#### Deliverables:
```
src/ingestion/
├── ingestion_cloudrun.py          [Flask app]
├── requirements.txt               [Dependencies]

Output: gs://kaggle_bronze_bucket/bronze_tripadvisor.csv
```

#### Can start: **Immediately** ✅
#### Blocks: **Person 4 (Data Cleaning)** ⏳

---

### **PERSON 4 - Data Cleaning (Cloud Dataprep)**
**Workload:** 🟡 **MEDIUM** (~15-20 hours)
**Independence:** ❌ **DEPENDS ON PERSON 3** (Bronze CSV)
**Input:** `gs://kaggle_bronze_bucket/raw/raw_bronze.csv`
**Output:** `gs://kaggle_silver_bucket/clean/clean_silver.csv`

#### Technical Responsibilities:

**1. Cloud Dataprep Setup & Configuration** (3-5 hours)
- Create Dataprep flow
- Connect to GCS Bronze bucket
- Load bronze_tripadvisor.csv

**2. Create Data Quality Recipes** (8-12 hours)
```
Recipe 1: Deduplication
├── Remove duplicate rows
└── Document: X rows removed

Recipe 2: Null Handling
├── Remove rows with NULL in key columns (location, type)
├── Fill NULL in optional columns with "Unknown"
└── Document: Y rows removed, Z nulls replaced

Recipe 3: Type Casting
├── Ensure numeric columns (rating, review_count) are float/int
├── Ensure text columns (location, type) are string
├── Standardize price_range to uppercase
└── Document: Type conversion rules applied

Recipe 4: Structural Cleaning
├── Remove leading/trailing whitespace
├── Standardize location names (consistent casing)
├── Remove special characters if needed
└── Document: Cleaning steps applied
```

**3. Execute Recipes & Validate Output** (3-5 hours)
- Run Dataprep recipes to completion
- Output to GCS Silver bucket: `gs://kaggle_silver_bucket/clean/clean_silver.csv`
- Generate data quality report
- Record before/after metrics

#### Report (~1.5 pages)
```
Page 7: Data Cleaning & Quality Engineering
  - Raw data challenges (duplicates, nulls, inconsistencies)
  - Cloud Dataprep recipe overview (visual diagrams)
  
  Recipe Details:
  1. Deduplication
     - Found X duplicate rows
     - Removed X rows (Y% of dataset)
  
  2. Null Handling
     - Location: A% missing → 0% after cleaning
     - Type: B% missing → 0% after cleaning
     - Optional columns: C% missing → D% after imputation
  
  3. Type Casting
     - Rating: converted to FLOAT
     - Review count: converted to INT
     - Price range: standardized to uppercase
  
  - Before/After Comparison Table
    | Metric | Before | After | Change |
    | Total Rows | X | Y | -Z rows (-W%) |
    | Null Columns | A% | B% | -C% |
    | Duplicates | D rows | 0 | -D rows |
  
  - Sample clean data (5 rows showing structure)
  - Output location: `gs://kaggle_silver_bucket/clean/clean_silver.csv`
```

#### Presentation (1 min)
- Show Dataprep UI screenshot
- "Raw data: X% duplicates, Y% nulls"
- "After cleaning: 0% duplicates, Z% nulls"
- Before/after bar chart
- "Ready for compute engines"

#### Deliverables:
```
dataprep/
├── dataprep_recipe.json           [Exported recipe]
├── before_profile.csv             [Data quality before]
├── after_profile.csv              [Data quality after]
└── quality_report.md              [Summary metrics]

Output: gs://kaggle_silver_bucket/tripadvisor_clean.csv
```

#### Can start: **After Person 3 completes ingestion** ⏳
#### Blocks: **Person 5 (Apache Tools)** ⏳

---

### **PERSON 5 - Apache Tools Comparison (Spark, Hive, Pig)**
**Workload:** 🔴 **VERY HEAVY**
**Independence:** ❌ **DEPENDS ON PERSON 4** (Silver CSV)
**Input:** `gs://kaggle_silver_bucket/clean/clean_silver.csv`

# We use Only the best/fastest tools for writing the output to GCS, Bigquery
**Output:** 
- `gs://kaggle_gold_bucket/spark_results/`
- `gs://kaggle_gold_bucket/hive_results/`
- `gs://kaggle_gold_bucket/pig_results/`
- Performance metrics (execution times)

#### Technical Responsibilities:

**1. PySpark Implementation** (Sample code, which u can find in the repo as well)
```python
# src/compute/dataproc_spark.py
import time
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count

spark = SparkSession.builder \
    .appName("Tripadvisor-Benchmark-Spark") \
    .config("spark.sql.warehouse.dir", "file:///tmp/spark-warehouse") \
    .enableHiveSupport() \
    .getOrCreate()

print("=" * 60)
print("APACHE SPARK BENCHMARK")
print("=" * 60)

start_spark = time.time()

# Load Silver data
df = spark.read.csv("gs://kaggle_silver_bucket/tripadvisor_clean.csv", 
                    header=True, inferSchema=True)

print(f"Loaded {df.count()} rows")

# Execute benchmark query
result = df.filter(col("location").isNotNull()) \
           .groupBy("location", "type", "price_range") \
           .agg(count("name").alias("total_restaurants")) \
           .sort(col("total_restaurants").desc()) \
           .limit(5)

result.show()

# Write to Gold layer (GCS)
result.write.mode("overwrite").parquet("gs://kaggle_gold_bucket/spark_results/")

# Write to BigQuery
result.write.format("bigquery") \
      .option("table", "restaurant_gold_db.spark_benchmark_results") \
      .mode("overwrite") \
      .save()

end_spark = time.time()
spark_time = end_spark - start_spark

print("=" * 60)
print(f"SPARK EXECUTION TIME: {spark_time:.2f} seconds")
print("=" * 60)

spark.stop()
```

**2. HiveQL Implementation** (Sample code, which u can find in the repo as well)
```sql
-- src/compute/dataproc_hive.hql
CREATE EXTERNAL TABLE tripadvisor_clean_table (
    name STRING,
    location STRING,
    type STRING,
    price_range STRING,
    rating FLOAT,
    review_count INT
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
LOCATION 'gs://kaggle_silver_bucket/tripadvisor_clean/';

SELECT location, type, price_range, COUNT(name) as total_restaurants
FROM tripadvisor_clean_table
WHERE location IS NOT NULL AND location != 'location'
GROUP BY location, type, price_range
ORDER BY total_restaurants DESC
LIMIT 5;
```

**3. Pig Latin Implementation** (Sample code, which u can find in the repo as well)
```pig
-- src/compute/dataproc_pig.pig
tripadvisor = LOAD 'gs://kaggle_silver_bucket/tripadvisor_clean.csv' 
              USING PigStorage(',') AS 
              (name, location, type, price_range, rating, review_count);

filtered = FILTER tripadvisor BY location IS NOT NULL AND location != 'location';

grouped = GROUP filtered BY (location, type, price_range);

counted = FOREACH grouped GENERATE 
          group.location as location,
          group.type as type,
          group.price_range as price_range,
          COUNT(filtered) as total_restaurants;

sorted = ORDER counted BY total_restaurants DESC;

limited = LIMIT sorted 5;

STORE limited INTO 'gs://kaggle_gold_bucket/pig_results/';
```

**4. Execution & Timing**
- Run each tool 1 or 2 times on Dataproc cluster
- Record execution times for each run
- Use `time` command to capture wall-clock time:
  ```bash
  # For Spark
  start_time=$(date +%s)
  spark-submit dataproc_spark.py
  end_time=$(date +%s)
  echo "Spark Runtime: $((end_time - start_time)) seconds"
  
  # For Hive
  start_time=$(date +%s)
  hive -f dataproc_hive.hql
  end_time=$(date +%s)
  echo "Hive Runtime: $((end_time - start_time)) seconds"
  
  # For Pig
  start_time=$(date +%s)
  pig -useHCatalog dataproc_pig.pig
  end_time=$(date +%s)
  echo "Pig Runtime: $((end_time - start_time)) seconds"
  ```
- Screenshot output logs

#### Report (~1.5-2 pages)
```
Page 8: Apache Tools Implementation

1. PySpark Implementation
   - Code architecture & optimization strategy
   - DAG evaluation model explanation
   - Execution time (3 runs):
     * Run 1: X.XX seconds
     * Run 2: X.YY seconds
     * Average: X.XX seconds
   - Sample output (5 rows) or image of the output
   - GitHub link: src/compute/dataproc_spark.py

2. HiveQL Implementation
   - External table definition
   - Query structure
   - Execution time (3 runs):
     * Run 1: A.AA seconds
     * Run 2: A.BB seconds
     * Average: A.AA seconds
   - Sample output (5 rows) or image of the output
   - GitHub link: src/compute/dataproc_hive.hql

3. Pig Latin Implementation
   - Dataflow script structure
   - MapReduce compilation steps
   - Execution time (3 runs):
     * Run 1: P.PP seconds
     * Run 2: P.QQ seconds
     * Average: P.PP seconds
   - Sample output (5 rows) or image of the output
   - GitHub link: src/compute/dataproc_pig.pig

Page 9: Raw Benchmark Results
   - Execution time summary table
   - Query output validation (all three produce same results)
   - Terminal screenshots with timestamps
   - Any anomalies or exceptions documented
```

# NOTE: Can also use information from Yarn

#### Presentation (1.5 min)
- Show 3 code snippets (30 sec each)
- "Identical query, 3 different tools"
- Raw execution times (results analysis by Person 7)

#### Deliverables:
```
src/compute/
├── dataproc_spark.py              [PySpark code]
├── dataproc_hive.hql              [HiveQL script]
├── dataproc_pig.pig               [Pig Latin script]
└── benchmark_logs/
    ├── spark_run1.log             [Execution log + time] if have
    ├── spark_run2.log
    ├── spark_run3.log
    ├── hive_run1.log
    ├── hive_run2.log
    ├── hive_run3.log
    ├── pig_run1.log
    ├── pig_run2.log
    └── pig_run3.log

Output (only one of the output below, the best tool):
├── gs://kaggle_gold_bucket/spark_results/
├── gs://kaggle_gold_bucket/hive_results/
└── gs://kaggle_gold_bucket/pig_results/

BigQuery Tables (only one of the output below, the best tool):
├── restaurant_gold_db.spark_benchmark_results
├── restaurant_gold_db.hive_benchmark_results
└── restaurant_gold_db.pig_benchmark_results
```

#### Can start: **After Person 4 completes cleaning** ⏳
#### Blocks: **Person 6 (Dashboard) + Person 7 (Results Analysis)** ⏳

---

### **PERSON 6 - Dashboard & Business Intelligence**
**Workload:** 🟡 **MEDIUM-HEAVY** (~18-22 hours)
**Independence:** ❌ **DEPENDS ON PERSON 5** (Gold results in BigQuery)
**Input:** BigQuery tables from Person 5
**Output:** Looker Studio dashboard

#### Technical Responsibilities:

**1. BigQuery Table Preparation** (5-8 hours)
- Create BigQuery dataset: `restaurant_gold_db`
- Create tables from Spark/Hive/Pig results
- Define schemas for optimal querying
- Ensure all three tool results loaded successfully

**2. Looker Studio Dashboard Creation**

A simple dashboard is sufficient

#### Example ideas:

**Dashboard 1: Restaurant Analytics**
- Top 10 restaurants by location & price range (table + bar chart)
- Rating distribution (histogram)
- Review count distribution (box plot)
- Geographic heatmap (if lat/long available)

**Dashboard 2: Booking Patterns**
- Daily booking volume by location (line chart)
- Price range distribution (pie chart)
- Cuisine type popularity (horizontal bar)
- Most popular restaurants (top 20 table)

**Dashboard 3: Benchmark Results** (optional, if space)
- Tool performance comparison (shared by Person 7 analysis)

#### Report (~1.5-2 pages)
```
Page 10: Business Intelligence Dashboards

Dashboard 1: Restaurant Analytics
  - Screenshot of dashboard
  - Top 3 findings:
    * Finding 1: [specific number from chart]
    * Finding 2: [specific trend]
    * Finding 3: [geographic insight]
  
Dashboard 2: Booking Patterns
  - Screenshot of dashboard
  - Top 3 findings:
    * Peak booking locations: Bangkok (X%), Singapore (Y%)
    * Price preference: X% prefer $$, Y% prefer $$$
    * Top cuisine type: [cuisine] with Z restaurants

Key Metrics Calculated:
  - Total restaurants: X
  - Total reviews: Y
  - Average rating: Z stars
  - Most common price range: $
```

#### Presentation (1 min)
- Screen shot Looker Studio

#### Deliverables:
```
Looker Studio (1 should be enough):
├── Dashboard 1: Restaurant Analytics (published link)
├── Dashboard 2: Booking Patterns (published link)
└── Dashboard 3: Benchmark Comparison (if created)
```

#### Can start: **After Person 5 loads results to BigQuery** ⏳
#### Blocks: **Nobody** ✅

---

### **PERSON 7 - Results Analysis & Tool Comparison**
**Workload:** 🟡 **MEDIUM-HEAVY** (~18-22 hours)
**Independence:** ❌ **DEPENDS ON PERSON 5** (Raw benchmark times)
**Input:** Execution times from Person 5's logs
**Output:** Performance comparison analysis, visualizations

#### Technical Responsibilities:

**1. Compile & Analyze Benchmark Data** (5-8 hours)
- Extract execution times from Person 5's logs/images (3 runs each tool)
- Calculate averages, standard deviations
- Create comparison table

**2. Performance Analysis & Visualization** (8-10 hours)
```
Create visualizations or table of comparison, a simple one is sufficient:
1. Execution Time Bar Chart
   - Y-axis: Seconds
   - X-axis: Tool (Spark, Hive, Pig)
   - Show average with error bars (min/max from 3 runs)

2. Memory Usage Comparison (if captured)
   - Peak RAM per tool
   - Average RAM per tool

3. Throughput Ranking (rows/sec)
   - Dataset size / execution time = throughput

4. Tool Selection Matrix
   - When to use each tool
   - Pros/cons comparison
```

**3. Comparative Insights** (5-6 hours)
- Why is Spark fastest? (DAG optimization, in-memory)
- Why is Hive moderate? (metastore overhead, Tez benefits)
- Why is Pig slowest? (MapReduce, disk I/O between phases)
- Tool selection recommendations

#### Report (~2 pages)
```
Page 11: Benchmark Results & Comparative Analysis

Raw Benchmark Results Table:
  | Tool | Run 1 | Run 2 | Run 3 | Average | Std Dev |
  | Spark | X.XX | X.YY | X.ZZ | X.XX | 0.05 |
  | Hive | A.AA | A.BB | A.CC | A.AA | 0.08 |
  | Pig | P.PP | P.QQ | P.RR | P.PP | 0.12 |

Performance Visualizations:
  - Execution Time Bar Chart (with error bars)
  - Memory Usage Comparison
  - Throughput Ranking (rows/sec)

Analysis & Findings:
  1. Spark Performance
     - Fastest: X.XX seconds (baseline)
     - Y% faster than Hive
     - Z% faster than Pig
     - Reason: DAG optimization, in-memory processing
     - Best for: Real-time analytics, iterative ML
  
  2. Hive Performance
     - Moderate: A.AA seconds
     - B% slower than Spark
     - C% faster than Pig
     - Reason: SQL query optimization, Tez improvements
     - Best for: Data warehouse, complex joins
  
  3. Pig Performance
     - Slowest: P.PP seconds
     - D% slower than Spark
     - E% slower than Hive
     - Reason: MapReduce model, disk I/O overhead
     - Best for: Complex multi-step ETL pipelines

Page 12: Tool Selection Matrix
  | Criteria | Spark | Hive | Pig |
  | Speed | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
  | SQL Familiarity | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
  | Memory Efficiency | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
  | Ease of Learning | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
  | Recommended Use | Real-time | Data Warehouse | Complex ETL |

Conclusion:
  - Winner for this dataset: Spark (X% faster than competitors)
  - Recommended tool selection by use case
  - Performance implications for future scaling
```

#### Presentation (1.5 min)
- Show execution time bar chart (30 sec)
- "Spark wins by X%, here's why" (45 sec)
- Tool selection matrix & recommendations (15 sec)

#### Deliverables:
```
analysis/
├── benchmark_results.csv          [Raw times from Person 5]
├── performance_analysis.xlsx      [Calculated metrics]
├── execution_time_chart.png       [Bar chart]
├── memory_comparison_chart.png    [Memory usage]
├── throughput_ranking_chart.png   [Rows/sec]
└── tool_selection_matrix.md       [Decision matrix]
```

#### Can start: **After Person 5 completes benchmark runs** ⏳
#### Blocks: **Nobody** ✅

---

### **PERSON 8 - Conclusion & Summary**
**Workload:** 🟢 **LIGHT** (~10-12 hours)
**Independence:** ❌ **DEPENDS ON ALL** (synthesis only)
**Input:** All completed reports from Persons 1-7
**Output:** Conclusion section, executive summary

#### Responsibilities:

**1. Project Summary** (4-5 hours)
- Recap entire project in 1-2 pages
- Key findings from each phase
- Business impact

**2. Conclusion & Insights** (4-5 hours)
- Main takeaways
- Tool selection recommendation
- Business intelligence discoveries
- Infrastructure validation

**3. Future Work & Recommendations** (2-3 hours)
- Suggestions for scaling
- Additional analyses
- Next phases

#### Report (~1-1.5 pages)
```
Page 13: Conclusion & Summary

Executive Summary:
  - Project objective recap (2-3 sentences)
  - High-level approach (medallion architecture)
  - Key findings summary (3-4 bullet points)

Key Findings:
  1. Data Pipeline
     - Successfully ingested X rows from Kaggle
     - Cleaned Y% duplicates, reduced null by Z%
  
  2. Apache Tools Comparison
     - Spark fastest at X.XX seconds
     - Hive moderate at A.AA seconds
     - Pig slowest at P.PP seconds
  
  3. Business Intelligence
     - Bangkok is top booking location
     - X% prefer mid-range pricing
     - Rating correlation with review count: Y%

Final Recommendations:
  - Use Spark for real-time analytics
  - Use Hive for SQL team with complex joins
  - Use Pig for complex ETL workflows
  - GCP infrastructure is scalable & production-ready

Future Work:
  1. Scale to multi-node Dataproc cluster
  2. Implement real-time streaming with Pub/Sub + Dataflow
  3. Extend analysis with machine learning predictions
  4. Build cost optimization dashboard

Conclusion:
  This project successfully demonstrated a production-grade big data pipeline
  on GCP, validated three Apache processing tools under controlled conditions,
  and extracted actionable business intelligence from tourism data. The findings
  enable architects to make informed tool selection decisions for their specific
  use cases.
```

#### Presentation (1 min)
- "In summary, we proved..." (project recap)
- "Winner: Spark, but choose based on your needs"
- "GCP + Apache is production-ready"

#### Deliverables:
```
reports/
├── conclusion.md                  [Conclusion section]
├── executive_summary.md           [1-page summary]
└── final_report.pdf               [Complete 10-page report]
```

#### Can start: **After most other people complete (last phase)** ⏳
#### Blocks: **Nobody** ✅

---

## **Complete Dependency Chain**

```
START
  ├─ Person 1 [Intro] → INDEPENDENT ✅
  ├─ Person 2 [Architecture] → INDEPENDENT ✅
  └─ Person 3 [IAM + Ingestion] → Bronze CSV
       ↓
       └─ Person 4 [Data Cleaning] → Silver CSV
            ↓
            └─ Person 5 [Apache Tools] → Gold results + Benchmark times
                 ├─ Person 6 [Dashboard] → Looker Studio
                 └─ Person 7 [Results Analysis] → Comparison charts
                      ↓
                      └─ Person 8 [Conclusion] → Final report
END
```

**Key Advantage:** Only 1 chain of dependencies!
- Person 1 & 2 work independently (no delays possible)
- Person 3 → 4 → 5 is linear (if one delays, only next waits)
- Person 6 & 7 both depend on Person 5 (can work in parallel)
- Person 8 waits for all (synthesis role)

---

## **Report Page Allocation (10 pages total)**

| Pages | Content | Person |
|-------|---------|--------|
| 1 | Abstract + Keywords | Person 1 |
| 1 | Introduction | Person 1 |
| 0.5 | Problem Statements | Person 1 |
| 0.5 | Architecture & Framework | Person 2 |
| 1 | IAM & Ingestion | Person 3 |
| 1 | Data Cleaning | Person 4 |
| 1 | Apache Tools Code | Person 5 |
| 1 | Raw Benchmark Results | Person 5 |
| 1.5 | Dashboard & BI | Person 6 |
| 1.5 | Results Analysis & Comparison | Person 7 |
| 1 | Conclusion & Recommendations | Person 8 |
| **10** | **TOTAL** | |

---

## **Presentation Slide Allocation (10 slides max)**

| Slide | Content | Speaker | Duration |
|-------|---------|---------|----------|
| 1 | Title Slide | Person 1 | 15 sec |
| 2 | Problem Statement | Person 1 | 30 sec |
| 3 | Architecture Diagram | Person 2 | 45 sec |
| 4 | IAM & Ingestion Flow | Person 3 | 1 min |
| 5 | Data Cleaning Results | Person 4 | 1 min |
| 6 | Apache Tools Code Comparison | Person 5 | 1.5 min |
| 7 | Dashboard Screenshots | Person 6 | 1 min |
| 8 | Benchmark Results Chart | Person 7 | 1 min |
| 9 | Tool Selection Matrix | Person 7 | 1 min |
| 10 | Conclusion & Recommendations | Person 8 | 1 min |
| | **TOTAL** | | **~10 min** |

---

## **Parallel vs. Sequential Work Timeline**

**Week 1-2:** Persons 1, 2 work independently
**Week 2-3:** Person 3 (IAM + Ingestion)
**Week 3-4:** Person 4 (Data Cleaning, waits for Person 3)
**Week 4-5:** Person 5 (Apache Tools, waits for Person 4) → Persons 6 & 7 start in parallel
**Week 5-6:** Person 6 & 7 finish (both waiting on Person 5)
**Week 6:** Person 8 (Conclusion, synthesis)
**Week 6:** Final report assembly & presentation practice

**No person should be blocked waiting** except as indicated above (linear chain).

---
