import os
from ragService import collection

print('MONGO_VECTOR_FIELD env var (as seen by ragService):', os.getenv('MONGO_VECTOR_FIELD'))
print('Collection type:', type(collection))

from collections import Counter

counter = Counter()

for doc in collection.find().limit(100):
    for k in doc.keys():
        counter[k] += 1

print('\nTop-level keys across first 100 documents:')
for k, v in counter.most_common():
    print(f'{k}: {v}')

# Show a sample document
sample = collection.find_one()
print('\nSample document keys and types:')
if sample:
    for k, v in sample.items():
        print(k, type(v))
    print('\nSample _id:', sample.get('_id'))
else:
    print('No sample doc found')
