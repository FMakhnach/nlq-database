from datetime import datetime

from archie.models import ConversationId
from archie.ml.embedder import get_embedding
from archie.persistence.elastic import es_client
from archie.persistence.entities import MemoryEntity, MemorySearchResult


def add_memory(memory: MemoryEntity) -> None:
    memory_doc = memory.to_dict()
    memory_doc['embedding'] = get_embedding(memory.message)
    es_client.index(index='memories', document=memory_doc)


def get_last_memories(conversation_id: ConversationId, limit: int = 4) -> list[MemoryEntity]:
    es_query = {
        "size": limit,
        "sort": [{"moment": {"order": "desc"}}],
        "query": {
            "bool": {
                "must": [
                    {"term": {"conversation_id": conversation_id.value}},
                ]
            }
        }
    }
    results = es_client.search(index="memories", body=es_query)["hits"]["hits"]
    memories = [
        to_memory(result['_source'])
        for result in results
    ]
    return memories


def search_relevant_memories(
        conversation_id: ConversationId,
        reference_text: str,
        threshold: float = 0.3,
        limit: int = 5
) -> list[MemorySearchResult]:
    reference_embedding = get_embedding(reference_text)
    es_query = {
        "query": {
            "bool": {
                "must": [
                    {"term": {"is_user_message": True}},
                    {"match": {"conversation_id": conversation_id.value}}
                ]
            }
        },
        "min_score": threshold,
        "size": limit,
        "knn": {
            "field": "embedding",
            "query_vector": reference_embedding,
            "k": 10,
            "num_candidates": 100,
        },
    }
    results = es_client.search(index="memories", body=es_query)["hits"]["hits"]
    memories = [
        MemorySearchResult(
            to_memory(result['_source']),
            score=result['_score']
        )
        for result in results
    ]
    return memories


def to_memory(source: dict) -> MemoryEntity:
    return MemoryEntity(
        conversation_id=source['conversation_id'],
        is_user_message=bool(source['is_user_message']),
        moment=datetime.fromisoformat(source['moment']),
        message=source['message'],
    )
