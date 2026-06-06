from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["salaries"]
collection = db["records"]

pipeline = [
    {"$group": {"_id": "$job_title", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}},
    {"$limit": 5}
]

result = list(collection.aggregate(pipeline))
for doc in result:
    print(doc)
