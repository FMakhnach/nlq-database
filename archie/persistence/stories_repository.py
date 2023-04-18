from archie.ml.embedder import get_embedding
from archie.persistence.elastic import es_client
from archie.persistence.entities import Story, StorySearchResult


def add_story(story: Story):
    story_doc = story.to_dict()
    story_doc['embedding'] = get_embedding(story.name)
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
                user_id=result['_source']['user_id'],
                name=result['_source']['name'],
                description=result['_source']['description'],
                prompt=result['_source']['prompt'],
                schema=result['_source']['schema'],
            ),
            score=result['_score']
        )
        for result in results
    ]
    return stories
