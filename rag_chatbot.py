import os
from dotenv import load_dotenv
from google import genai
from google.genai.errors import APIError
from pymongo import MongoClient

# 1. Load Environment Variables
load_dotenv()

# --- Configuration from .env ---
MONGODB_URI = os.getenv("MONGODB_URI")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DB_NAME = os.getenv("MONGO_DB_NAME")
COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME")
VECTOR_FIELD = os.getenv("MONGO_VECTOR_FIELD")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION")) # 768

# 2. Initialize Clients
try:
    # MongoDB Client
    mongo_client = MongoClient(MONGODB_URI)
    db = mongo_client[DB_NAME]
    collection = db[COLLECTION_NAME]

    # Gemini Client
    # The google-genai library will automatically use the GEMINI_API_KEY 
    # from the environment if not explicitly passed.
    gemini_client = genai.Client(api_key=GEMINI_API_KEY)

except Exception as e:
    print(f"Error initializing clients: {e}")
    exit()

def get_context_from_vector_search(user_query: str, k: int = 4) -> str:
    """
    1. Embeds the user query.
    2. Performs a vector search in MongoDB Atlas.
    3. Returns the relevant text chunks as a single context string.
    """
    try:
        # Generate embedding for the user query
        query_embedding_response = gemini_client.models.embed_content(
            model=EMBEDDING_MODEL, 
            content=user_query,
            task_type="RETRIEVAL_QUERY"
        )
        query_vector = query_embedding_response.embedding

    except APIError as e:
        return f"Error embedding query: {e}. Check your GEMINI_API_KEY and model name."
    
    # Define the Atlas Vector Search pipeline
    # The index name must match the name you used in Step 2: 'vector_index'
    vector_search_pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index", 
                "path": VECTOR_FIELD,
                "queryVector": query_vector,
                "numCandidates": 100, # Number of documents to scan
                "limit": k,           # Number of documents to return
            }
        },
        {
            "$project": {
                "_id": 0,
                "text_chunk": "$text",  # Assuming your scraped text is stored in a 'text' field
                "score": {"$meta": "vectorSearchScore"}
            }
        }
    ]

    # Execute the search
    results = collection.aggregate(vector_search_pipeline)
    
    # Compile the context from the top K results
    context_chunks = [result['text_chunk'] for result in results]
    
    context = "\n---\n".join(context_chunks)
    
    if not context:
        return "No relevant information found in the knowledge base."
        
    return context

def generate_rag_response(user_query: str):
    """
    1. Retrieves context from MongoDB.
    2. Combines context with user query into a system prompt.
    3. Generates a response using a Gemini model.
    """
    print("-> Retrieving context from MongoDB Atlas...")
    context = get_context_from_vector_search(user_query)
    
    if context.startswith("Error") or "No relevant information" in context:
        return context

    # 4. Create the final prompt for the LLM
    system_prompt = f"""
    You are an AI chatbot specializing in USDA Programs. Your role is to answer user
    questions *only* based on the provided CONTEXT. Do not use outside knowledge.
    If the context does not contain the answer, state clearly: 
    "I cannot find the answer to that specific question in the USDA programs documentation."
    
    CONTEXT:
    {context}
    
    USER QUESTION: {user_query}
    
    RESPONSE:
    """

    # 5. Generate the final response
    print("-> Generating final response with Gemini...")
    try:
        response = gemini_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=system_prompt
        )
        return response.text
    except APIError as e:
        return f"Error generating response: {e}. Check your model usage."

# --- Main Chat Loop ---
if __name__ == "__main__":
    print("USDA RAG Chatbot Initialized. Type 'quit' to exit.")
    
    # IMPORTANT: Ensure your MongoDB collection has documents with:
    # 1. A 'text' field containing the scraped text chunk.
    # 2. An 'embeddings' field containing the 768-dim vector 
    #    (you must run your scraping/embedding script first!).
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            break
            
        if not user_input.strip():
            continue

        final_answer = generate_rag_response(user_input)
        print("\nAI:")
        print(final_answer)
        print("-" * 50 + "\n")

    mongo_client.close()
    print("Chatbot closed.")