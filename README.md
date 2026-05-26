export PROJECT_ID="bigdatamanagement-497302"
export REGION="asia-southeast1" # Set to Singapore
export BRONZE_BUCKET="kaggle_bronze_bucket"
export SILVER_BUCKET="kaggle_silver_bucket"
export SA_NAME="921953242742-compute"
export SERVICE_ACCOUNT_EMAIL="${SA_NAME}@developer.gserviceaccount.com"

gcloud services enable storage.googleapis.com\
secretmanager.googleapis.com \
cloudfunctions.googleapis.com \
cloudbuild.googleapis.com \
run.googleapis.com \
logging.googleapis.com

# Assign permissions across storage, secrets, and dataproc components
for ROLE in storage.admin secretmanager.secretAccessor dataproc.editor metastore.editor bigquery.admin; do \
  gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
    --role="roles/${ROLE}"; \
done

gcloud functions deploy ingestion_kaggle --runtime python310 --trigger-http --allow-unauthenticated --region ${REGION} --source ./cloudfunction_scripts --set-env-vars PROJECT_ID=${PROJECT_ID},BUCKET=${BUCKET} --timeout=540s --memory=1024MB

curl -X POST "https://asia-southeast1-bigdatamanagement-497302.cloudfunctions.net/ingestion_kaggle" \
-H "Authorization: bearer $(gcloud auth print-identity-token)" \
-H "Content-Type: application/json" \
-d '{
  "name": "Developer"
}'

after the csv land in bronze bucket

enable dataprep (alteryx trifacta (new name))

do data cleaning of the dataset

u could also use ui for this in dataproc (managed apache spark) choose metastore and create metastore (developer tier)

gcloud services enable metastore.googleapis.com

create dataproc cluster (i suggest use ui)

region asia-southeast-1

 Put cluster name
 region asia-southeast-1
4 vcpu 32gb memory
pick pig/jupyter server

then go to the web interface.
launch pyspark

write ur pyspark code.

additional permission if require to write to bigquery or gcs

# Set your project context
gcloud config set project bigdatamanagement-497302

# Give BigQuery Admin access to your default Compute Engine account just to be safe
COMPUTE_SVC_ACCOUNT="$(gcloud projects get-iam-policy bigdatamanagement-497302 --format="value(bindings.role)" | grep -o '[0-9]*\-compute@developer\.gserviceaccount\.com' | head -n 1)"

gcloud projects add-iam-policy-binding bigdatamanagement-497302 \
    --member="serviceAccount:${COMPUTE_SVC_ACCOUNT}" \
    --role="roles/bigquery.admin"


turn on the dataproc cluster and turn off if done with the task to save money.

create a pyspark notebook, write the code.
if received this error
26/05/26 02:54:06 WARN YarnScheduler: Initial job has not accepted any resources; check your cluster UI to ensure that workers are registered and have sufficient resources 

meaning its out of memory due to too many kernel is running in the background click the kernel and stop all kernel.

run hive and pig in terminal dont run it in the ipynb, theres a bug if u run it in ipynb

pricing website
https://cloud.google.com/products/compute/pricing/general-purpose?hl=en

e2-highmem-4 -cheapest for 32gb memory (out of memory issue should be fixed with this)

4 vcpu

32 GiB ram

$0.22302732 / 1 hour


hive still has out of memory issue due to how the node behave.

so we need to use terminal

Step 1: Create and open the file using a text editor
Since you are in a terminal, the easiest built-in text editor to use is nano. Type this command and press Enter:

Bash
nano tripadvisor_benchmark.hql
Step 2: Paste your script
Your terminal will change into a basic text editor screen. Paste your entire Hive script inside.

SQL
-- Set local directories and memory limits
SET hive.exec.scratchdir=/tmp/hive/scratch;
SET hive.metastore.warehouse.dir=/tmp/hive/warehouse;
SET hive.query.results.cache.enabled=false;
SET tez.am.resource.memory.mb=2048;
SET hive.tez.container.size=2048;

CREATE DATABASE IF NOT EXISTS ta_final_db;
USE ta_final_db;

DROP TABLE IF EXISTS tripadvisor_clean_table;

CREATE EXTERNAL TABLE tripadvisor_clean_table (
    name STRING, street_address STRING, location STRING, type STRING,
    reviews STRING, no_of_reviews STRING, comments STRING, contact_number STRING,
    trip_advisor_url STRING, menu STRING, price_range STRING
) ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' 
STORED AS TEXTFILE
LOCATION 'gs://kaggle_bronze_bucket/tripadvisor_raw/';

SELECT location, type, price_range, COUNT(name) as total_restaurants
FROM tripadvisor_clean_table
WHERE location IS NOT NULL AND location != 'location'
GROUP BY location, type, price_range
ORDER BY total_restaurants DESC
LIMIT 5;
Step 3: Save and Exit
To save the file in nano, use these exact keyboard shortcuts:

Press Ctrl + O (the letter O, to "Write Out" or save).

Press Enter to confirm the file name.

Press Ctrl + X to exit the editor and return to the normal command line.

Step 4: Execute the file with a timer
Now that the file is permanently saved on your master node's hard drive, you can run it as many times as you want without opening it again. To run it and get your final benchmark time, paste this execution block:

Bash
start_time=$(date +%s)

hive -f tripadvisor_benchmark.hql

end_time=$(date +%s)
echo "--------------------------------------------------------"
echo "⏱️ PURE STANDALONE APACHE HIVE RUNTIME: $((end_time - start_time)) SECONDS"
echo "--------------------------------------------------------"


Step 1: Create the Pig Script File
In that same black SSH terminal window, use nano to create your new Pig file:

Bash
nano tripadvisor_benchmark.pig
Step 2: Paste the Pig Latin Code
Paste this complete pipeline into the editor. Notice how Pig looks much more like a sequential programming script than SQL.

Code snippet
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
Step 3: Save and Exit
Just like before:

Press Ctrl + O (the letter O) to save.

Press Enter to confirm.

Press Ctrl + X to exit back to the command line.

Step 4: Execute and Time the Run
Now, run the script using the native pig binary wrapper. Paste this block to get your final, objective benchmark metric:

Bash
start_time=$(date +%s)

pig -useHCatalog tripadvisor_benchmark.pig

end_time=$(date +%s)
echo "--------------------------------------------------------"
echo "⏱️ PURE STANDALONE APACHE PIG RUNTIME: $((end_time - start_time)) SECONDS"
echo "--------------------------------------------------------"


IAM role for team members
Need access to bigquery, gcs, dataproc (start and stop cluster). i want to test whether we use pyspark, hive, pig earlier that we tested with main acc.
access to looker studio

BIgquery Data viewer
Bigquery job user
Bigquery data editor

storage object viewer
storage object admin

dataproc editor

now data studio (old name is looker studio) to do report