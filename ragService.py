import os
from dotenv import load_dotenv
from google import genai
from google.genai.errors import APIError
from pymongo import MongoClient

# 1. Load Environment Variables (happens once when the server starts)
load_dotenv()

# --- Configuration from .env ---
MONGODB_URI = os.getenv("MONGODB_URI")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DB_NAME = os.getenv("MONGO_DB_NAME")
COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME")

# UPDATED FIELDS (These variables must be defined globally!)
VECTOR_FIELD = os.getenv("MONGO_VECTOR_FIELD")  # 'embedding'
TEXT_FIELD = os.getenv("MONGO_TEXT_FIELD")      # 'text'
# ------------------------------

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
RAG_CHAT_MODEL = 'gemini-2.5-flash'          # <-- DEFINES RAG_CHAT_MODEL
VECTOR_INDEX_NAME = "vector_index"           # <-- DEFINES VECTOR_INDEX_NAME

# --- 2. Initialize Clients Globally (These variables must be defined!) ---
try:
    # MongoDB Client
    mongo_client = MongoClient(MONGODB_URI)
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
        query_embedding_response = gemini_client.models.embed_content(
            model=EMBEDDING_MODEL, 
            content=user_query,
            task_type="RETRIEVAL_QUERY"
        )
        query_vector = query_embedding_response.embedding
    except APIError as e:
        return f"Error embedding query with Gemini: {e}"
    
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
            return "I cannot find any relevant information in the knowledge base to answer that question."
            
    except Exception as e:
        return f"Error during MongoDB Vector Search: {e}"

    # --- 2.3 Generate the Final RAG Response (Updated Prompt) ---
    system_prompt = f"""
    You are an AI chatbot specializing in USDA Programs. Your goal is to provide a helpful 
    and complete answer to the user's question *ONLY* based on the provided CONTEXT. 
    Reference the 'Program Name' and 'Title' when possible to ground your answer.
    Do not use outside knowledge.
    
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