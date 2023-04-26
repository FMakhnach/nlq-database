from datetime import datetime

from archie.ml.embedder import get_embedding
from archie.persistence.elastic import es_client
from archie.persistence.entities import Memory, MemorySearchResult


def add_memory(memory: Memory) -> None:
    es_client.index(index='memories', document=memory.to_dict())


def get_last_memories(user_id: str, limit: int = 6) -> list[Memory]:
    es_query = {
        "size": limit,
        "sort": [{"moment": {"order": "desc"}}],
        "query": {
            "bool": {
                "must": [
                    {"term": {"user_id": user_id}},
                ]
            }
        }
    }
    results = es_client.search(index="memories", body=es_query)["hits"]["hits"]
    memories = [
        Memory(
            moment=datetime.fromisoformat(result['_source']['moment']),
            user_id=result['_source']['user_id'],
            is_users=bool(result['_source']['is_users']),
            memory=result['_source']['memory'],
        )
        for result in results
    ]
    return memories


def search_relevant_memories(
        user_id: str or int,
        prompt: str,
        threshold: float = 0.9,
        limit: int = 5
) -> list[MemorySearchResult]:
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
        "size": limit,
        "knn": {
            "field": "embedding",
            "query_vector": prompt_embedding,
            "k": 10,
            "num_candidates": 100,
        },
    }
    results = es_client.search(index="memories", body=es_query)["hits"]["hits"]
    memories = [
        MemorySearchResult(
            Memory(
                moment=datetime.fromisoformat(result['_source']['moment']),
                user_id=result['_source']['user_id'],
                is_users=bool(result['_source']['is_users']),
                memory=result['_source']['memory'],
            ),
            score=result['_score']
        )
        for result in results
    ]
    return memories
