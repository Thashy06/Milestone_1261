import requests
import io
import pandas as pd
from src.logging_config import get_logger

logger = get_logger("hdfs")

HDFS_HOST = "http://hadoop-namenode:9870"
HDFS_USER = "root"
HDFS_PATH = "/user/root/raw/temperatures.csv"


# ---------------------------------------------------------
# 1. UPLOAD DATAFRAME TO HDFS  (you already had this)
# ---------------------------------------------------------
def ingest_to_hdfs(df):
    """Upload DataFrame to HDFS using WebHDFS with manual redirect."""
    logger.info("Starting HDFS ingestion")

    try:
        # Convert DataFrame to CSV in memory
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_bytes = csv_buffer.getvalue().encode()

        # Step 1 - request upload (expect 307 redirect)
        init_url = (
            f"{HDFS_HOST}/webhdfs/v1{HDFS_PATH}?"
            f"op=CREATE&overwrite=true&user.name={HDFS_USER}"
        )

        init_res = requests.put(init_url, allow_redirects=False)

        if init_res.status_code != 307:
            raise Exception(f"Unexpected response: {init_res.status_code}")

        redirect_url = init_res.headers["Location"]

        # Step 2 - upload file to redirected URL
        upload_res = requests.put(redirect_url, data=csv_bytes)

        if upload_res.status_code not in (200, 201):
            raise Exception(f"Upload failed: {upload_res.text}")

        logger.info("Finished HDFS ingestion")

    except Exception as e:
        logger.error(f"HDFS ingestion failed: {e}")
        raise

def read_from_hdfs():
    """Download CSV from HDFS and return as list of dicts."""
    logger.info("Reading dataset from HDFS")

    try:
        read_url = (
            f"{HDFS_HOST}/webhdfs/v1{HDFS_PATH}?"
            f"op=OPEN&user.name={HDFS_USER}"
        )

        res = requests.get(read_url, allow_redirects=True)

        if res.status_code != 200:
            raise Exception(f"Failed to read file: {res.text}")

        # Convert CSV bytes → DataFrame
        df = pd.read_csv(io.StringIO(res.text))

        logger.info(f"Loaded {len(df)} rows from HDFS")

        return df.to_dict(orient="records")

    except Exception as e:
        logger.error(f"Failed to read from HDFS: {e}")
        raise

if __name__ == "__main__":
    logger.info("Loading dataset for ingestion")

    # Example: load your CSV from /app/data
    df = pd.read_csv("/app/data/GlobalLandTemperaturesByCity.csv")

    ingest_to_hdfs(df)

    logger.info("Ingestion complete")
