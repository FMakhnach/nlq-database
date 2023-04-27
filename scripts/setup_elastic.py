from archie.persistence.elastic import es_client as es

NUMBER_OF_SHARDS = 1


def recreate_index(index: str, **kwargs):
    if es.indices.exists(index=index):
        es.indices.delete(index=index)
    es.indices.create(index=index, **kwargs)


def create_memories_index():
    settings = {
        "number_of_shards": NUMBER_OF_SHARDS,
    }
    mappings = {
        "properties": {
            "conversation_id": {"type": "text"},
            "is_user_message": {"type": "boolean"},
            "moment": {"type": "date"},
            "message": {"type": "text"},
            "embedding": {
                "type": "dense_vector",
                "dims": 384,
                "index": True,
                "similarity": "dot_product"},
        }
    }
    recreate_index(es, index='memories', settings=settings, mappings=mappings)


def create_stories_index():
    settings = {
        "number_of_shards": NUMBER_OF_SHARDS,
    }
    mappings = {
        "properties": {
            "conversation_id": {"type": "text"},
            "key": {"type": "text"},
            "reference": {"type": "text"},
            "message": {"type": "text"},
            "schema": {"type": "text"},
            "embedding": {
                "type": "dense_vector",
                "dims": 384,
                "index": True,
                "similarity": "dot_product"},
        }
    }
    recreate_index(index='stories', settings=settings, mappings=mappings)


def create_facts_index():
    settings = {
        "number_of_shards": NUMBER_OF_SHARDS,
    }
    mappings = {
        "properties": {
            "conversation_id": {"type": "text"},
            "story_key": {"type": "text"},
            "data": {"type": "object"},
        }
    }
    recreate_index(index='facts', settings=settings, mappings=mappings)


def create_openai_calls_logs_index():
    settings = {
        "number_of_shards": NUMBER_OF_SHARDS,
    }
    mappings = {
        "properties": {
            "params": {"type": "object"},
            "response": {"type": "text"},
        }
    }
    recreate_index(index='openai_logs', settings=settings, mappings=mappings)

def create_openai_calls_logs2_index():
    settings = {
        "number_of_shards": NUMBER_OF_SHARDS,
    }
    mappings = {
        "properties": {
            "params": {"type": "object"},
            "response": {"type": "text"},
        }
    }
    recreate_index(index='openai_logs2', settings=settings, mappings=mappings)


def create_indices():
    data = es.info()
    print(data)
    # create_memories_index()
    # create_stories_index()
    # create_facts_index()
    # create_openai_calls_logs_index()
    create_openai_calls_logs2_index()


if __name__ == '__main__':
    create_indices()
