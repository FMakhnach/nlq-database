from sentence_transformers import SentenceTransformer

EMBEDDER_MODEL = 'paraphrase-multilingual-mpnet-base-v2'
EMBEDDER_DIMS = 768
embedder = SentenceTransformer(EMBEDDER_MODEL)


def get_embedding(text):
    embedding = embedder.encode(text, normalize_embeddings=True)
    return embedding
