from ragService import collection, VECTOR_FIELD, VECTOR_INDEX_NAME

print('Counting docs with vector field...')
print(collection.count_documents({VECTOR_FIELD: {'$exists': True}}))

# sample vector length
doc = collection.find_one({VECTOR_FIELD: {'$exists': True}})
if doc:
    vec = doc.get(VECTOR_FIELD)
    print('Sample vector type:', type(vec))
    if isinstance(vec, list):
        print('Sample vector length:', len(vec))

# run vectorSearch with and without index name (some Atlas versions accept empty index)
from bson import SON

try:
    print('\nTrying $vectorSearch with configured index name:', VECTOR_INDEX_NAME)
    pipeline = [
        {"$vectorSearch": {"index": VECTOR_INDEX_NAME, "path": VECTOR_FIELD, "queryVector": vec, "numCandidates": 50, "limit": 3}},
        {"$project": {"_id": 0, "text": "$text", "score": {"$meta": "vectorSearchScore"}}}
    ]
    res = list(collection.aggregate(pipeline))
    print('Results with index name:', len(res))
except Exception as e:
    print('Error with index name search:', e)

try:
    print('\nTrying $vectorSearch WITHOUT index name (index omitted)')
    pipeline = [
        {"$vectorSearch": {"path": VECTOR_FIELD, "queryVector": vec, "numCandidates": 50, "limit": 3}},
        {"$project": {"_id": 0, "text": "$text", "score": {"$meta": "vectorSearchScore"}}}
    ]
    res = list(collection.aggregate(pipeline))
    print('Results without index name:', len(res))
except Exception as e:
    print('Error without index name search:', e)
