import time
import json
from bson import ObjectId
from ragService import collection, gemini_client, EMBEDDING_MODEL, VECTOR_FIELD, TEXT_FIELD, embedding_to_list

BATCH_SIZE = 10
SLEEP_BETWEEN = 0.35  # seconds between embed calls to be polite with API rate limits

query = {VECTOR_FIELD: {'$exists': False}}  # find docs missing embeddings
cursor = collection.find(query)

count = 0
failed = 0

for doc in cursor:
    count += 1
    _id = doc.get('_id')
    text = doc.get(TEXT_FIELD) or doc.get('program_overview') or doc.get('title')
    if not text:
        print(f"Skipping {_id} - no text available to embed")
        continue
    try:
        resp = gemini_client.models.embed_content(model=EMBEDDING_MODEL, contents=[text])
        # try to extract embedding robustly
        raw_vec = None
        if hasattr(resp, 'embedding'):
            raw_vec = resp.embedding
        elif hasattr(resp, 'embeddings'):
            raw_vec = resp.embeddings[0]
        elif isinstance(resp, dict):
            raw_vec = resp.get('embedding') or (resp.get('embeddings') and resp.get('embeddings')[0])
            if not raw_vec and resp.get('data'):
                try:
                    raw_vec = resp['data'][0].get('embedding')
                except Exception:
                    raw_vec = None

        vec = embedding_to_list(raw_vec)
        if not vec:
            raise ValueError('Could not extract embedding as list')

        collection.update_one({'_id': ObjectId(_id)}, {'$set': {VECTOR_FIELD: vec}})
        print(f"Backfilled embedding for doc {_id} ({count})")
    except Exception as e:
        failed += 1
        print(f"Failed to backfill {_id}: {e}")
        try:
            with open('failed_backfill.jsonl', 'a', encoding='utf-8') as f:
                json.dump({'_id': str(_id), 'error': str(e)}, f)
                f.write('\n')
        except Exception:
            pass
    time.sleep(SLEEP_BETWEEN)

print(f"Backfill complete. Attempted: {count}, failed: {failed}")
