from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["salaries"]
collection = db["records"]

pipeline = [
    {"$group": {"_id": "$job_title", "avg_salary": {"$avg": "$salary_in_usd"}}},
    {"$sort": {"avg_salary": -1}},
    {"$limit": 5}
]

for doc in collection.aggregate(pipeline):
    print(doc)


cat > /spark/src/queries/es_query1.py << 'EOF'
from elasticsearch import Elasticsearch

es = Elasticsearch("http://elasticsearch:9200")

index_name = "salaries_clean"

query = {
    "query": {
        "match_all": {}
    },
    "size": 5
}

response = es.search(index=index_name, body=query)

for hit in response["hits"]["hits"]:
    print(hit["_source"])
EOF
