from ragService import collection, VECTOR_FIELD, TEXT_FIELD

print('Collection object:', type(collection))
try:
    total = collection.count_documents({})
    print('Total documents in collection:', total)
except Exception as e:
    print('Error counting documents:', e)

# Count documents that have the vector field
try:
    have_vec = collection.count_documents({VECTOR_FIELD: {'$exists': True}})
    print(f"Documents with vector field '{VECTOR_FIELD}':", have_vec)
except Exception as e:
    print('Error counting docs with vector field:', e)

# Show types of vector field in first 5 docs that have it
try:
    cur = collection.find({VECTOR_FIELD: {'$exists': True}}).limit(5)
    for i, d in enumerate(cur):
        vec = d.get(VECTOR_FIELD)
        print('--- Doc', i, 'title=', d.get('title'))
        print('Vector type:', type(vec))
        # If it's a list, print length and sample
        if isinstance(vec, list):
            print('Vector length:', len(vec))
            print('First 5 values:', vec[:5])
        else:
            print('Vector repr (truncated):', repr(vec)[:200])
except Exception as e:
    print('Error reading sample docs:', e)

# Count docs where text field exists
try:
    have_text = collection.count_documents({TEXT_FIELD: {'$exists': True}})
    print(f"Documents with text field '{TEXT_FIELD}':", have_text)
except Exception as e:
    print('Error counting docs with text field:', e)
