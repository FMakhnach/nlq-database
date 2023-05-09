from sentence_transformers import SentenceTransformer

from archie.persistence.elastic import es_client as es

# DRAFT CODE


# tnx ChatGPT for this code

def update_mapping_and_embeddings(
        index_alias,
        index_name,
        embedding_model_name,
        vector_dims: int):
    temp_index_name = index_name + '_temp'
    # Get the mapping of the old index
    old_mapping = es.indices.get_mapping(index=old_index_name)
    new_mapping = dict(old_mapping)[old_index_name]['mappings']
    new_mapping['properties']['embedding']['dims'] = vector_dims

    # Create the new index with the updated mapping
    es.indices.create(index=temp_index_name, body={"mappings": new_mapping})

    # Get the documents from the old index
    body = {
        "size": 10000,
        "query": {
            "match_all": {}
        }
    }
    docs = es.search(index=old_index_name, **body)["hits"]["hits"]

    # Calculate the new embeddings
    model = SentenceTransformer(embedding_model_name)
    new_docs = []
    for doc in docs:
        text = doc["_source"]["message"]
        embedding = model.encode(text, normalize_embeddings=True)
        doc["_source"]["embedding"] = embedding
        new_docs.append(doc["_source"])

    for new_doc in new_docs:
        es.index(index=temp_index_name, document=new_doc)

    # Delete the old index
    # es.indices.delete(index=old_index_name)


# Example usage
# old_index_name = "memories"
# new_index_name = "memories_v2"
# update_mapping_and_embeddings(es,
#                               old_index_name=old_index_name,
#                               new_index_name=new_index_name,
#                               embedding_model_name='paraphrase-multilingual-mpnet-base-v2',
#                               vector_dims=768)
