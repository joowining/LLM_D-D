import React from 'react';
import { Message as MessageType } from './ChatContainer';
import './Message.css';

interface MessageProps {
  message: MessageType;
}

const Message: React.FC<MessageProps> = ({ message }) => {
  const formatTime = (timestamp: Date) => {
    return timestamp.toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <div className={`message ${message.isOwnMessage ? 'own-message' : 'other-message'}`}>
      <div className="message-content">
        <div className="message-header">
          <span className="message-sender">{message.sender}</span>
          <span className="message-time">{formatTime(message.timestamp)}</span>
        </div>
        <div className="message-text">{message.text}</div>
      </div>
    </div>
  );
};

export default Message;