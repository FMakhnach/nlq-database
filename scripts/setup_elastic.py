from elasticsearch import Elasticsearch

NUMBER_OF_SHARDS = 1


def recreate_index(es: Elasticsearch, index: str, **kwargs):
    if es.indices.exists(index=index):
        es.indices.delete(index=index)
    es.indices.create(index=index, **kwargs)


def create_memories_index(es: Elasticsearch):
    settings = {
        "number_of_shards": NUMBER_OF_SHARDS,
    }
    mappings = {
        "properties": {
            "user_id": {"type": "text"},
            "is_users": {"type": "boolean"},
            "moment": {"type": "date"},
            "memory": {"type": "text"},
            "embedding": {
                "type": "dense_vector",
                "dims": 384,
                "index": True,
                "similarity": "dot_product"},
        }
    }
    recreate_index(es, index='memories', settings=settings, mappings=mappings)


def create_stories_index(es: Elasticsearch):
    settings = {
        "number_of_shards": NUMBER_OF_SHARDS,
    }
    mappings = {
        "properties": {
            "user_id": {"type": "text"},
            "name": {"type": "text"},
            "description": {"type": "text"},
            "prompt": {"type": "text"},
            "schema": {"type": "text"},
            "embedding": {
                "type": "dense_vector",
                "dims": 384,
                "index": True,
                "similarity": "dot_product"},
        }
    }
    recreate_index(es, index='stories', settings=settings, mappings=mappings)


def create_facts_index(es: Elasticsearch):
    settings = {
        "number_of_shards": NUMBER_OF_SHARDS,
    }
    mappings = {
        "properties": {
            "user_id": {"type": "text"},
            "story_name": {"type": "text"},
            "data": {"type": "object"},
        }
    }
    recreate_index(es, index='stories', settings=settings, mappings=mappings)


def create_indices():
    CERT_FINGERPRINT = "aa12b0203cdf7439af11fab9045b500b0ad6fc5ef41b1302e42d97543dd2f922"
    # Password for the 'elastic' user generated by Elasticsearch
    ELASTIC_PASSWORD = "z*b-*g9iIpvYgkSW9WN7"

    client = Elasticsearch(
        "https://localhost:9200",
        ssl_assert_fingerprint=CERT_FINGERPRINT,
        basic_auth=("elastic", ELASTIC_PASSWORD)
    )

    data = client.info()
    print(data)
    create_memories_index(client)
    create_stories_index(client)
    create_facts_index(client)


if __name__ == '__main__':
    create_indices()
