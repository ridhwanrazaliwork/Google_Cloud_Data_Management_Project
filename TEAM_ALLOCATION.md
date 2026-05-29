# Team Task Allocation - 8 People (Minimal Dependencies)

## Dependency Map Analysis - UPDATED
```
Person 1 (Intro) → [INDEPENDENT]
Person 2 (Architecture) → [INDEPENDENT]
Person 3 (IAM + Ingestion) → Produces: Bronze CSV in GCS
Person 4 (Data Cleaning) → Depends on: Person 3 ✓ (clear input/output)
Person 5 (Apache Tools) → Depends on: Person 4 ✓ (benchmarking ONLY, NO writes)
Person 6 (Dashboard) → [INDEPENDENT FROM PERSON 5] ✓ reads Silver bucket directly
Person 7 (Results Analysis) → Depends on: Person 5 ✓ (uses benchmark metrics)
Person 8 (Conclusion) → Depends on: All completed ✓ (synthesis only)
```

**KEY CHANGE:** 
- ✅ Person 5 NO LONGER writes to BigQuery or GCS Gold bucket
- ✅ Person 5 only benchmarks, records metrics, saves terminal logs locally
- ✅ Person 6 reads Silver CSV directly (can use GCS or load to BigQuery independently)
- ✅ **Person 6 & Person 5 are NOW INDEPENDENT** - if Person 5 delays, Person 6 is NOT affected

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
  - Gold layer (curated/aggregated data - handled by dashboard)
  - Visual diagram

Page 3.5-4: GCP Service Stack
  - Cloud Run (ingestion)
  - Cloud Storage (landing zones)
  - Dataproc (compute - no direct writes to gold)
  - BigQuery (warehouse - optional, for dashboard)
  - Looker Studio (BI)
  - Diagram showing all services
```

#### Presentation (1 min)
- Show 3-layer architecture
- Explain each layer purpose
- Show GCP service relationships

#### Can start: **Immediately** ✅
#### Blocks: **Nobody** ✅

---

### **PERSON 3 (RIDHWAN) - IAM, Access Management & Ingestion**
**Workload:** 🔴 **VERY HEAVY** (~40-50 hours)
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
  - Roles assigned
  - Team member access credentials
  - Security best practices

Page 5.5-6: Data Ingestion Pipeline
  - Cloud Run Flask app architecture
  - Secret Manager integration
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

#### Can start: **Immediately** ✅
#### Blocks: **Person 4 (Data Cleaning)** ⏳

---

### **PERSON 4 - Data Cleaning (Cloud Dataprep)**
**Workload:** 🟡 **MEDIUM** (~15-20 hours)
**Independence:** ❌ **DEPENDS ON PERSON 3** (Bronze CSV)
**Input:** `gs://kaggle_bronze_bucket/bronze_tripadvisor.csv`
**Output:** `gs://kaggle_silver_bucket/tripadvisor_clean.csv`

#### Technical Responsibilities:

**1. Cloud Dataprep Setup & Configuration** (3-5 hours)
- Create Dataprep flow
- Connect to GCS Bronze bucket
- Load bronze_tripadvisor.csv

**2. Create Data Quality Recipes** (8-12 hours)
```
Recipe 1: Deduplication
Recipe 2: Null Handling
Recipe 3: Type Casting
Recipe 4: Structural Cleaning
```

**3. Execute Recipes & Validate Output** (3-5 hours)
- Run Dataprep recipes to completion
- Output to GCS Silver bucket
- Generate data quality report
- Record before/after metrics

#### Report (~1.5 pages)
```
Page 7: Data Cleaning & Quality Engineering
  - Raw data challenges
  - Dataprep recipe overview
  - Before/After Comparison Table
  - Sample clean data
  - Output location: gs://kaggle_silver_bucket/tripadvisor_clean.csv
```

#### Presentation (1 min)
- Show Dataprep UI screenshot
- "Raw data: X% duplicates, Y% nulls"
- "After cleaning: Z% improvement"
- Before/after bar chart

#### Can start: **After Person 3 completes ingestion** ⏳
#### Blocks: **Person 5 + Person 6** ⏳

---

### **PERSON 5 - Apache Tools Benchmarking (Spark, Hive, Pig) - BENCHMARKING ONLY**
**Workload:** 🔴 **VERY HEAVY** (~40-50 hours)
**Independence:** ❌ **DEPENDS ON PERSON 4** (Silver CSV)
**Input:** `gs://kaggle_silver_bucket/tripadvisor_clean.csv`
**Output:** Benchmark metrics, execution times, terminal logs (LOCAL FILES ONLY)

**CRITICAL CHANGE:** Person 5 does NOT write results to BigQuery or GCS Gold bucket.
Only record metrics and save terminal output logs locally.

#### Technical Responsibilities:

**1. PySpark Implementation** (12-15 hours)
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

start_spark = time.time()

# Load Silver data
df = spark.read.csv("gs://kaggle_silver_bucket/tripadvisor_clean.csv", 
                    header=True, inferSchema=True)

# Execute benchmark query
result = df.filter(col("location").isNotNull()) \
           .groupBy("location", "type", "price_range") \
           .agg(count("name").alias("total_restaurants")) \
           .sort(col("total_restaurants").desc()) \
           .limit(5)

result.show()

# ONLY save locally for logging
result.coalesce(1).write.mode("overwrite").csv("/tmp/spark_output")

end_spark = time.time()
spark_time = end_spark - start_spark

print("=" * 60)
print(f"SPARK EXECUTION TIME: {spark_time:.2f} seconds")
print("=" * 60)

spark.stop()
```

**2. HiveQL Implementation** (12-15 hours)
```sql
-- src/compute/dataproc_hive.hql
CREATE EXTERNAL TABLE tripadvisor_clean_table (...)
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

**3. Pig Latin Implementation** (12-15 hours)
```pig
-- src/compute/dataproc_pig.pig
tripadvisor = LOAD 'gs://kaggle_silver_bucket/tripadvisor_clean.csv' ...
filtered = FILTER tripadvisor BY location IS NOT NULL ...
grouped = GROUP filtered BY (location, type, price_range) ...
counted = FOREACH grouped GENERATE ...
sorted = ORDER counted BY total_restaurants DESC ...
STORE limited INTO '/tmp/pig_output';
```

**4. Execution, Timing & Logging** (8-10 hours)
- Run each tool 2-3 times on Dataproc cluster
- Record execution times
- Use `time` command:
```bash
start_time=$(date +%s)
spark-submit dataproc_spark.py > /tmp/spark_run1.log 2>&1
end_time=$(date +%s)
echo "Runtime: $((end_time - start_time)) seconds" >> /tmp/spark_run1.log
```
- Screenshot output logs
- Save ALL logs locally (not to BigQuery/GCS)

#### Report (~1.5-2 pages)
```
Page 8: Apache Tools Implementation

1. PySpark Implementation
   - Code architecture
   - DAG evaluation model
   - Execution times (3 runs): X.XX, X.YY, X.ZZ seconds
   - Sample output
   - GitHub link

2. HiveQL Implementation
   - External table definition
   - Query structure
   - Execution times: A.AA, A.BB, A.CC seconds
   - Sample output

3. Pig Latin Implementation
   - Dataflow script structure
   - Execution times: P.PP, P.QQ, P.RR seconds
   - Sample output

Page 9: Raw Benchmark Results
   - Execution time summary table
   - Query output validation
   - Terminal screenshots
```

#### Presentation (1.5 min)
- Show 3 code snippets (30 sec each)
- "Identical query, 3 different tools"
- Raw execution times (analysis by Person 7)

#### Deliverables:
```
src/compute/
├── dataproc_spark.py              [PySpark code]
├── dataproc_hive.hql              [HiveQL script]
├── dataproc_pig.pig               [Pig Latin script]
└── benchmark_logs/
    ├── spark_run1.log             [Local file]
    ├── spark_run2.log
    ├── spark_run3.log
    ├── hive_run1.log
    ├── hive_run2.log
    ├── hive_run3.log
    ├── pig_run1.log
    ├── pig_run2.log
    └── pig_run3.log

NO BigQuery writes
NO GCS Gold bucket writes
ONLY local benchmark logs
```

#### Can start: **After Person 4 completes cleaning** ⏳
#### Blocks: **Person 7 (Results Analysis) ONLY** ⏳
#### Does NOT block: **Person 6 (Dashboard)** ✅

---

### **PERSON 6 - Dashboard & Business Intelligence - NO DEPENDENCY ON PERSON 5**
**Workload:** 🟡 **MEDIUM-HEAVY** (~18-22 hours)
**Independence:** ❌ **DEPENDS ONLY ON PERSON 4** (Silver CSV)
**Input:** `gs://kaggle_silver_bucket/tripadvisor_clean.csv` (reads directly)
**Output:** Looker Studio dashboard

**KEY ADVANTAGE:** Person 6 is COMPLETELY INDEPENDENT from Person 5
- Reads Silver bucket directly (already cleaned by Person 4)
- Can load to BigQuery independently if desired
- If Person 5 is delayed, Person 6 is NOT affected ✅

#### Technical Responsibilities:

**Option A (Recommended - Simplest): Connect Looker Studio Directly to GCS**
- Create Looker Studio data source → GCS Silver CSV
- Build visualizations directly from CSV
- Fastest setup, no intermediate BigQuery needed

**Option B (If preferred): Load Silver to BigQuery First**
- Create BigQuery dataset: `restaurant_gold_db`
- Load Silver CSV to BigQuery table
- Connect Looker Studio to BigQuery
- More scalable, better for real-time queries

**Either way:** This is Person 6's choice, independent of Person 5

#### Dashboard Creation (10-14 hours)

**Dashboard 1: Restaurant Analytics**
- Top 10 restaurants by location & price range
- Rating distribution (histogram)
- Review count distribution
- Geographic heatmap (if lat/long available)

**Dashboard 2: Booking Patterns**
- Daily booking volume by location
- Price range distribution (pie chart)
- Cuisine type popularity
- Most popular restaurants (top 20)

#### Report (~1.5-2 pages)
```
Page 10: Business Intelligence Dashboards

Dashboard 1: Restaurant Analytics
  - Screenshot
  - Top 3 findings

Dashboard 2: Booking Patterns
  - Screenshot
  - Top 3 findings

Key Metrics:
  - Total restaurants: X
  - Total reviews: Y
  - Average rating: Z
  
Data Source: GCS Silver bucket (gs://kaggle_silver_bucket/tripadvisor_clean.csv)
or BigQuery (if loaded independently)
```

#### Presentation (1 min)
- Screen share Looker Studio
- Click 2-3 filters dynamically
- "Here's what hotel managers see"
- Point to 2-3 key business insights

#### Deliverables:
```
Looker Studio:
├── Dashboard 1: Restaurant Analytics (published link)
└── Dashboard 2: Booking Patterns (published link)

Optional BigQuery (if choosing Option B):
└── restaurant_gold_db.restaurants

Documentation:
└── dashboard_guide.md
```

#### Can start: **After Person 4 completes cleaning** ⏳
#### Blocks: **Nobody** ✅
#### Does NOT depend on: **Person 5** ✅

---

### **PERSON 7 - Results Analysis & Tool Comparison**
**Workload:** 🟡 **MEDIUM-HEAVY** (~18-22 hours)
**Independence:** ❌ **DEPENDS ON PERSON 5** (Raw benchmark times)
**Input:** Execution times from Person 5's terminal logs
**Output:** Performance comparison analysis, visualizations

#### Technical Responsibilities:

**1. Compile & Analyze Benchmark Data** (5-8 hours)
- Extract execution times from Person 5's logs
- Calculate averages, standard deviations
- Create comparison table

**2. Performance Analysis & Visualization** (8-10 hours)
```
Create visualizations:
1. Execution Time Bar Chart
2. Memory Usage Comparison (if captured)
3. Throughput Ranking (rows/sec)
4. Tool Selection Matrix
```

**3. Comparative Insights** (5-6 hours)
- Why is Spark fastest? (DAG optimization)
- Why is Hive moderate? (metastore overhead)
- Why is Pig slowest? (MapReduce, disk I/O)
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
  - Execution Time Bar Chart
  - Memory Usage Comparison
  - Throughput Ranking

Page 12: Tool Selection Matrix & Recommendations
  - When to use each tool
  - Performance implications
  - Scaling considerations
```

#### Presentation (1.5 min)
- Show execution time bar chart (30 sec)
- "Spark wins by X%, here's why" (45 sec)
- Tool selection matrix (15 sec)

#### Can start: **After Person 5 completes benchmark runs** ⏳
#### Blocks: **Nobody** ✅

---

### **PERSON 8 - Conclusion & Summary**
**Workload:** 🟢 **LIGHT** (~10-12 hours)
**Independence:** ❌ **DEPENDS ON ALL** (synthesis only)
**Input:** All completed reports from Persons 1-7
**Output:** Conclusion section, executive summary

#### Report (~1-1.5 pages)
```
Page 13: Conclusion & Summary

Executive Summary:
  - Project recap
  - High-level approach
  - Key findings (3-4 bullet points)

Key Findings:
  1. Data Pipeline: Ingested X rows, cleaned Y% duplicates
  2. Apache Tools: Spark fastest, Hive moderate, Pig slowest
  3. Business Intelligence: Top locations, pricing preferences

Final Recommendations:
  - Use Spark for real-time analytics
  - Use Hive for SQL team
  - Use Pig for complex ETL
  - GCP infrastructure is scalable

Future Work:
  1. Multi-node scaling tests
  2. Real-time streaming
  3. ML predictions
  4. Cost optimization
```

#### Can start: **After most people complete** ⏳
#### Blocks: **Nobody** ✅

---

## **UPDATED Dependency Chain - Person 5 & 6 NOW INDEPENDENT**

```
START
  ├─ Person 1 [Intro] → INDEPENDENT ✅
  ├─ Person 2 [Architecture] → INDEPENDENT ✅
  └─ Person 3 [IAM + Ingestion] → Bronze CSV
       ↓
       └─ Person 4 [Data Cleaning] → Silver CSV
            ├─ Person 5 [Apache Tools] → Benchmark metrics (local logs ONLY)
            │    └─ Person 7 [Results Analysis] → Comparison
            │
            └─ Person 6 [Dashboard] → Looker Studio (INDEPENDENT ✅)
                 
                 └─ Person 8 [Conclusion] → Final report
END
```

**KEY CHANGES:**
- ✅ Person 5 NO LONGER writes to BigQuery or Gold bucket
- ✅ Person 5 only benchmarks, records metrics, saves logs locally
- ✅ Person 6 reads Silver bucket DIRECTLY (can optionally load to BigQuery)
- ✅ **Person 6 & Person 5 are COMPLETELY INDEPENDENT**
- ✅ If Person 5 is delayed, Person 6 is NOT affected

---

## **Dependency Summary**

| Person | Depends On | Blocks | Can Parallel With |
|--------|-----------|--------|------------------|
| **1** | Nobody | Nobody | 2, 3 |
| **2** | Nobody | Nobody | 1, 3 |
| **3** | Nobody | 4 | 1, 2 |
| **4** | 3 | 5, 6 | - |
| **5** | 4 | 7 | 6 ✅ |
| **6** | 4 | Nobody | 5, 7 ✅ |
| **7** | 5 | Nobody | 6 |
| **8** | 1,2,3,4,5,6,7 | Nobody | - |

**IF PERSON 5 IS DELAYED:** Only Person 7 waits, NOT Person 6 ✅

---

## **Timeline**

**Week 1-2:** Persons 1, 2 work independently
**Week 2-3:** Person 3 (IAM + Ingestion)
**Week 3-4:** Person 4 (Data Cleaning)
**Week 4-5:** Persons 5 & 6 start in PARALLEL (independent of each other)
- Person 5: Benchmarking only
- Person 6: Dashboard from Silver bucket
**Week 5-6:** Person 7 (Results, waits on P5)
**Week 6:** Person 8 (Conclusion)

**Person 6 is no longer blocked by Person 5** ✅
