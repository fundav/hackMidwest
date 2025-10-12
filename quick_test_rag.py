# Quick test: import ragService and show whether collection is available and ping the DB
import ragService
print('Has collection:', hasattr(ragService, 'collection'))
if hasattr(ragService, 'collection'):
    try:
        print('Collection name:', ragService.collection.name)
        print('Attempting ping...')
        print(ragService.mongo_client.admin.command('ping'))
    except Exception as e:
        print('Ping failed:', e)
