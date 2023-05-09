from archie.persistence.elastic import es_client
from archie.persistence.elastic.indices import OPENAI_CALLS_LOGS_INDEX as INDEX


def add(log: dict):
    es_client.index(index=INDEX, document=log)
