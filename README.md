# 1261-Project

import pymongo

client = pymongo.MongoClient("mongodb://localhost:27017")
db = client["climate"]
collection = db["raw_temperatures"]

result = collection.find().limit(5)
for r in result:
    print(r)
