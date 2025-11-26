import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
//import reactIcon from './assets/react.svg';

// Configuration: Your FastAPI endpoint
const API_ENDPOINT = 'https://usda-chatbotbackend.onrender.com/';

// Structure for a single message
const initialMessages = [
  { role: 'assistant', content: 'Hello, my name is Sprout! Ask me anything about rural development programs.' }
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
      {/* Top-centered logo */}
      <div style={styles.topIconWrap}>
        <img
          src="/usda-rd-logo.png"
          alt="USDA Rural Development"
          title="USDA Rural Development"
          style={styles.topIcon}
          onError={(e) => { e.currentTarget.onerror = null; e.currentTarget.src = reactIcon; }}
        />
      </div>
      <h2 style={styles.title}>The Rural Navigator</h2>
      
      {/* Message History */}
      <div style={styles.messageList}>
        {messages.map((msg, index) => (
          <div key={index} style={msg.role === 'user' ? styles.userMessage : styles.aiMessage}>
            <div style={styles.messageBubble}>
                <strong>{msg.role === 'user' ? 'You' : 'Sprout 🌱'}:</strong>{' '}
                {/* Render message content as Markdown so *italic* and **bold** work */}
                <div style={{ display: 'inline-block', maxWidth: '100%' }}>
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
                </div>
            </div>
          </div>
        ))}
        {/* Loading Indicator */}
        {isLoading && (
          <div style={styles.loadingMessage}>
      <div style={styles.messageBubble}>
        Sprout 🌱 is processing your query...
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
    maxWidth: '900px',
    height: '80vh',
    margin: '20px auto',
    padding: '24px',
    borderRadius: '12px',
    boxShadow: '0 8px 20px rgba(0,0,0,0.15)',
    // Light green → yellow gradient background across the whole chatbox
    background: 'radial-gradient(circle, #f7f7c8 0%, #ddf4dfff 50%, #dbe3eaff 80%)',
    // Fallback solid color for older browsers
    backgroundColor: '#f7f7c8',
    display: 'flex',
    flexDirection: 'column',
  },
  // Top-right corner image styles
  // Top-centered logo styles
  topIconWrap: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: '8px',
  },
  topIcon: {
    width: '120px',
    height: 'auto',
    objectFit: 'contain',
    display: 'block',
    pointerEvents: 'none',
  },
  title: {
    textAlign: 'center',
    margin: '6px 0 14px',
  },
  messageList: {
    flexGrow: 1,
    overflowY: 'auto',
    marginBottom: '15px',
    padding: '16px',
    borderRadius: '8px',
    background: 'linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01))',
    boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.02)',
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
    maxWidth: '50%',
    padding: '10px',
    borderRadius: '15px',
    display: 'inline-block',
    background: '#eaf2f3ff', // Light blue for Sprout (original)
    color: '#004d40',
    fontSize: '14px',
    lineHeight: '1.4',
    wordBreak: 'break-word',
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
    borderRadius: '12px',
    border: '1px solid #ccc',
    background: '#ffffff',
    color: '#000000',
  },
  sendButton: {
    padding: '10px 15px',
    border: 'none',
    borderRadius: '12px',
    backgroundColor: '#1C4E9D',
    color: 'white',
    cursor: 'pointer',
  }
};

export default Chatbot;