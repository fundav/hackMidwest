import React, { useEffect } from 'react';
import Chatbot from './Chatbot'; // Import your new component
import './App.css'; // Assuming you keep the default CSS file

function App() {
  useEffect(() => {
    document.title = 'USDA Chatbot'; // dynamic title
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <Chatbot />
      </header>
    </div>
  );
}

export default App;