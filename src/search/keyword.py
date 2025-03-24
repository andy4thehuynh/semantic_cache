from langchain_core.documents import Document
from config import VECTOR_INDEX_NAME, FTS_INDEX_NAME

def keyword_search(cluster, query_text, k=5):
    """
    Uses SQL++ and Full Text Search to find hotels.

    Couchbase's SEARCH function finds hotels matching texts in their descriptions.

    Args:
        cluster: Couchbase cluster
        query_text: Text to search
        k: Number of results

    Returns:
        list: Search results containing:
            - document: Langchain Document with hotel details
            - score: Relevance score from Full Text Search
    """
    search_request = {
        "query": {
            "match": query_text,
            "field": "description",
            "analyzer": "standard"
        },
        "size": k,
        "index": VECTOR_INDEX_NAME
    }

    sql_query = f"""
        SELECT 
            h.id, 
            h.name, 
            h.country, 
            h.city, 
            h.description,
            SEARCH_SCORE() as `score`
        FROM `travel-sample`.inventory.hotel h
        WHERE SEARCH(h.description, $search_request,
            {{"index": "travel-sample.inventory.{FTS_INDEX_NAME}"}}
        )
        ORDER BY `score` DESC
        LIMIT $k
    """
    
    try:
        results = []
        query_results = list(cluster.query(sql_query, search_request=search_request, k=k))

        for row in query_results:
            results.append({
                'document': Document(
                    page_content=row['description'],
                    metadata={
                        'id': row['id'],
                        'name': row['name'],
                        'country': row.get('country', ''),
                        'city': row.get('city', ''),
                    }
                ),
                'score': float(row.get('score', 0.0)),
                'match_type': 'keyword'
            })
        
        return results
    except Exception as e:
        print(f"Error in keyword_search: {e}")