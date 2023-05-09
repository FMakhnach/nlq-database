from elasticsearch.helpers import reindex

from talkql.persistence.elastic import es_client as es
from talkql.persistence.elastic.indices import *

NUMBER_OF_SHARDS = 1
DEFAULT_SETTINGS = {
    "number_of_shards": NUMBER_OF_SHARDS,
}


def create_initial_index(name: str, mappings: dict):
    alias = name
    index_name = alias + '_v0'
    es.indices.create(index=index_name, settings=DEFAULT_SETTINGS, mappings=mappings)
    es.indices.put_alias(index=index_name, name=alias)


def rename_index(old_index_name: str, new_index_name: str, delete_old: bool):
    old_mappings = es.indices.get_mapping(index=old_index_name)[old_index_name]['mappings']
    # Create the new index with the same mappings as the old index
    es.indices.create(index=new_index_name, settings=DEFAULT_SETTINGS, mappings=old_mappings)
    reindex(es, source_index=old_index_name, target_index=new_index_name)
    if delete_old:
        # Delete the old index
        es.indices.delete(index=old_index_name)


def create_memories_index(
        embedding_model: str,
        embedding_model_dimensions: int,
):
    mappings = {
        "properties": {
            "id": {"type": "keyword"},
            "created_at": {"type": "date"},
            "conversation_id": {"type": "text"},
            "is_user_text": {"type": "boolean"},
            "text": {"type": "text"},
            "embedding": {
                "type": "dense_vector",
                "dims": embedding_model_dimensions,
                "index": True,
                "similarity": "dot_product",
            },
        },
        "_meta": {
            "embedding_model": embedding_model,
        },
    }
    create_initial_index(MEMORIES_INDEX, mappings)


def create_stories_index(
        embedding_model: str,
        embedding_model_dimensions: int,
):
    mappings = {
        "properties": {
            "id": {"type": "keyword"},
            "created_at": {"type": "date"},
            "conversation_id": {"type": "text"},
            "reference_text": {"type": "text"},
            "schema": {"type": "text"},
            "embedding": {
                "type": "dense_vector",
                "dims": embedding_model_dimensions,
                "index": True,
                "similarity": "dot_product",
            },
        },
        "_meta": {
            "embedding_model": embedding_model,
        },
    }
    create_initial_index(STORIES_INDEX, mappings)


def create_facts_index():
    mappings = {
        "properties": {
            "id": {"type": "keyword"},
            "created_at": {"type": "date"},
            "conversation_id": {"type": "text"},
            "story_id": {"type": "keyword"},
            "data": {"type": "object"},
        }
    }
    create_initial_index(FACTS_INDEX, mappings)


def create_openai_calls_logs_index():
    mappings = {
        "properties": {
            "moment": {"type": "date"},
            "params": {"type": "object"},
            "response": {"type": "text"},
        }
    }
    create_initial_index(OPENAI_CALLS_LOGS_INDEX, mappings)
