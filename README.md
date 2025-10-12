# 🇺🇸 USDA Programs RAG Chatbot

# hackMidwest
PROBLEM STATEMENT
USDA Rural Development Chatbot: Develop a public-facing AI chatbot designed to provide information about USDA Rural Development programs and their eligibility criteria. This chatbot will streamline public interactions with RD Programs.
Users should be able to describe their situation, and the chatbot will suggest relevant RD programs, including links to the appropriate pages.
Additionally, it will answer basic questions about the programs using publicly available data and offer contact information or next steps for potential applicants.
Participants will gain experience in curating knowledge bases, exploring different methods of LLM data ingestion + QA (Cache-augmented generation, retrieval-augmented generation, etc.), as well as potentially employing a frontend UI.

Judging
MongoDB
40% working demo
30% solves a real world problem
20% value of solution
10 % presentation

Code quality will not be judged. Each judge will be able to rate each application on a scale of zero to ten (0-10). Your application will be judged based on a few criteria:
Value, impact, usefulness
 innovative, unique, and are excited about idea
 Realness, completeness, is it actually built or an MVP

## 🎯 Project Overview & Purpose

This project implements a **Retrieval-Augmented Generation (RAG)** chatbot designed to provide accurate, grounded answers to user inquiries about various U.S. Department of Agriculture (USDA) programs.

The system significantly reduces the risk of Large Language Model (LLM) **hallucinations** by retrieving contextually relevant information from an authoritative **MongoDB Atlas Vector Database** before generating a final response using a **Google Gemini** model.

**Key Features:**
* **Semantic Search:** Uses vector embeddings to understand the *meaning* of a user's question, not just keywords.
* **Grounding:** Answers are strictly based on pre-scraped USDA program documentation.
* **Scalable Backend:** Utilizes **FastAPI** for a high-performance, asynchronous web API service.
* **Secure Configuration:** Uses the `.env` file and environment variables to manage sensitive credentials securely.

***

## 💻 Technology Stack

This application is built on a modern, decoupled full-stack architecture.

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **LLM / Embeddings** | **Google Gemini API** (`text-embedding-004`, `gemini-2.5-flash`) | Generates vector embeddings and the final chat response. |
| **Vector Database** | **MongoDB Atlas** | Stores text chunks and their corresponding vector embeddings (`embedding` field). |
| **Backend API** | **Python**, **FastAPI**, **Uvicorn** | High-performance API routing and logic server. |
| **Frontend / GUI** | **HTML, CSS, JavaScript** (`fetch` API) | Provides the user interface and handles communication with the backend via HTTP POST requests. |

***

## 📁 Project Structure

The project is structured to separate the core RAG logic, the API serving layer, and the frontend presentation.

'''
/hackMidwest
├── .env              # Configuration: API Keys (Gemini), MongoDB URI, and application settings.
├── README.md         # Project documentation (this file).
├── embed_data.py     # Data Loader: Script to generate embeddings and populate the MongoDB collection.
├── rag_service.py    # Core RAG Logic: Contains the main 'get_rag_answer' function for retrieval and generation.
├── api_app.py        # API Service: FastAPI entry point, defines the '/chat' endpoint, and handles CORS.
└── frontend/         # Frontend GUI Directory
    └── index.html    # Client-side chat interface and JavaScript API calls.
'''