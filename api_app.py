from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ragService import get_rag_answer # <--- Imports your core RAG function

# 1. Initialize the FastAPI application
app = FastAPI(title="USDA RAG Chatbot API")

# 2. Configure CORS (Crucial for frontend communication)
# *WARNING*: Using "*" (wildcard) is easy for development, but specify 
# your frontend's exact URL (e.g., "http://localhost:3000") in a real deployment.
origins = [
    "*", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

# 3. Define the Pydantic model for the incoming JSON data
# This validates that the user request body has a field named 'query'
class UserQuery(BaseModel):
    query: str
    
# 4. Define the API endpoint that your frontend will call
# The endpoint is POST /chat
@app.post("/chat")
def chat_endpoint(user_query: UserQuery):
    """
    Receives a user query, calls the RAG service, and returns the AI's response.
    """
    
    # Extract the query string from the validated Pydantic model
    question = user_query.query
    
    # Call the core RAG function defined in rag_service.py
    answer = get_rag_answer(question)
    
    # Return the AI response as a JSON object
    return {"response": answer}

# End of api_app.py