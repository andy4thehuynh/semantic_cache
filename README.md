<h1 align="center">
  <img alt="couchbase" src="src/assets/cb_logo.png" />
</h1>

# Semantic Cache

An interactive CLI program combining SQL++ keyword search and vector similarity search using Couchbase Capella and LangChain to retrieve contextually relevant search results using the sample dataset (hotels) provided by Couchbase.

## Setup Instructions
### Prerequisites
- Python 3.10.x or higher
- Provision a Couchbase Capella free tier cluster
- Ensure `travel-sample` dataset bucket is installed *(provided by free tier)*

### Setup Steps
1. Clone repository and cd into directory: `
2. Create and activate a virtual environment: `python -m venv venv` and `source venv/bin/activate`
3. Install dependencies: `python -m pip install -r src/requirements.txt`
4. Update environemnt variables in `.env.sample` and rename to `.env`
5. Create indexes in Couchbase
- Vector index: `travel_inventory_hotel_hugging_face_vector_index`
- FTS index: `travel_inventory_hotel_fts_index`
7. Run the program: `python src/main.py`

## Embedding & Schema
**Embedding Model**: `all-mpnet-base-v2` 
- 32M downloads per month on Hugging Face suggests it's widely adopted and a popular choice for sentence embedding
- Produces 768-dimensional embeddings to capture the meaning of the text semantically
- Strikes a balance between performance and accuracy
- The [Hugging Face documentation description](https://huggingface.co/sentence-transformers/all-mpnet-base-v2) explicitly states it's a good choice for semantic search
- **Alternative model**: considered `all-MiniLM-L6-v2` as it is faster but seems less accurate in comparison

**Schema**:
```json
{
    "id": "hotel_123",
    "name": "Oceanfront Resort",
    "description": "Luxury beachfront resort...",
    "description_minilm_vector": [0.123, 0.456, 0.789, ...],
    "city": "Miami",
    "state": "Florida",
    "country": "USA"
}
```
- Uses Couchbase as a backend database for storing embeddings
- Leverages `langchain_couchbase` package to access Couchbase's native vector store
- Documents stored in `travel-sample` bucket under `inventory` scope and `hotel` collection
- Full text search on on the index embedding

## SQL++ & Vector Search

**Keyword Search (SQL++) Strengths**:
- Allows for finding exact matches when users search specific hotel features like "oceanfront"
- Filters hotels by specific amenities mentioned in descriptions
- Quick results for common hotel keywords

**Vector Search Strengths**:
- Captures intent behind user queries like "oceanfront" being similar to "beachfront"
- Retrieves hotels with similar features, even if not explicitly mentioned in user queries

**How They Complement Each Other**:
- Vectors find similar concepts while keywords find exact matches with speed
- This approach ensures users don't miss out on relevant hotels due to phrasing
- Users find relevant hotels regardless of how they phrase their search queries


## Challenges & Improvements

### Challenges
1. Having never used LangChain before, I spent significant time understanding the technical exercise requirements and the LangChain framework. The `langchain-couchbase` package helped abstract complexity and reading through the [source code](https://github.com/Couchbase-Ecosystem/langchain-couchbase/) proved to be time well spent. I found these resources helpful: [LangChain Couchbase Documentation](https://python.langchain.com/docs/integrations/vectorstores/couchbase), [LangChain Couchbase API Reference](https://github.com/couchbase-examples/langchain-couchbase-api-reference/tree/main?tab=readme-ov-file)
2. Deciding on an embedding model presented challenges in balancing performance and accuracy. I opted for `all-mpnet-base-v2` due to its popularity and support for semantic understanding. The tradeoff was managing larger embeddings for better accuracy at the cost of slower performance. For the presentation, I considered using an in-memory embedding model like `all-MiniLM-L6-v2` which stores smaller embeddings but would provide less semantic understanding. Ultimately, I stuck with `all-mpnet-base-v2` even though downloading the model locally took a while.

### Improvements
1. We're relying on basic print statements for user feedback which makes it difficult to track issues if this project scales. Adding a logging system and retry logic for failed API calls would improve the user experience.
2. Users cannot balance the scoring weights from search results of which might be valuable for tuning results.
3. Restructuring `main.py` by extracting the logic from `if __name__ == __main__` to a separate function (likely called main) to extend the program for other uses like a web app.
4. Create unit tests for embedding and hybrid search logic to ensure coverage of application.