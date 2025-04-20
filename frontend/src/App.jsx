import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import ChatbotDemo from './pages/ChatbotDemo';

function App() {
  const [activeItem, setActiveItem] = useState('dashboard');

  const handleItemClick = (itemId) => {
    setActiveItem(itemId);
  };

  return (
    <Router>
      <div style={{ display: 'flex' }}>
        <Sidebar activeItem={activeItem} onItemClick={handleItemClick} />
        <div className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/chatbot-demo" element={<ChatbotDemo />} />
            {/* Add more routes as needed */}
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;