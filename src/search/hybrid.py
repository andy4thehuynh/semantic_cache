from search.keyword import keyword_search

def hybrid_search(cluster, vector_store, query_text, k=5):
    """
    Combines keyword search (SQL++) and vector search similarity search.

    Normalizes results to rank-based scores.
    Combines results alternating between keyword and vector to include both types in results.

    Args:
        cluster: Couchbase cluster
        vector_store: Stores embeddings
        query_text: User input for search query
        k: Number of results

    Returns:
        list: The shape of the ranked search results:
            - document: Langchain Document object
            - score: Normalized rank score between 0-1
            - match_type: 'keyword' or 'vector'
            - original_score: Score before normalization (for debugging)
    """
    keyword_results = keyword_search(cluster, query_text, k=k)
    vector_results = vector_store.similarity_search_with_score(query_text, k=k)
    
    (normalized_keyword_results, 
    normalized_vector_results) = _normalize_to_rank_based_scores(keyword_results, vector_results, k)

    _print_scores(normalized_keyword_results, normalized_vector_results)
    
    all_results = []
    for i in range(max(len(normalized_keyword_results), len(normalized_vector_results))):
        if i < len(normalized_keyword_results):
            all_results.append(normalized_keyword_results[i])
        if i < len(normalized_vector_results):
            all_results.append(normalized_vector_results[i])
    
    return all_results[:k]

def _normalize_to_rank_based_scores(keyword_results, vector_results, k):
    top_k_each = max(k // 2, 1)
    
    normalized_keyword_results = []
    for i, result in enumerate(keyword_results[:top_k_each]):
        rank_score = 1.0 - (i / k)
        normalized_keyword_results.append({
            'document': result['document'],
            'score': rank_score,
            'match_type': 'keyword',
            'original_score': result['score']
        })
    
    normalized_vector_results = []
    for i, (doc, score) in enumerate(vector_results[:top_k_each]):
        rank_score = 1.0 - (i / k) 
        normalized_vector_results.append({
            'document': doc,
            'score': rank_score,
            'match_type': 'vector',
            'original_score': score
        })
    
    return normalized_keyword_results, normalized_vector_results

def _print_scores(keyword_results, vector_results):
    print("--------------------------------")
    print("Rank-based scores:")
    print("Keyword results:")
    for r in keyword_results:
        print(f"  {r['document'].metadata['name']}: rank_score={r['score']:.3f}, original={r['original_score']:.3f}")
    print("Vector results:")
    for r in vector_results:
        print(f"  {r['document'].metadata['name']}: rank_score={r['score']:.3f}, original={r['original_score']:.3f}")
    print("--------------------------------")