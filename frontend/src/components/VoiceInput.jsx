import React, { useState } from 'react';

function VoiceInput({ onTranscript }) {
  const [listening, setListening] = useState(false);
  const [supported, setSupported] = useState(true);

  const startListening = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      setSupported(false);
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    
    recognition.lang = 'en-US';
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = () => {
      setListening(true);
    };

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      onTranscript(transcript);
      setListening(false);
    };

    recognition.onerror = () => {
      setListening(false);
    };

    recognition.onend = () => {
      setListening(false);
    };

    recognition.start();
  };

  if (!supported) {
    return null;
  }

  return (
    <button
      onClick={startListening}
      disabled={listening}
      className={`px-4 py-3 rounded-lg transition ${
        listening
          ? 'bg-red-500 text-white animate-pulse'
          : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
      }`}
      title="Voice input"
    >
      {listening ? '🎤 Listening...' : '🎤'}
    </button>
  );
}

export default VoiceInput;
