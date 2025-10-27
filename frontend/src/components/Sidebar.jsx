import React, { useState, useEffect } from 'react';

function Sidebar({ onNewChat, currentChatId, onSelectChat }) {
  const [chatHistory, setChatHistory] = useState([]);

  // Load chat history from localStorage on mount
  useEffect(() => {
    const savedHistory = localStorage.getItem('ai_lth_chat_history');
    if (savedHistory) {
      setChatHistory(JSON.parse(savedHistory));
    }
  }, []);

  // Save chat history to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('ai_lth_chat_history', JSON.stringify(chatHistory));
  }, [chatHistory]);

  const handleDeleteChat = (chatId, e) => {
    e.stopPropagation();
    setChatHistory(prev => prev.filter(c => c.id !== chatId));
    
    // If deleting current chat, trigger new chat
    if (currentChatId === chatId) {
      onNewChat();
    }
  };

  const handleNewChat = () => {
    onNewChat();
  };

  return (
    <div className="w-64 bg-sidebar-bg border-r border-primary/10 flex flex-col h-screen animate-slide-in">
      {/* Header */}
      <div className="p-4 border-b border-primary/10">
        <h1 className="font-orbitron text-2xl font-bold text-primary tracking-wider">
          AI-LTH
        </h1>
        <p className="text-xs text-gray-400 mt-1">Medicine Transparency</p>
      </div>

      {/* New Chat Button */}
      <div className="p-4">
        <button
          onClick={handleNewChat}
          className="w-full px-4 py-3 bg-primary/10 hover:bg-primary/20 border border-primary/30 hover:border-primary text-white rounded-xl flex items-center justify-center gap-2 transition-all duration-300 hover:shadow-glow-green group"
        >
          <svg 
            className="w-5 h-5 group-hover:rotate-90 transition-transform duration-300" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          <span className="font-medium">New Chat</span>
        </button>
      </div>

      {/* Chat History */}
      <div className="flex-1 overflow-y-auto px-4">
        <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
          Chat History
        </h3>
        {chatHistory.length === 0 ? (
          <div className="text-center py-8 text-gray-500 text-sm">
            No chat history yet
          </div>
        ) : (
          <div className="space-y-2">
            {chatHistory.map((chat) => (
              <div
                key={chat.id}
                onClick={() => onSelectChat && onSelectChat(chat.id)}
                className={`relative p-3 rounded-lg cursor-pointer transition-all duration-200 group ${
                  currentChatId === chat.id
                    ? 'bg-primary/20 border border-primary/40'
                    : 'bg-sidebar-hover/50 hover:bg-sidebar-hover border border-transparent hover:border-primary/20'
                }`}
              >
                <div className="flex items-start gap-2">
                  <svg 
                    className="w-4 h-4 text-gray-500 group-hover:text-primary transition-colors mt-0.5 flex-shrink-0" 
                    fill="none" 
                    stroke="currentColor" 
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                  </svg>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-200 truncate group-hover:text-white transition-colors">
                      {chat.title}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">{chat.timestamp}</p>
                  </div>
                  <button
                    onClick={(e) => handleDeleteChat(chat.id, e)}
                    className="opacity-0 group-hover:opacity-100 p-1.5 hover:bg-red-500/20 rounded transition-all"
                    title="Delete chat"
                  >
                    <svg className="w-4 h-4 text-gray-400 hover:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-primary/10">
        <div className="flex items-center gap-3 p-3 rounded-lg bg-sidebar-hover/30">
          <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center border border-primary/30">
            <span className="text-xs font-bold text-primary">AI</span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-200 truncate">Medicine Bot</p>
            <p className="text-xs text-gray-500">Always here to help</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Sidebar;
