#Main source code
from scrapFromUSDA import WebAutomator
from selenium.webdriver.common.by import By
from scraping import scrape_current_page
from ragServiceUP import gemini_client, collection, EMBEDDING_MODEL, VECTOR_FIELD, TEXT_FIELD
import hashlib
import os
import traceback
from pymongo.errors import InvalidDocument

USDA = WebAutomator(True)
programLinks = []
USDA.navigate_to("https://www.rd.usda.gov/programs-services/all-programs?page=0")
index = USDA.find_element(By.CSS_SELECTOR, "li.usa-pagination__item:nth-child(5) > a:nth-child(1)").text
for i in range (0, int(index)):
    USDA.navigate_to(("https://www.rd.usda.gov/programs-services/all-programs?page=" + str(i)))
    programsList = USDA.find_element(By.CSS_SELECTOR, "div.view-content:nth-child(3)")
    programs = programsList.find_elements(By.CLASS_NAME, "views-row")
    for i in programs:
        prog = i.find_element(By.TAG_NAME, "a").get_attribute("href")
        programLinks.append(prog)
obj = []
for i in programLinks:
    USDA.navigate_to(i)
    item = scrape_current_page(USDA, By)
    obj.append(item)

    # Prepare a text field for embedding and storage. Prefer program_overview, then overview link, then joined fields.
    text_content = None
    if item.get('program_overview'):
        text_content = item.get('program_overview')
    elif item.get('program_overview_link'):
        text_content = item.get('program_overview_link')
    else:
        # Fallback: join available string fields
        parts = []
        for v in ['title', 'program_status', 'program_deadline', 'program_apply', 'program_requirements', 'program_contact', 'program_events']:
            if item.get(v):
                parts.append(str(item.get(v)))
        text_content = "\n\n".join(parts) if parts else ""

    # Ensure TEXT_FIELD variable
    text_field_name = TEXT_FIELD if 'TEXT_FIELD' in globals() and TEXT_FIELD else os.getenv('MONGO_TEXT_FIELD') or 'text'

    # Create a simple unique id for upsert using the overview link or title
    unique_key = item.get('program_overview_link') or item.get('title') or str(hashlib.sha256(text_content.encode('utf-8')).hexdigest())

    # Embed the text and upsert into MongoDB
    try:
        # Gemini expects 'contents' (not 'content'). Accept string or list.
        # Avoid truth-testing collection/gemini_client objects; compare with None explicitly
        if gemini_client is None or collection is None:
            raise RuntimeError('Gemini client or Mongo collection not initialized')
        emb_resp = gemini_client.models.embed_content(model=EMBEDDING_MODEL, contents=[text_content])

        # Robust extraction of embedding vector from response
        embedding_vector = None
        if hasattr(emb_resp, 'embedding'):
            embedding_vector = emb_resp.embedding
        elif hasattr(emb_resp, 'embeddings'):
            embedding_vector = emb_resp.embeddings[0]
        elif isinstance(emb_resp, dict):
            embedding_vector = emb_resp.get('embedding') or (emb_resp.get('embeddings') and emb_resp.get('embeddings')[0])
            if not embedding_vector and emb_resp.get('data'):
                try:
                    embedding_vector = emb_resp['data'][0].get('embedding')
                except Exception:
                    embedding_vector = None

        if embedding_vector is None:
            raise ValueError('Could not extract embedding vector from Gemini response')

        # Build document to upsert
        doc = item.copy()
        doc[text_field_name] = text_content

        # Normalize embedding vector to a plain Python list of floats
        try:
            if embedding_vector is None:
                normalized_vector = None
            else:
                # If the vector is wrapped in another container (like dict or object), try to extract a list
                if hasattr(embedding_vector, '__iter__') and not isinstance(embedding_vector, (str, bytes)):
                    normalized_vector = [float(x) for x in embedding_vector]
                else:
                    # single numeric value -> wrap in list
                    normalized_vector = [float(embedding_vector)]
        except Exception:
            # Fallback: drop the embedding if it can't be converted
            normalized_vector = None

        if normalized_vector is not None:
            doc[VECTOR_FIELD] = normalized_vector

        # Use upsert on a stable key
        filter_q = { 'unique_id': unique_key }
        doc['unique_id'] = unique_key

        try:
            collection.update_one(filter_q, {'$set': doc}, upsert=True)
            print(f"Upserted document for: {item.get('title') or unique_key}")
        except InvalidDocument as ide:
            # Attempt to sanitize and retry: remove problematic fields, convert vector to simple list or drop it
            print(f"InvalidDocument on upsert for {item.get('title')}: {ide}; attempting sanitization and retry")
            try:
                # Remove any keys with leading $ or containing '.' (not allowed in BSON keys)
                safe_doc = {}
                for k, v in doc.items():
                    if isinstance(k, str) and (k.startswith('$') or '.' in k):
                        # skip or rename; here we skip
                        continue
                    safe_doc[k] = v

                # Ensure vector is a list of floats or remove it
                if VECTOR_FIELD in safe_doc:
                    try:
                        safe_doc[VECTOR_FIELD] = [float(x) for x in safe_doc[VECTOR_FIELD]]
                    except Exception:
                        safe_doc.pop(VECTOR_FIELD, None)

                collection.update_one(filter_q, {'$set': safe_doc}, upsert=True)
                print(f"Upserted sanitized document for: {item.get('title') or unique_key}")
            except Exception as e2:
                print(f"Sanitized upsert failed for {item.get('title')}: {e2}")
                # Log failed item + traceback
                try:
                    with open('failed_upserts.jsonl', 'a', encoding='utf-8') as f:
                        f.write('{')
                        f.write('"title": ' + repr(item.get('title')) + ',')
                        f.write('"error": ' + repr(str(e2)) + ',')
                        f.write('"trace": ' + repr(traceback.format_exc()))
                        f.write('}\n')
                except Exception:
                    pass
        except Exception as e:
            # Generic failure already logged below
            raise
    except Exception as e:
        print(f"Failed to embed/upsert item ({item.get('title')}): {e}")
        # Log failed item to disk for later retry
        try:
            import json
            with open('failed_upserts.jsonl', 'a', encoding='utf-8') as f:
                json.dump({'item': item, 'error': str(e)}, f)
                f.write('\n')
        except Exception:
            pass

# Cleanup WebDriver
USDA.close_driver()
#print(obj)
