from archie.models import ConversationId
from archie.ml.embedder import get_embedding
from archie.persistence.elastic import es_client
from archie.persistence.entities import Story, StorySearchResult


def add_story(story: Story):
    story_doc = story.to_dict()
    story_doc['embedding'] = get_embedding(story.key)
    es_client.index(index='stories', document=story_doc)


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
    results = es_client.search(index="stories", body=es_query)["hits"]["hits"]
    stories = [
        StorySearchResult(
            story=to_story(result['_source']),
            score=result['_score'],
        )
        for result in results
    ]
    return stories


def to_story(source: dict) -> Story:
    return Story(
        conversation_id=source['conversation_id'],
        key=source['key'],
        reference=source['reference'],
        message=source['message'],
        schema=source['schema'],
    )
