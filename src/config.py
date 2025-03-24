import os
from dotenv import load_dotenv

load_dotenv()

# Required Couchbase creds
COUCHBASE_CLUSTER = os.getenv('COUCHBASE_CLUSTER')
COUCHBASE_USERNAME = os.getenv('COUCHBASE_USERNAME')
COUCHBASE_PASSWORD = os.getenv('COUCHBASE_PASSWORD')

if not all([COUCHBASE_CLUSTER, COUCHBASE_USERNAME, COUCHBASE_PASSWORD]):
    print("Error: Missing required Couchbase credentials in .env file")
    exit(1)

COUCHBASE_BUCKET = os.getenv('COUCHBASE_BUCKET', 'travel-sample')
EMBEDDING_MODEL_NAME = os.getenv('EMBEDDING_MODEL_NAME', "sentence-transformers/all-mpnet-base-v2")

# Search config
VECTOR_INDEX_NAME = os.getenv('VECTOR_INDEX_NAME', 'travel_inventory_hotel_hugging_face_vector_index')
VECTOR_FIELD_NAME = os.getenv('VECTOR_FIELD_NAME', 'description_minilm_vector')
MODEL_DIMENSIONS = int(os.getenv('MODEL_DIMENSIONS', '768'))
FTS_INDEX_NAME = os.getenv('FTS_INDEX_NAME', 'travel_inventory_hotel_fts_index')
