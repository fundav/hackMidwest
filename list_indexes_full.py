from ragService import collection

print('Collection:', collection.full_name)

try:
    idxs = list(collection.list_indexes())
    print('Found', len(idxs), 'indexes')
    for i, idx in enumerate(idxs):
        print('\n--- Index', i+1, '---')
        for k, v in idx.items():
            print(k, ':', v)
except Exception as e:
    print('Error listing indexes:', e)
