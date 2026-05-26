import os
import json
import logging
import pandas as pd
import kagglehub
from flask import Flask, jsonify, request
from google.cloud import storage, secretmanager

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)


def load_kaggle_credentials():
    project_id = os.getenv("PROJECT_ID")
    if not project_id:
        raise ValueError("PROJECT_ID environment variable is not set")

    logger.info("Accessing Secret Manager for Kaggle credentials...")
    client = secretmanager.SecretManagerServiceClient()
    secret_name = f"projects/{project_id}/secrets/kaggle-json/versions/latest"
    logger.info(f"Secret path: {secret_name}")

    response = client.access_secret_version(name=secret_name)
    creds = json.loads(response.payload.data.decode("UTF-8"))
    logger.info("Successfully retrieved Kaggle credentials from Secret Manager")

    os.environ["KAGGLE_USERNAME"] = creds["username"]
    os.environ["KAGGLE_KEY"] = creds["key"]
    logger.info("Kaggle environment variables set successfully")


@app.route("/ingest", methods=["POST", "GET"])
def ingestion_kaggle(request=None):
    try:
        project_id = os.getenv("PROJECT_ID")
        bronze_bucket = os.getenv("BRONZE_BUCKET")
        logger.info(f"Starting ingestion — Project: {project_id}, Bronze Bucket: {bronze_bucket}")

        if not project_id:
            logger.error("PROJECT_ID environment variable is not set")
            return jsonify({"error": "PROJECT_ID environment variable is not set"}), 500
        if not bronze_bucket:
            logger.error("BRONZE_BUCKET environment variable is not set")
            return jsonify({"error": "BRONZE_BUCKET environment variable is not set"}), 500

        load_kaggle_credentials()
        logger.info("Kaggle credentials loaded successfully from Secret Manager")

        logger.info("Downloading TripAdvisor dataset via kagglehub...")
        download_path = kagglehub.dataset_download(
            "siddharthmandgi/tripadvisor-restaurant-recommendation-data-usa"
        )
        logger.info(f"Dataset downloaded successfully to: {download_path}")

        csv_files = [f for f in os.listdir(download_path) if f.endswith(".csv")]
        if not csv_files:
            raise FileNotFoundError(f"No CSV files found in {download_path}")
        csv_file = csv_files[0]
        local_csv_path = os.path.join(download_path, csv_file)
        logger.info(f"Found CSV file: {local_csv_path}")

        df = pd.read_csv(local_csv_path)
        logger.info(f"Loaded CSV into DataFrame — Shape: {df.shape}, Columns: {list(df.columns)}")

        logger.info("Standardizing column names (lowercase, spaces/hyphens to underscores)...")
        original_cols = list(df.columns)
        df.columns = [col.lower().replace(" ", "_").replace("-", "_") for col in df.columns]
        logger.info(f"Column rename complete — {len(original_cols)} columns processed")

        modified_local_path = "/tmp/bronze_tripadvisor.csv"
        df.to_csv(modified_local_path, index=False)
        logger.info(f"Standardized dataset saved locally to: {modified_local_path}")

        logger.info(f"Uploading to GCS Bronze layer — bucket: {bronze_bucket}")
        storage_client = storage.Client()
        bucket = storage_client.bucket(bronze_bucket)
        blob = bucket.blob("bronze_tripadvisor.csv")
        blob.upload_from_filename(modified_local_path)
        logger.info(f"Upload complete — gs://{bronze_bucket}/tripadvisor_raw/bronze_tripadvisor.csv")

        logger.info("Ingestion pipeline completed successfully")
        return jsonify({
            "status": "success",
            "layer": "Bronze Landing",
            "destination": f"gs://{bronze_bucket}/bronze_tripadvisor.csv",
            "row_count": int(df.shape[0]),
            "column_count": int(df.shape[1]),
        }), 200

    except Exception as e:
        logger.error(f"Unexpected ingestion error: {e}", exc_info=True)
        return jsonify({"error": f"Unexpected error: {e}"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"Starting Flask server on 0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port)
