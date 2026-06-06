from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["salaries"]
collection = db["records"]

query = {"remote_ratio": 100}

result = list(collection.find(query).limit(5))
for doc in result:
    print(doc)
