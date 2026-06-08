from pymongo import MongoClient
import csv

client = MongoClient("mongodb://mongodb:27017/")
db = client["salaries"]
collection = db["records"]

csv_path = "/app/data/ds_salaries.csv"

with open(csv_path, "r") as f:
    reader = csv.DictReader(f)
    docs = []
    for row in reader:
        row["salary_in_usd"] = float(row["salary_in_usd"])
        docs.append(row)

if docs:
    collection.insert_many(docs)

print("Inserted", len(docs), "documents")
