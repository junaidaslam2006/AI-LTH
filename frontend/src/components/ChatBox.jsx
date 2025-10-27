import React, { useState, useRef, useEffect } from 'react';
import { queryMedicine } from '../utils/api';
import MessageBubble from './MessageBubble';

function ChatBox({ onFirstMessage, resetTrigger }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Reset messages when resetTrigger changes (New Chat clicked)
  useEffect(() => {
    if (resetTrigger) {
      setMessages([]);
      setInput('');
    }
  }, [resetTrigger]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    // Trigger hero hide on first message
    if (messages.length === 0 && onFirstMessage) {
      onFirstMessage();
    }

    const userMessage = {
      type: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await queryMedicine(input);
      
      const aiMessage = {
        type: 'ai',
        content: response.ai_explanation || response.description || response.explanation || 'No explanation available',
        data: response,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      const errorMessage = {
        type: 'ai',
        content: error.response?.data?.message || error.response?.data?.suggestion || 'Sorry, I could not find information about that medicine. Please check the spelling or try another name.',
        error: true,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages Area - ChatGPT Style */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-3xl mx-auto px-4 py-6 space-y-6">
          {messages.map((message, index) => (
            <MessageBubble key={index} message={message} />
          ))}
          {loading && (
            <div className="flex items-center gap-2 text-gray-400 animate-fade-in-up">
              <div className="w-2 h-2 bg-primary rounded-full animate-glow-pulse"></div>
              <span className="text-sm text-gray-400">AI is analyzing...</span>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Fixed Input at Bottom - ChatGPT Style */}
      <div className="border-t border-primary/10 bg-black/20 backdrop-blur-sm">
        <div className="max-w-3xl mx-auto px-4 py-4">
          <form onSubmit={handleSubmit} className="flex gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about any medicine..."
              className="flex-1 px-5 py-3 bg-input-bg/80 border border-primary/20 rounded-full focus:outline-none focus:border-primary text-white placeholder-gray-500 transition-all"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="px-6 py-3 bg-primary hover:bg-accent text-black font-semibold rounded-full transition-all duration-300 hover:shadow-glow-green transform hover:scale-105 disabled:bg-gray-700 disabled:text-gray-500 disabled:cursor-not-allowed disabled:hover:scale-100"
            >
              {loading ? (
                <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              ) : (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              )}
            </button>
          </form>
          <p className="text-xs text-gray-600 text-center mt-2">
            AI-LTH can make mistakes. Verify important information.
          </p>
        </div>
      </div>
    </div>
  );
}

export default ChatBox;
