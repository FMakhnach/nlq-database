from dotenv import load_dotenv
from elasticsearch import Elasticsearch
import os

load_dotenv()

ELASTIC_HOST = os.getenv("ELASTIC_HOST")
ELASTIC_CERT_FINGERPRINT = os.getenv("ELASTIC_CERT_FINGERPRINT")
ELASTIC_LOGIN = os.getenv("ELASTIC_LOGIN")
ELASTIC_PASSWORD = os.getenv("ELASTIC_PASSWORD")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

es_client = Elasticsearch(
    ELASTIC_HOST,
    ssl_assert_fingerprint=ELASTIC_CERT_FINGERPRINT,
    basic_auth=(ELASTIC_LOGIN, ELASTIC_PASSWORD),
)
