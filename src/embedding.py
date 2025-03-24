from langchain_core.documents import Document
from config import VECTOR_FIELD_NAME

def generate_and_store_embeddings(cluster, vector_store):
    """
    Generates embeddings for documents that don't already have them.

    Processes documents in batches of 50 (avoids memory issues) and adds to vector store.

    Args:
        cluster: Couchbase cluster
        vector_store: Stores embeddings
    """
    try:
        existing_count, total_docs = _check_existing_embeddings(cluster)
        if (existing_count * 2) >= total_docs:
            print("All documents have embeddings. Skipping embedding generation.")
        else:
            batch_size = 50
            offset = 0
            total_processed = 0

            print('Processing documents in batches...')

            while True:
                batch_query = f"""
                    SELECT h.*
                    FROM `travel-sample`.inventory.hotel h
                    WHERE h.description IS NOT MISSING 
                    AND h.description != ''
                    AND h.{VECTOR_FIELD_NAME} IS MISSING
                    LIMIT {batch_size} OFFSET {offset}
                """
                
                print(f'Fetching batch of documents (offset: {offset}, limit: {batch_size})...')
                result = cluster.query(batch_query)
                
                docs = []
                hotel_ids = []
                for row in result:
                    doc = Document(
                        page_content=row['description'],
                        metadata={
                            "id": row['id'],
                            "name": row['name'],
                            "city": row.get('city', ''),
                            "state": row.get('state', ''),
                            "country": row.get('country', ''),
                        },
                    )
                    docs.append(doc)
                    hotel_ids.append(str(row['id']))
                
                batch_count = len(docs)
                if batch_count == 0:
                    break
                    
                total_processed += batch_count
                print(f"Processing batch with {batch_count} documents...")
                
                try:
                    vector_store.add_documents(documents=docs, ids=hotel_ids)
                    print(f'Successfully added batch of {batch_count} documents to vector store')
                except Exception as e:
                    print(f'Error during batch processing: {e}')
                    raise
                    
                offset += batch_size
                
            print(f"Total documents processed and added to vector store: {total_processed}")

    except Exception as e:
        print(f'Error in generate_and_store_embeddings: {e}')
        raise

def _check_existing_embeddings(cluster):
    """
    Checks number of documents that already have embeddings and checks total documents.
    
    Args:
        cluster: Couchbase cluster 
        
    Returns:
        tuple: (existing_count, total_docs) where
            existing_count: Documents with embeddings
            total_docs: Number of documents with descriptions to index
    """
    try:
        existing_count = 0
        count_query = f"""
            SELECT COUNT(*) as count
            FROM `travel-sample`.inventory.hotel h
            WHERE h.{VECTOR_FIELD_NAME} IS NOT MISSING
        """
        print('Checking existing embeddings...')

        result = cluster.query(count_query)
        for row in result:
            existing_count = row['count']
        
        print(f"Found {existing_count} documents that already have embeddings")

        total_docs = 0
        total_docs_query = """
            SELECT COUNT(*) as count
            FROM `travel-sample`.inventory.hotel h
            WHERE h.description IS NOT MISSING AND h.description != ''
        """
        result = cluster.query(total_docs_query)

        for row in result:
            total_docs = row['count']

        print(f"Total hotel documents with descriptions: {total_docs}")

        return existing_count, total_docs
    except Exception as e:
        print(f'Error in check_existing_embeddings: {e}')
        raise
