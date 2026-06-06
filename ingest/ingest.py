import pandas as pd
from pymongo import MongoClient
from elasticsearch import Elasticsearch
from hdfs import InsecureClient

# ---- HDFS ----
hdfs_client = InsecureClient("http://namenode:9870", user="root")
print("Connected to HDFS")

# ---- MongoDB ----
mongo_client = MongoClient("mongodb://mongodb:27017/")
db = mongo_client["salaries"]
collection = db["records"]
print("Connected to MongoDB")

# ---- Elasticsearch ----
es = Elasticsearch(["http://elasticsearch:9200"])
print("Connected to Elasticsearch")

# ---- Load CSV ----
df = pd.read_csv("/app/ds_salaries.csv")
print("Loaded CSV with", len(df), "rows")

# ---- Store raw CSV in HDFS ----
with hdfs_client.write("/data/raw/ds_salaries.csv", overwrite=True) as writer:
    df.to_csv(writer, index=False)
print("Saved CSV to HDFS")

# ---- Insert into MongoDB ----
records = df.to_dict(orient="records")
collection.insert_many(records)
print("Inserted into MongoDB")

# ---- Index into Elasticsearch ----
for i, row in df.iterrows():
    es.index(index="salaries", id=i, body=row.to_dict())

print("Indexed into Elasticsearch")

import time
import requests
# Wait for WebHDFS (port 9870) to be ready before writing
for i in range(10):
    try:
        # Try hitting WebHDFS LISTSTATUS endpoint
        requests.get("http://namenode:9870/webhdfs/v1/?op=LISTSTATUS", timeout=2)
        print("WebHDFS is ready")
        break
    except Exception:
        print("Waiting for WebHDFS to start...")
        time.sleep(2)
else:
    raise Exception("WebHDFS did not become ready after multiple attempts")

