from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer


def setup(es):
    settings = {
        "number_of_shards": 1,
    }
    mappings = {
        "properties": {
            "embedding": {
                "type": "dense_vector",
                "dims": 384,
                "index": True,
                "similarity": "cosine"},
            "category": {"type": "text"},
            "message": {"type": "text"},
            "schema": {"type": "text"},
        }
    }

    es.indices.create(index='schemas', settings=settings, mappings=mappings)
    es.indices.create(index='facts')


def setup2(es):
    settings = {
        "number_of_shards": 1,
    }
    mappings = {
        "properties": {
            "embedding": {
                "type": "dense_vector",
                "dims": 384,
                "index": True,
                "similarity": "cosine"},
            "category": {"type": "text"},
            "data_schema": {"type": "text"},
            "statement": {"type": "text"},
            "user_id": {"type": "text"},
        }
    }

    es.indices.create(index='schemas', settings=settings, mappings=mappings)


def insert(es: Elasticsearch, encoder, prompt):
    embedding = encoder.encode(prompt)
    es.index(index='test', document={
        'embedding': embedding,
        'message': prompt,
        'category': 'appointment',
        'schema': """
type: object
properties:
  description:
    type: string
  datetime:
    type: string
    format: date-time
required:
  - description
  - datetime
"""
    })


def insert2(es: Elasticsearch):
    es.index(index='test', document={
        'user_id': 123,
        'message': "trololo"
    })


def query(es, encoder, prompt):
    input_vector = encoder.encode(prompt)

    es_query = {
        "query": {
            "bool": {
                "must": {
                    "match": {"user_id": 123}
                }
            }
        },
        "size": 5,
        "knn": {
            "field": "embedding",
            "query_vector": input_vector,
            "k": 10,
            "num_candidates": 100,
        },
    }
    for result in es.search(
            index="test", body=es_query
    )["hits"]["hits"]:
        print(result)


def query2(es):
    es_query = {
        "query": {
            "bool": {
                "must": {
                    "match": {"user_id": 123}
                }
            }
        },
        "size": 5,
        "knn": {
            "field": "message",
            "query": "lala",
            "k": 10,
            "num_candidates": 100,
        },
    }
    for result in es.search(
            index="test", body=es_query
    )["hits"]["hits"]:
        print(result)


def match_all(es):
    es_query = {
        "query": {
            "match_all": {}
        },
    }
    for result in es.search(index="schemas", body=es_query
    )["hits"]["hits"]:
        print(result)


embedder = SentenceTransformer('all-MiniLM-L6-v2')

CERT_FINGERPRINT = "aa12b0203cdf7439af11fab9045b500b0ad6fc5ef41b1302e42d97543dd2f922"

# Password for the 'elastic' user generated by Elasticsearch
ELASTIC_PASSWORD = "z*b-*g9iIpvYgkSW9WN7"

client = Elasticsearch(
    "https://localhost:9200",
    ssl_assert_fingerprint=CERT_FINGERPRINT,
    basic_auth=("elastic", ELASTIC_PASSWORD)
)

# Successful response!
data = client.info()
print(data)

# setup(client)
# insert(client, embedder, "I've just washed bed linen.")
# insert(client, embedder, "I need to buy apples, milk, tomatoes and eggs. Write it down.")
# insert2(client)
# query2(client)
# match_all(client)
#setup(client)


mappings = {
    "properties": {
        "user_id": {"type": "text"},
        "category": {"type": "text"},
        "data": {"type": "object"},
    }
}

client.indices.put_mapping(mappings)
