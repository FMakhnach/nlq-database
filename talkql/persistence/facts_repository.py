from talkql.persistence.elastic import es_client
from talkql.persistence.elastic.indices import FACTS_INDEX as INDEX
from talkql.persistence.entities import FactEntity


def add_fact(fact: FactEntity):
    es_client.index(index=INDEX, document=fact.to_dict())


def search_facts(query: dict):
    return es_client.search(index=INDEX, body=query)["hits"]["hits"]
