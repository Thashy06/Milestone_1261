import time
import requests
import pandas as pd
from pymongo import MongoClient
from elasticsearch import Elasticsearch
from hdfs import InsecureClient

# HDFS
hdfs_client = InsecureClient("http://namenode:9870", user="root")
print("Connected to HDFS")

# Wait for WebHDFS to be ready
for _ in range(10):
    try:
        requests.get("http://namenode:9870/webhdfs/v1/?op=LISTSTATUS", timeout=2)
        print("WebHDFS is ready")
        break
    except Exception:
        print("Waiting for WebHDFS to start...")
        time.sleep(2)
else:
    raise Exception("WebHDFS did not become ready")

# MongoDB
mongo_client = MongoClient("mongodb://mongodb:27017/")
db = mongo_client["salaries_db"]
collection = db["records"]
print("Connected to MongoDB")

# Elasticsearch
es = Elasticsearch("http://elasticsearch:9200")
print("Connected to Elasticsearch")

# Load CSV
df = pd.read_csv("ds_salaries.csv")
print(f"Loaded CSV with {len(df)} rows")

# Write to HDFS
with hdfs_client.write("/data/raw/ds_salaries.csv", overwrite=True) as writer:
    df.to_csv(writer, index=False)
print("Saved CSV to HDFS")

# Insert into MongoDB
records = df.to_dict(orient="records")
collection.insert_many(records)
print("Inserted into MongoDB")

# Index into Elasticsearch
for i, row in df.iterrows():
    es.index(index="salaries", id=i, document=row.to_dict())

print("Indexed into Elasticsearch")
print("Ingestion pipeline finished successfully")
