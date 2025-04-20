import React, { useState, useEffect, useRef } from 'react';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import './ChatStyles.css';

const ChatWidget = ({ restaurantId, theme = 'light' }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { id: 1, text: "Hello! How can I help you with your reservation or questions about our restaurant?", sender: 'bot' }
  ]);
  const messagesEndRef = useRef(null);

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  const handleSendMessage = (text) => {
    if (!text.trim()) return;
    
    // Add user message
    const newUserMessage = { id: messages.length + 1, text, sender: 'user' };
    setMessages([...messages, newUserMessage]);
    
    // Simulate bot response (this will be replaced with your actual API call)
    setTimeout(() => {
      const botResponse = { 
        id: messages.length + 2, 
        text: "Thanks for your message. I'm a placeholder response. Soon I'll be connected to an AI that can help with reservations and answer questions about the restaurant.", 
        sender: 'bot' 
      };
      setMessages(prev => [...prev, botResponse]);
    }, 1000);
  };

  // Auto-scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className={`chat-widget ${theme}`}>
      {!isOpen ? (
        <button className="chat-toggle" onClick={toggleChat}>
          Chat with us
        </button>
      ) : (
        <div className="chat-container">
          <div className="chat-header">
            <h3>Restaurant Assistant</h3>
            <button className="close-btn" onClick={toggleChat}>×</button>
          </div>
          <div className="chat-messages">
            {messages.map(message => (
              <ChatMessage key={message.id} message={message} />
            ))}
            <div ref={messagesEndRef} />
          </div>
          <ChatInput onSendMessage={handleSendMessage} />
        </div>
      )}
    </div>
  );
};

export default ChatWidget;