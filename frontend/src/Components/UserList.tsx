import React from 'react';
import { User } from './ChatContainer';
import './UserList.css';

interface UserListProps {
  users: User[];
}

const UserList: React.FC<UserListProps> = ({ users }) => {
  return (
    <div className="user-list">
      <div className="user-list-header">
        <h3>Online Users ({users.filter(user => user.isOnline).length})</h3>
      </div>
      <div className="user-list-content">
        {users.map((user) => (
          <div key={user.id} className="user-item">
            <div className={`user-status ${user.isOnline ? 'online' : 'offline'}`}></div>
            <span className="user-name">{user.name}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default UserList;