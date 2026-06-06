from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["salaries"]
collection = db["records"]

result = list(collection.find().limit(5))
for doc in result:
    print(doc)
