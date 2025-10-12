import React, { useState, useRef, useEffect } from 'react';

// Configuration: Your FastAPI endpoint
const API_ENDPOINT = 'http://localhost:8000/chat';

// Structure for a single message
const initialMessages = [
  { role: 'assistant', content: 'Hello! I am your USDA Programs Assistant. Ask me a question about any program.' }
];

function Chatbot() {
  const [messages, setMessages] = useState(initialMessages);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const chatEndRef = useRef(null);

  // Scrolls to the bottom of the chat window when new messages arrive
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Handles sending the query to the FastAPI backend
  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = { role: 'user', content: input };

    // 1. Update state with user's message
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // 2. Make the POST request to the RAG API
      const response = await fetch(API_ENDPOINT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        // The payload matches the Pydantic UserQuery model in api_app.py
        body: JSON.stringify({ query: input }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      // 3. Parse the JSON response
      const result = await response.json();
      const assistantResponse = { 
        role: 'assistant', 
        // The response field is named 'response' by your FastAPI endpoint
        content: result.response 
      };

      // 4. Update state with AI's response
      setMessages((prev) => [...prev, assistantResponse]);

    } catch (error) {
      console.error('API Call Error:', error);
      const errorMessage = { 
        role: 'assistant', 
        content: `Error: Could not connect to the RAG service. Please ensure the backend is running on ${API_ENDPOINT} and check your CORS settings.` 
      };
      setMessages((prev) => [...prev, errorMessage]);
      
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={styles.chatContainer}>
      <h2>USDA Program Assistant</h2>
      
      {/* Message History */}
      <div style={styles.messageList}>
        {messages.map((msg, index) => (
          <div key={index} style={msg.role === 'user' ? styles.userMessage : styles.aiMessage}>
            <div style={styles.messageBubble}>
                <strong>{msg.role === 'user' ? 'You' : 'AI'}:</strong> {msg.content}
            </div>
          </div>
        ))}
        {/* Loading Indicator */}
        {isLoading && (
          <div style={styles.loadingMessage}>
            <div style={styles.messageBubble}>
                AI is processing your query...
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Input Form */}
      <form onSubmit={handleSend} style={styles.inputForm}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={isLoading ? "Please wait..." : "Ask about a USDA program..."}
          disabled={isLoading}
          style={styles.inputField}
        />
        <button type="submit" disabled={isLoading} style={styles.sendButton}>
          {isLoading ? 'Sending...' : 'Send'}
        </button>
      </form>
    </div>
  );
}

// Basic Inline Styles (You should replace this with a proper CSS file or library like Tailwind/MUI)
const styles = {
  chatContainer: {
    maxWidth: '600px',
    margin: '40px auto',
    padding: '20px',
    border: '1px solid #ccc',
    borderRadius: '8px',
    boxShadow: '0 4px 8px rgba(0,0,0,0.1)',
  },
  messageList: {
    height: '400px',
    overflowY: 'auto',
    marginBottom: '15px',
    paddingRight: '10px',
  },
  userMessage: {
    textAlign: 'right',
    marginBottom: '10px',
  },
  aiMessage: {
    textAlign: 'left',
    marginBottom: '10px',
  },
  messageBubble: {
    maxWidth: '80%',
    padding: '10px',
    borderRadius: '15px',
    display: 'inline-block',
    background: '#e0f7fa', // Light blue for AI
    color: '#004d40',
    fontSize: '14px'
  },
  loadingMessage: {
    textAlign: 'left',
    marginBottom: '10px',
  },
  inputForm: {
    display: 'flex',
    gap: '10px',
  },
  inputField: {
    flexGrow: 1,
    padding: '10px',
    borderRadius: '4px',
    border: '1px solid #ccc',
  },
  sendButton: {
    padding: '10px 15px',
    border: 'none',
    borderRadius: '4px',
    backgroundColor: '#007bff',
    color: 'white',
    cursor: 'pointer',
  }
};

export default Chatbot;