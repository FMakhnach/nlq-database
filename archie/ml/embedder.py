from sentence_transformers import SentenceTransformer

embedder = SentenceTransformer('all-MiniLM-L6-v2')


def get_embedding(text):
    embedding = embedder.encode(text, normalize_embeddings=True)
    return embedding
