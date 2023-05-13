from datetime import datetime
from uuid import UUID

from talkql.models import ConversationId
from talkql.ml.embedder import get_embedding
from talkql.persistence.elastic import es_client
from talkql.persistence.elastic.indices import STORIES_INDEX as INDEX
from talkql.persistence.entities import StoryEntity, StorySearchResult


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
            "script_score": {
                "query": {
                    "match_all": {}
                    # "bool": {
                    #     "must": {
                    #         "match": {"conversation_id": conversation_id.value}
                    #     },
                    # },
                },
                "script": {
                    "source": f"cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                    "params": {
                        "query_vector": reference_embedding
                    }
                }
            }
        },
        "min_score": threshold,
        "size": 1,
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
