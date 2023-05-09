from datetime import datetime
from uuid import UUID

from archie.models import ConversationId
from archie.ml.embedder import get_embedding
from archie.persistence.elastic import es_client
from archie.persistence.elastic.indices import STORIES_INDEX as INDEX
from archie.persistence.entities import StoryEntity, StorySearchResult


def add_story(story: StoryEntity):
    story_doc = story.to_dict()
    story_doc['embedding'] = get_embedding(story.reference_text)
    es_client.index(index=INDEX, document=story_doc)


def search_relevant_stories(
        conversation_id: ConversationId,
        reference_text: str,
        threshold: float) -> list[StorySearchResult]:
    reference_embedding = get_embedding(reference_text)
    es_query = {
        "query": {
            "bool": {
                "must": {
                    "match": {"conversation_id": conversation_id.value}
                },
            }
        },
        "min_score": threshold,
        "size": 1,
        "knn": {
            "field": "embedding",
            "query_vector": reference_embedding,
            "k": 10,
            "num_candidates": 100,
        },
    }
    results = es_client.search(index=INDEX, body=es_query)["hits"]["hits"]
    stories = [
        StorySearchResult(
            story=to_story(result['_source']),
            score=result['_score'],
        )
        for result in results
    ]
    return stories


def to_story(source: dict) -> StoryEntity:
    return StoryEntity(
        id=UUID(source['id']),
        created_at=datetime.fromisoformat(source['created_at']),
        conversation_id=source['conversation_id'],
        reference_text=source['reference_text'],
        schema=source['schema'],
    )
