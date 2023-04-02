from elasticsearch import Elasticsearch
from embedder import get_embedding
from models import Story, StorySearchResult, Fact

CERT_FINGERPRINT = "aa12b0203cdf7439af11fab9045b500b0ad6fc5ef41b1302e42d97543dd2f922"
ELASTIC_PASSWORD = "z*b-*g9iIpvYgkSW9WN7"

es_client = Elasticsearch(
    "https://localhost:9200",
    ssl_assert_fingerprint=CERT_FINGERPRINT,
    basic_auth=("elastic", ELASTIC_PASSWORD)
)


def add_story(story: Story):
    story_doc = story.to_dict()
    story_doc['embedding'] = get_embedding(story.prompt)
    es_client.index(index='stories', document=story_doc)


def search_relevant_stories(user_id: str or int, prompt: str, threshold: float) -> list[StorySearchResult]:
    prompt_embedding = get_embedding(prompt)
    es_query = {
        "query": {
            "bool": {
                "must": {
                    "match": {"user_id": str(user_id)}
                },
            }
        },
        "min_score": threshold,
        "size": 1,
        "knn": {
            "field": "embedding",
            "query_vector": prompt_embedding,
            "k": 10,
            "num_candidates": 100,
        },
    }
    results = es_client.search(index="stories", body=es_query)["hits"]["hits"]
    stories = [
        StorySearchResult(
            Story(
                story_name=result['_source']['story_name'],
                user_id=result['_source']['user_id'],
                prompt=result['_source']['prompt'],
                fact_schema=result['_source']['fact_schema'],
            ),
            score=result['_score']
        )
        for result in results
    ]
    return stories


def add_fact(fact: Fact):
    es_client.index(index='facts', document=fact.to_dict())


def search_facts(query: dict):
    return es_client.search(index='facts', body=query)["hits"]["hits"]
