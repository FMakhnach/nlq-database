from elasticsearch import Elasticsearch

CERT_FINGERPRINT = "aa12b0203cdf7439af11fab9045b500b0ad6fc5ef41b1302e42d97543dd2f922"
ELASTIC_PASSWORD = "z*b-*g9iIpvYgkSW9WN7"

es_client = Elasticsearch(
    "https://localhost:9200",
    ssl_assert_fingerprint=CERT_FINGERPRINT,
    basic_auth=("elastic", ELASTIC_PASSWORD)
)
