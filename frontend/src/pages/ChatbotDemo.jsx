import React from 'react';
import ChatWidget from '../chatbot/ChatWidget';

function ChatbotDemo() {
  return (
    <div className="chatbot-demo" style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h1>Chatbot Demo</h1>
      <p>This page demonstrates how the chatbot will appear on restaurant websites.</p>
      
      {/* Restaurant content simulation */}
      <div className="demo-content" style={{ marginTop: '40px', padding: '20px', border: '1px solid #ddd' }}>
        <h2>Sample Restaurant Content</h2>
        <p>This simulates a restaurant website where our chatbot will be embedded.</p>
        
        <div className="demo-menu" style={{ marginTop: '20px' }}>
          <h3>Sample Menu</h3>
          <ul>
            <li>Appetizer 1 - $12</li>
            <li>Main Course 1 - $25</li>
            <li>Dessert 1 - $8</li>
          </ul>
        </div>
      </div>
      
      {/* Embed the chat widget */}
      <ChatWidget restaurantId="demo-restaurant" />
    </div>
  );
}

export default ChatbotDemo;