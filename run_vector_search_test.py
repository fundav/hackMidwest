from ragService import collection, EMBEDDING_MODEL, VECTOR_FIELD, VECTOR_INDEX_NAME, gemini_client, embedding_to_list

query = "How do I apply for a farm loan?"
print('Query:', query)

# embed
try:
    resp = gemini_client.models.embed_content(model=EMBEDDING_MODEL, contents=[query])
    raw_vec = None
    if hasattr(resp, 'embedding'):
        raw_vec = resp.embedding
    elif hasattr(resp, 'embeddings'):
        raw_vec = resp.embeddings[0]
    elif isinstance(resp, dict):
        raw_vec = resp.get('embedding') or (resp.get('embeddings') and resp.get('embeddings')[0])
    vec = embedding_to_list(raw_vec)
    print('Query embedding length:', len(vec) if vec else 'None')
except Exception as e:
    print('Embedding error:', e)
    raise

pipeline = [
    {
        "$vectorSearch": {
            "index": VECTOR_INDEX_NAME,
            "path": VECTOR_FIELD,
            "queryVector": vec,
            "numCandidates": 50,
            "limit": 5
        }
    },
    {"$project": {"_id": 0, "text_chunk": f"${{}}".format(VECTOR_FIELD, ), "score": {"$meta": "vectorSearchScore"}}}
]

print('\nRunning aggregation...')
try:
    results = list(collection.aggregate(pipeline))
    print('Found', len(results), 'results')
    for r in results:
        print('---')
        print(r)
except Exception as e:
    print('Aggregation error:', e)
    raise
