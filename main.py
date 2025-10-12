#Main source code
from scrapFromUSDA import WebAutomator
from selenium.webdriver.common.by import By
from scraping import scrape_current_page
from ragService import gemini_client, collection, EMBEDDING_MODEL, VECTOR_FIELD, TEXT_FIELD, embedding_to_list
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
    item = scrape_current_page(USDA, By, i)
    obj.append(item)

    # Prepare a text field for embedding and storage. Prefer program_overview, then overview link, then joined fields.
    if item.get('program_overview'):
        text_content = item.get('program_overview')
    elif item.get('program_overview_link'):
        text_content = item.get('program_overview_link')
    else:
        parts = []
        for v in ['title', 'website', 'program_status', 'program_deadline', 'program_apply', 'program_requirements', 'program_contact', 'program_events']:
            if item.get(v):
                parts.append(str(item.get(v)))
        text_content = "\n\n".join(parts) if parts else ""

    # Use TEXT_FIELD from ragService (fallback to 'text' if missing)
    text_field_name = TEXT_FIELD or os.getenv('MONGO_TEXT_FIELD') or 'text'

    # Create a stable unique id for upsert using the overview link or title
    unique_key = item.get('program_overview_link') or item.get('title') or hashlib.sha256(text_content.encode('utf-8')).hexdigest()

    # Embed the text and upsert into MongoDB
    try:
        # Gemini expects 'contents' (not 'content'). Accept string or list.
        # Avoid truth-testing collection/gemini_client objects; compare with None explicitly
        if gemini_client is None or collection is None:
            raise RuntimeError('Gemini client or Mongo collection not initialized')
        emb_resp = gemini_client.models.embed_content(model=EMBEDDING_MODEL, contents=[text_content])

        # Robust extraction and normalization using helper from ragService
        raw_vec = None
        if hasattr(emb_resp, 'embedding'):
            raw_vec = emb_resp.embedding
        elif hasattr(emb_resp, 'embeddings'):
            raw_vec = emb_resp.embeddings[0]
        elif isinstance(emb_resp, dict):
            raw_vec = emb_resp.get('embedding') or (emb_resp.get('embeddings') and emb_resp.get('embeddings')[0])

        normalized_vector = embedding_to_list(raw_vec)
        if normalized_vector is None:
            raise ValueError('Could not extract/normalize embedding vector from Gemini response')

        # Build document and upsert
        doc = item.copy()
        doc[text_field_name] = text_content
        doc[VECTOR_FIELD] = normalized_vector
        filter_q = {'unique_id': unique_key}
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
