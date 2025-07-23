import React, { useState } from 'react';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import UserList from './UserList';
import './ChatContainer.css';

export interface Message {
  id: string;
  text: string;
  sender: string;
  timestamp: Date;
  isOwnMessage: boolean;
}

export interface User {
  id: string;
  name: string;
  isOnline: boolean;
}

const ChatContainer: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [users] = useState<User[]>([
    { id: '1', name: 'Alice', isOnline: true },
    { id: '2', name: 'Bob', isOnline: false },
    { id: '3', name: 'Charlie', isOnline: true },
  ]);

  const handleSendMessage = (text: string) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      text,
      sender: 'You',
      timestamp: new Date(),
      isOwnMessage: true,
    };
    setMessages(prev => [...prev, newMessage]);
  };

  return (
    <div className="chat-container">
      <div className="chat-sidebar">
        <UserList users={users} />
      </div>
      <div className="chat-main">
        <div className="chat-header">
          <h2>Chat Room</h2>
        </div>
        <MessageList messages={messages} />
        <MessageInput onSendMessage={handleSendMessage} />
      </div>
    </div>
  );
};

export default ChatContainer;