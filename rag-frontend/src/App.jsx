import React from 'react';
import Chatbot from './Chatbot'; // Import your new component
import './App.css'; // Assuming you keep the default CSS file

function App() {
  return (
    <div className="App">
      <header className="App-header">
        {/* Your main Chatbot component */}
        <Chatbot />
      </header>
    </div>
  );
}

export default App;