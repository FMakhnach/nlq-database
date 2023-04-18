from archie.persistence.elastic import es_client
from archie.persistence.entities import Fact


def add_fact(fact: Fact):
    es_client.index(index='facts', document=fact.to_dict())


def search_facts(query: dict):
    return es_client.search(index='facts', body=query)["hits"]["hits"]
