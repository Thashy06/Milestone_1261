"""
mongo_ingest.py
---------------
Reads the Berkeley Earth dataset from HDFS and loads it into MongoDB
with correct schema (dates, floats, strings). Fully logged and error-handled.
"""

import pandas as pd
from datetime import datetime
from hdfs import InsecureClient
from pymongo import MongoClient
from logging_config import get_logger
from config import (
    HDFS_URL,
    HDFS_USER,
    RAW_HDFS_DIR,
    MONGO_URI,
    MONGO_DB,
    MONGO_COLLECTION,
)

logger = get_logger("mongo_ingest")


def read_from_hdfs(filename: str) -> pd.DataFrame:
    """Read CSV file from HDFS into a Pandas DataFrame."""
    try:
        client = InsecureClient(HDFS_URL, user=HDFS_USER)
        hdfs_path = f"{RAW_HDFS_DIR}/{filename}"

        logger.info(f"Reading from HDFS: {hdfs_path}")

        with client.read(hdfs_path, encoding="utf-8") as reader:
            df = pd.read_csv(reader)

        logger.info(f"Loaded {len(df)} rows from HDFS")
        return df

    except Exception as e:
        logger.error(f"Failed to read from HDFS: {e}")
        raise


def clean_schema(df: pd.DataFrame) -> pd.DataFrame:
    """Convert columns to correct types for MongoDB."""
    logger.info("Cleaning schema and converting data types")

    try:
        df["dt"] = pd.to_datetime(df["dt"], errors="coerce")
        df["AverageTemperature"] = pd.to_numeric(df["AverageTemperature"], errors="coerce")
        df["AverageTemperatureUncertainty"] = pd.to_numeric(
            df["AverageTemperatureUncertainty"], errors="coerce"
        )

        logger.info("Schema conversion complete")
        return df

    except Exception as e:
        logger.error(f"Schema cleaning failed: {e}")
        raise


def insert_into_mongo(df: pd.DataFrame):
    """Insert cleaned DataFrame into MongoDB in batches."""
    try:
        logger.info("Connecting to MongoDB")
        client = MongoClient(MONGO_URI)
        collection = client[MONGO_DB][MONGO_COLLECTION]

        logger.info(f"Using DB: {MONGO_DB}, Collection: {MONGO_COLLECTION}")
        logger.info("Dropping existing collection (raw load)")
        collection.drop()

        records = df.to_dict("records")
        logger.info(f"Preparing to insert {len(records)} records in batches")

        batch_size = 50000
        for i in range(0, len(records), batch_size):
            batch = records[i:i+batch_size]
            collection.insert_many(batch, ordered=False)
            logger.info(f"Inserted batch {i//batch_size + 1}")

        logger.info("MongoDB ingestion complete")

    except Exception as e:
        logger.error(f"MongoDB ingestion failed: {e}")
        raise


# ⭐ THIS MUST BE ABOVE main() ⭐
def write_to_mongo(data):
    """Wrapper to insert list-of-dicts into MongoDB."""
    df = pd.DataFrame(data)
    df = clean_schema(df)
    insert_into_mongo(df)


def main():
    logger.info("=== Starting MongoDB ingestion ===")

    try:
        filename = "temperatures.csv"

        df = read_from_hdfs(filename)
        df = clean_schema(df)
        insert_into_mongo(df)

        logger.info("=== MongoDB ingestion completed successfully ===")

    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        logger.info("=== MongoDB ingestion terminated with errors ===")


if __name__ == "__main__":
    main()
