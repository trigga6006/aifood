import React from 'react';

const ChatMessage = ({ message }) => {
  const { text, sender } = message;
  
  return (
    <div className={`chat-message ${sender}`}>
      <div className="message-content">
        {text}
      </div>
    </div>
  );
};

export default ChatMessage;