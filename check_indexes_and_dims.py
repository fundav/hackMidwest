from ragService import collection, gemini_client, EMBEDDING_MODEL, VECTOR_FIELD
import certifi

print('Collection:', collection.full_name)

# List indexes
try:
    idxs = list(collection.list_indexes())
    print('\nIndexes found:')
    for i in idxs:
        print('-', i['name'], 'keys->', i.get('key') or i.get('weights') or i.get('v'))
except Exception as e:
    print('Error listing indexes:', e)

# Count docs with VECTOR_FIELD
try:
    have_vec = collection.count_documents({VECTOR_FIELD: {'$exists': True}})
    print(f"\nDocuments with vector field '{VECTOR_FIELD}':", have_vec)
except Exception as e:
    print('Error counting vector-field docs:', e)

# Sample vector length
try:
    doc = collection.find_one({VECTOR_FIELD: {'$exists': True}})
    if doc:
        vec = doc.get(VECTOR_FIELD)
        print('\nSample doc _id:', doc.get('_id'))
        print('Type of vector in sample doc:', type(vec))
        if isinstance(vec, list):
            print('Sample vector length:', len(vec))
            print('First 5 values:', vec[:5])
        else:
            print('Vector is not a list; repr (truncated):', repr(vec)[:200])
    else:
        print('\nNo document with vector field found')
except Exception as e:
    print('Error sampling vector:', e)

# Request a test embedding to compare lengths
try:
    test_text = 'This is a short test sentence to measure embedding length.'
    resp = gemini_client.models.embed_content(model=EMBEDDING_MODEL, contents=[test_text])
    raw = None
    if hasattr(resp, 'embedding'):
        raw = resp.embedding
    elif hasattr(resp, 'embeddings'):
        raw = resp.embeddings[0]
    elif isinstance(resp, dict):
        raw = resp.get('embedding') or (resp.get('embeddings') and resp.get('embeddings')[0])
    # Try to coerce list
    if raw is not None:
        try:
            if hasattr(raw, 'values'):
                arr = [float(x) for x in raw.values]
            elif isinstance(raw, (list, tuple)):
                arr = [float(x) for x in raw]
            elif isinstance(raw, dict) and 'embedding' in raw:
                arr = [float(x) for x in raw['embedding']]
            else:
                arr = list(raw)
            print('\nTest embedding length:', len(arr))
        except Exception as e:
            print('Could not coerce test embedding to list:', e)
    else:
        print('No embedding returned by Gemini for test text')
except Exception as e:
    print('Error requesting test embedding:', e)
