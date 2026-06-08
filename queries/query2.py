from pymongo import MongoClient

client = MongoClient("mongodb://mongodb:27017/")
db = client["salaries"]
collection = db["records"]

pipeline = [
    {"$sort": {"salary_in_usd": -1}},
    {"$limit": 10}
]

results = collection.aggregate(pipeline)

for doc in results:
    print(doc)

from elasticsearch import Elasticsearch

es = Elasticsearch("http://elasticsearch:9200")

index_name = "salaries_clean"

query = {
    "query": {
        "term": {
            "experience_level.keyword": "Senior"
        }
    },
    "size": 5
}

response = es.search(index=index_name, body=query)

for hit in response["hits"]["hits"]:
    print(hit["_source"])
