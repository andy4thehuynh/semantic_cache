from datetime import timedelta
from config import (
    COUCHBASE_CLUSTER,
    COUCHBASE_USERNAME,
    COUCHBASE_PASSWORD,
    COUCHBASE_BUCKET,
    VECTOR_INDEX_NAME,
    VECTOR_FIELD_NAME,
    EMBEDDING_MODEL_NAME,
)
from search.hybrid import hybrid_search
from embedding import generate_and_store_embeddings

# Connect to Couchbase cluster
from couchbase.auth import PasswordAuthenticator
from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions

# Generates vector embeddings and uses Couchbase as backend
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_couchbase.vectorstores import CouchbaseVectorStore

def connect_to_couchbase_cluster():
    """
    Gets credentials from config to authenticate and establish a connection.

    Returns:
        Cluster: Couchbase cluster

    Raises:
        Exception: Prints error if connection fails
    """
    auth = PasswordAuthenticator(COUCHBASE_USERNAME, COUCHBASE_PASSWORD)
    options = ClusterOptions(auth)
    options.apply_profile("wan_development")

    print("Connecting to cluster...")
    try:
        cluster = Cluster(f"couchbases://{COUCHBASE_CLUSTER}", options)
        cluster.wait_until_ready(timedelta(seconds=5))
        print("Connected to cluster")

        return cluster
    except Exception as e:
        print(e)

def initialize_vector_store(cluster):
    """
    Set up a vector store using Couchbase as the backend to store embeddings.

    Args:
        cluster: Couchbase cluster

    Returns:
        CouchbaseVectorStore: For semantic search using embeddings
    """
    embeddings_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

    return CouchbaseVectorStore(
        cluster=cluster,
        bucket_name=COUCHBASE_BUCKET,
        scope_name="inventory",
        collection_name="hotel",
        embedding=embeddings_model,
        index_name=VECTOR_INDEX_NAME,
        text_key="page_content",
        embedding_key=VECTOR_FIELD_NAME,
    )

if __name__ == "__main__":
    cluster = connect_to_couchbase_cluster()
    vector_store = initialize_vector_store(cluster)
    collection = cluster.bucket(COUCHBASE_BUCKET).scope("inventory").collection("hotel")

    generate_and_store_embeddings(cluster, vector_store)

    # CLI for hotel search
    print("\nWelcome to the Hotel Search System")
    print("=" * 50)
    print("Enter your hotel search query")
    print("Example: 'beachfront resort with ocean view in Miami'")
    
    while True:
        try:
            query = input("\nSearch query, or 'q' to quit: ").strip()
            if not query:
                print("Please enter a search query")
                continue
                
            if query.lower() == 'q':
                print("\nThank you for using the Hotel Search System!")
                break
            
            print(f"\nSearching for: '{query}'")
            print("=" * 50)
            
            results = hybrid_search(cluster, vector_store, query)
            
            if not results:
                print("\nNo matching hotels found.")
                continue
                
            print(f"\nFound {len(results)} results:")
            for i, result in enumerate(results, 1):
                print(f"\n{i}. {result['document'].metadata['name']}")
                location_parts = [
                    result['document'].metadata['city'],
                    result['document'].metadata.get('state', ''),
                    result['document'].metadata['country']
                ]
                location = ', '.join(part for part in location_parts if part)
                print(f"  Location: {location}")
                print(f"  Score: {result['score']:.3f} ({result['match_type']})")
                print(f"  Description: {result['document'].page_content[:200]}...")
            
            print("\nSearch Analysis:")
            keyword_matches = sum(1 for r in results if r['match_type'] == 'keyword')
            vector_matches = sum(1 for r in results if r['match_type'] == 'vector')
            print(f"  Keyword matches: {keyword_matches}")
            print(f"  Vector matches: {vector_matches}")
            
        except Exception as e:
            print(f"\nError during search: {e}")
            print("Please try again with a different query")