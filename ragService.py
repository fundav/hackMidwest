import os
from dotenv import load_dotenv
from google import genai
from google.genai.errors import APIError
from pymongo import MongoClient
import certifi
import urllib.parse
import re

# 1. Load Environment Variables (happens once when the server starts)
load_dotenv()

# --- Configuration from .env ---
MONGODB_URI = os.getenv("MONGODB_URI")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DB_NAME = os.getenv("MONGO_DB_NAME")
COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME")

# UPDATED FIELDS (These variables must be defined globally!)
VECTOR_FIELD = os.getenv("MONGO_VECTOR_FIELD") or "embedding"  # 'embedding'
# TEXT_FIELD: default to 'text' when env var is missing to keep compatibility
TEXT_FIELD = os.getenv("MONGO_TEXT_FIELD") or "text"      # 'text'
# ------------------------------

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
RAG_CHAT_MODEL = 'gemini-2.5-flash'          # <-- DEFINES RAG_CHAT_MODEL
VECTOR_INDEX_NAME = "vector_index"           # <-- DEFINES VECTOR_INDEX_NAME


# Helper: convert various embedding container types into plain Python list of floats
def embedding_to_list(vec):
    if vec is None:
        return None
    # google.genai.types.ContentEmbedding has .values
    if hasattr(vec, 'values'):
        try:
            return [float(x) for x in vec.values]
        except Exception:
            pass
    # embeddings may be directly on .embedding
    if hasattr(vec, 'embedding'):
        try:
            e = getattr(vec, 'embedding')
            if hasattr(e, 'values'):
                return [float(x) for x in e.values]
            if isinstance(e, (list, tuple)):
                return [float(x) for x in e]
        except Exception:
            pass
    # dict-like shapes
    if isinstance(vec, dict):
        if 'values' in vec and isinstance(vec['values'], (list, tuple)):
            try:
                return [float(x) for x in vec['values']]
            except Exception:
                pass
        if 'embedding' in vec and isinstance(vec['embedding'], (list, tuple)):
            try:
                return [float(x) for x in vec['embedding']]
            except Exception:
                pass
        if 'data' in vec and isinstance(vec['data'], list) and len(vec['data']) > 0:
            first = vec['data'][0]
            if isinstance(first, dict) and 'embedding' in first and isinstance(first['embedding'], (list, tuple)):
                try:
                    return [float(x) for x in first['embedding']]
                except Exception:
                    pass
    # plain list/tuple
    if isinstance(vec, (list, tuple)):
        try:
            return [float(x) for x in vec]
        except Exception:
            pass
    # try to iterate
    try:
        return [float(x) for x in vec]
    except Exception:
        return None

# --- 2. Initialize Clients Globally (These variables must be defined!) ---
try:
    # MongoDB Client
    safe_uri = MONGODB_URI
    try:
        if MONGODB_URI and '://' in MONGODB_URI and '@' in MONGODB_URI:
            scheme, rest = MONGODB_URI.split('://', 1)
            authpart = rest.split('@', 1)[0]
            if ':' in authpart:
                user, pw = authpart.split(':', 1)
                pw_enc = urllib.parse.quote(pw, safe='')
                after = rest.split('@', 1)[1]
                safe_uri = f"{scheme}://{user}:{pw_enc}@{after}"
    except Exception:
        safe_uri = MONGODB_URI

    mongo_client = MongoClient(safe_uri, tls=True, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=10000)
    db = mongo_client[DB_NAME]
    collection = db[COLLECTION_NAME]         # <-- DEFINES collection

    # Gemini Client
    gemini_client = genai.Client()           # <-- DEFINES gemini_client

except Exception as e:
    # Important: In a web service, logging this is better than exiting.
    print(f"FATAL ERROR: Could not initialize database or Gemini client: {e}")
    # You might raise an exception or set a global flag here to halt the service.

# ----------------------------------------------------------------------
# The get_rag_answer function starts below this block.
# ----------------------------------------------------------------------

def get_rag_answer(user_query: str, k: int = 4) -> str:
    """
    Performs the full RAG workflow: embed query, search MongoDB, and generate response.
    """
    if not user_query:
        return "Please provide a question."
        
    # --- 2.1 Embed the User Query ---
    try:
        from google.genai import types # Ensure types is imported for config

        # 1. CRITICAL FIX: Use the correct configuration object for RETRIEVAL_QUERY
        config = types.EmbedContentConfig(
            task_type="RETRIEVAL_QUERY"
        )

        query_embedding_response = gemini_client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=[user_query],
            config=config # Pass the configuration
        )
        
        # 2. Extract the list of floats directly. This resolves the 'cannot encode object' error.
        # .embeddings[0].values extracts the Python list of floats needed by PyMongo.
        query_vector = query_embedding_response.embeddings[0].values
        
        if query_vector is None:
            return "Error: Could not extract embedding vector from Gemini response"

    except APIError as e:
        return f"Error embedding query with Gemini: {e}"
    # --- The function continues immediately after this block with step 2.2 ---
    
    # --- 2.2 Perform Vector Search in MongoDB Atlas ---
    try:
        vector_search_pipeline = [
            {
                "$vectorSearch": {
                    "index": VECTOR_INDEX_NAME, 
                    "path": VECTOR_FIELD,        # Uses 'embedding'
                    "queryVector": query_vector,
                    "numCandidates": 100, 
                    "limit": k,                   
                }
            },
            {
                # KEY CHANGE: Projecting text, title, and program_name
                "$project": {
                    "_id": 0,
                    "text_chunk": f"${TEXT_FIELD}",
                    "title": "$title",
                    "program_name": "$program_name",
                    "score": {"$meta": "vectorSearchScore"}
                }
            }
        ]

        results = collection.aggregate(vector_search_pipeline)
        
        # Compile the context from the top K results, including metadata
        context_chunks = []
        for result in results:
            if result.get('text_chunk'):
                chunk_text = result.get('text_chunk')
                program_name = result.get('program_name', 'N/A')
                title = result.get('title', 'N/A')
                
                # Format the context to be clear for the LLM
                formatted_chunk = (
                    f"--- DOCUMENT START ---\n"
                    f"Program Name: {program_name}\n"
                    f"Title: {title}\n"
                    f"Content: {chunk_text}\n"
                    f"--- DOCUMENT END ---"
                )
                context_chunks.append(formatted_chunk)

        context = "\n\n".join(context_chunks)

        if not context:
            # Attempt a text-based fallback retrieval so the chatbot can still answer
            # when a vector index is not present. First try MongoDB $text (requires a text index),
            # otherwise perform a case-insensitive regex search on the TEXT_FIELD.
            text_candidates = []
            try:
                # Try $text search (will fail if no text index exists)
                text_candidates = list(collection.find({"$text": {"$search": user_query}}, {TEXT_FIELD: 1, "title": 1, "program_name": 1}).limit(k))
            except Exception:
                # Fallback: try a tokenized OR-regex search across common text fields.
                try:
                    # extract words of length >=3 to avoid common stopwords
                    tokens = re.findall(r"\w{3,}", user_query)
                    tokens = [t for t in tokens if len(t) >= 3]
                    # limit tokens to avoid huge queries
                    tokens = tokens[:12]
                    or_clauses = []
                    for t in tokens:
                        safe_t = re.escape(t)
                        or_clauses.append({TEXT_FIELD: {"$regex": safe_t, "$options": "i"}})
                        or_clauses.append({"title": {"$regex": safe_t, "$options": "i"}})
                        or_clauses.append({"program_overview": {"$regex": safe_t, "$options": "i"}})

                    if or_clauses:
                        text_candidates = list(collection.find({"$or": or_clauses}, {TEXT_FIELD: 1, "title": 1, "program_name": 1}).limit(k))
                    else:
                        text_candidates = []
                except Exception:
                    text_candidates = []

            if text_candidates:
                # Build context from textual candidates and continue to LLM generation
                context_chunks = []
                for result in text_candidates:
                    chunk_text = result.get(TEXT_FIELD) or result.get('program_overview') or ''
                    program_name = result.get('program_name', 'N/A')
                    title = result.get('title', 'N/A')
                    formatted_chunk = (
                        f"--- DOCUMENT START ---\n"
                        f"Program Name: {program_name}\n"
                        f"Title: {title}\n"
                        f"Content: {chunk_text}\n"
                        f"--- DOCUMENT END ---"
                    )
                    context_chunks.append(formatted_chunk)

                context = "\n\n".join(context_chunks)
            else:
                # If still no context, provide the diagnostic about missing vector index
                try:
                    num_vectors = collection.count_documents({VECTOR_FIELD: {'$exists': True}})
                except Exception:
                    num_vectors = 0

                sample_dim = None
                if num_vectors > 0:
                    try:
                        sample = collection.find_one({VECTOR_FIELD: {'$exists': True}})
                        if sample and isinstance(sample.get(VECTOR_FIELD), list):
                            sample_dim = len(sample.get(VECTOR_FIELD))
                    except Exception:
                        sample_dim = None

                if num_vectors > 0:
                    hint = (
                        f"No relevant context found by vector search. "
                        f"I see {num_vectors} documents that have a '{VECTOR_FIELD}' vector field"
                    )
                    if sample_dim:
                        hint += f" (sample embedding dimension: {sample_dim})."
                    hint += (
                        " This usually means an Atlas Search (vector) index is not configured on that field, "
                        f"or the index name is not '{VECTOR_INDEX_NAME}'.\n"
                        "Please create a Vector Search (KNN) index on your Atlas cluster for this collection "
                        f"targeting the field '{VECTOR_FIELD}' (dimensions should match the embedding size)."
                    )
                    return hint

                return "I cannot find any relevant information in the knowledge base to answer that question."
            
    except Exception as e:
        return f"Error during MongoDB Vector Search: {e}"

    # --- 2.3 Generate the Final RAG Response (Updated Prompt) ---
    system_prompt = f"""
    You are an AI chatbot specializing in USDA Programs. Your goal is to provide a helpful 
    and complete answer to the user's question *ONLY* based on the provided CONTEXT. 
    Reference the 'Program Name' and 'Title' when possible to ground your answer.
    Do not use outside knowledge.
    but small talk can happen.
    
    If the context does not contain the answer, state clearly: 
    "I cannot find the answer to that specific question in the USDA programs documentation."
    
    CONTEXT (Retrieved from USDA Programs Documentation):
    {context}
    
    USER QUESTION: {user_query}
    
    RESPONSE:
    """

    try:
        response = gemini_client.models.generate_content(
            model=RAG_CHAT_MODEL,
            contents=system_prompt
        )
        return response.text
    except APIError as e:
        return f"Error generating final response: {e}"