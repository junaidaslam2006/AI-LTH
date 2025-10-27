import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import ChatBox from './components/ChatBox';
import ImageUploader from './components/ImageUploader';
import CameraCapture from './components/CameraCapture';

function App() {
  const [activeTab, setActiveTab] = useState('chat');
  const [showHero, setShowHero] = useState(true);
  const [chatResetTrigger, setChatResetTrigger] = useState(0);

  const handleNewChat = () => {
    setShowHero(true);
    setActiveTab('chat');
    setChatResetTrigger(prev => prev + 1); // Trigger reset by changing the value
  };

  const handleStartChat = () => {
    setShowHero(false);
  };

  return (
    <div className="flex h-screen overflow-hidden font-inter">
      {/* Sidebar */}
      <Sidebar onNewChat={handleNewChat} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col">
        {/* Top Bar with Tabs */}
        <div className="border-b border-primary/10 bg-black/20 backdrop-blur-sm">
          <div className="flex items-center justify-between px-8 py-3">
            <div className="flex gap-2">
              <button
                onClick={() => setActiveTab('chat')}
                className={`px-4 py-2 rounded-lg font-medium text-sm transition-all duration-300 ${
                  activeTab === 'chat'
                    ? 'bg-primary/20 text-primary border border-primary/30'
                    : 'text-gray-400 hover:text-gray-200 hover:bg-white/5'
                }`}
              >
                💬 Chat
              </button>
              <button
                onClick={() => setActiveTab('image')}
                className={`px-4 py-2 rounded-lg font-medium text-sm transition-all duration-300 ${
                  activeTab === 'image'
                    ? 'bg-primary/20 text-primary border border-primary/30'
                    : 'text-gray-400 hover:text-gray-200 hover:bg-white/5'
                }`}
              >
                � Image
              </button>
              <button
                onClick={() => setActiveTab('camera')}
                className={`px-4 py-2 rounded-lg font-medium text-sm transition-all duration-300 ${
                  activeTab === 'camera'
                    ? 'bg-primary/20 text-primary border border-primary/30'
                    : 'text-gray-400 hover:text-gray-200 hover:bg-white/5'
                }`}
              >
                � Camera
              </button>
            </div>
            <div className="flex items-center gap-2 text-xs text-gray-500">
              <div className="w-2 h-2 bg-primary rounded-full animate-glow-pulse"></div>
              <span>AI Online</span>
            </div>
          </div>
        </div>

        {/* Main Area with Hero or Chat */}
        <div className="flex-1 overflow-y-auto relative">
          {/* Back Button (when chat is active) */}
          {!showHero && activeTab === 'chat' && (
            <button
              onClick={() => setShowHero(true)}
              className="absolute top-4 left-4 z-10 px-4 py-2 bg-sidebar-bg/80 backdrop-blur border border-primary/30 text-gray-300 hover:text-white hover:border-primary rounded-lg transition-all duration-300 flex items-center gap-2 group"
            >
              <svg className="w-4 h-4 group-hover:-translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              Back to Home
            </button>
          )}
          
          {/* Hero Section (VOXA-inspired) */}
          {showHero && activeTab === 'chat' && (
            <div className="absolute inset-0 flex items-center justify-center p-8 animate-fade-in-up">
              <div className="text-center max-w-4xl">
                <h1 className="font-orbitron text-8xl font-black text-transparent bg-clip-text bg-gradient-to-r from-primary via-accent to-primary mb-6 animate-glow-intense tracking-wider">
                  AI-LTH
                </h1>
                <p className="text-2xl text-gray-300 mb-8 font-light">
                  Your smart help<br />
                  <span className="text-primary font-medium">for medicine transparency.</span>
                </p>
                <div className="grid grid-cols-3 gap-4 max-w-2xl mx-auto mb-8">
                  <div className="p-4 bg-sidebar-bg/50 backdrop-blur border border-primary/10 rounded-xl hover:border-primary/30 transition-all duration-300 hover:shadow-glow-green group">
                    <div className="text-3xl mb-2 transform group-hover:scale-110 transition-transform">💊</div>
                    <p className="text-sm text-gray-400">Medicine Info</p>
                  </div>
                  <div className="p-4 bg-sidebar-bg/50 backdrop-blur border border-primary/10 rounded-xl hover:border-primary/30 transition-all duration-300 hover:shadow-glow-green group">
                    <div className="text-3xl mb-2 transform group-hover:scale-110 transition-transform">🔍</div>
                    <p className="text-sm text-gray-400">Smart Search</p>
                  </div>
                  <div className="p-4 bg-sidebar-bg/50 backdrop-blur border border-primary/10 rounded-xl hover:border-primary/30 transition-all duration-300 hover:shadow-glow-green group">
                    <div className="text-3xl mb-2 transform group-hover:scale-110 transition-transform">🤖</div>
                    <p className="text-sm text-gray-400">AI Powered</p>
                  </div>
                </div>
                <button
                  onClick={handleStartChat}
                  className="px-8 py-4 bg-primary hover:bg-accent text-black font-bold rounded-full text-lg transition-all duration-300 hover:shadow-glow-intense transform hover:scale-105 inline-flex items-center gap-2"
                >
                  Start Chatting
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </button>
                <p className="text-xs text-gray-500 mt-6 max-w-xl mx-auto">
                  ⚠️ Educational purposes only. Not medical advice. Always consult healthcare professionals.
                </p>
              </div>
            </div>
          )}

          {/* Chat Interface */}
          {(!showHero || activeTab !== 'chat') && (
            <div className="h-full">
              {activeTab === 'chat' && <ChatBox onFirstMessage={handleStartChat} resetTrigger={chatResetTrigger} />}
              {activeTab === 'image' && <ImageUploader />}
              {activeTab === 'camera' && <CameraCapture />}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
