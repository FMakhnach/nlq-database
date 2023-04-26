from archie.persistence.elastic import es_client


def add(log: dict):
    es_client.index(index='openai_logs', document=log)
