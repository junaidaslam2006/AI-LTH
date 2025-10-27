import React from 'react';

function MessageBubble({ message }) {
  const isUser = message.type === 'user';
  const isError = message.error;

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} animate-fade-in-up`}>
      <div
        className={`max-w-2xl rounded-2xl p-5 ${
          isUser
            ? 'bg-user-bubble text-white'
            : isError
            ? 'bg-red-900/30 text-red-200 border border-red-500/30'
            : 'bg-ai-bubble/50 backdrop-blur text-white border border-primary/10'
        }`}
      >
        {/* User message - show content as is */}
        {isUser && (
          <div className="whitespace-pre-wrap text-sm leading-relaxed">{message.content}</div>
        )}

        {/* AI Response - structured medicine explanation */}
        {!isUser && !isError && message.data && (
          <div className="space-y-4">
            {/* Medicine Name Header */}
            <div className="border-b border-primary/30 pb-3">
              <h3 className="text-lg font-bold text-accent">{message.data.medicine_name}</h3>
              {message.data.generic_name && message.data.generic_name !== 'N/A' && (
                <p className="text-xs text-gray-400 mt-1">Generic: {message.data.generic_name}</p>
              )}
              {message.data.manufacturer && message.data.manufacturer !== 'N/A' && (
                <p className="text-xs text-gray-400">Manufacturer: {message.data.manufacturer}</p>
              )}
            </div>

            {/* Description */}
            {message.data.description && (
              <div className="bg-primary/5 p-4 rounded-xl border border-primary/20">
                <h4 className="text-sm font-semibold text-primary mb-2">📋 Overview</h4>
                <p className="text-sm text-gray-200 leading-relaxed">{message.data.description}</p>
              </div>
            )}

            {/* Uses */}
            {message.data.uses && message.data.uses !== 'N/A' && message.data.uses !== 'Information not available' && (
              <div className="bg-blue-900/20 p-4 rounded-xl border border-blue-500/20">
                <h4 className="text-sm font-semibold text-blue-300 mb-2">💊 Medical Uses</h4>
                <p className="text-sm text-gray-200 leading-relaxed">{message.data.uses}</p>
              </div>
            )}

            {/* Side Effects */}
            {message.data.side_effects && message.data.side_effects.length > 0 && message.data.side_effects[0] !== 'Information not available' && (
              <div className="bg-orange-900/20 p-4 rounded-xl border border-orange-500/20">
                <h4 className="text-sm font-semibold text-orange-300 mb-2">⚠️ Possible Side Effects</h4>
                <ul className="space-y-1">
                  {Array.isArray(message.data.side_effects) ? (
                    message.data.side_effects.map((effect, idx) => (
                      <li key={idx} className="text-sm text-gray-200 flex items-start gap-2">
                        <span className="text-orange-400 mt-1">•</span>
                        <span>{effect}</span>
                      </li>
                    ))
                  ) : (
                    <li className="text-sm text-gray-200">{message.data.side_effects}</li>
                  )}
                </ul>
              </div>
            )}

            {/* Warnings */}
            {message.data.warnings && (
              <div className="bg-red-900/20 p-4 rounded-xl border border-red-500/20">
                <h4 className="text-sm font-semibold text-red-300 mb-2">🚨 Warnings</h4>
                <p className="text-sm text-gray-200 leading-relaxed">{message.data.warnings}</p>
              </div>
            )}

            {/* Disclaimer */}
            {message.data.disclaimer && (
              <div className="p-3 bg-yellow-900/30 border border-yellow-500/30 rounded-xl text-xs text-yellow-300">
                {message.data.disclaimer}
              </div>
            )}
          </div>
        )}

        {/* Error message */}
        {!isUser && isError && (
          <div className="whitespace-pre-wrap text-sm leading-relaxed">{message.content}</div>
        )}

        {/* Simple text fallback */}
        {!isUser && !isError && !message.data && (
          <div className="whitespace-pre-wrap text-sm leading-relaxed">{message.content}</div>
        )}

        <div className="text-xs mt-2 opacity-70 text-gray-400">
          {message.timestamp.toLocaleTimeString()}
        </div>
      </div>
    </div>
  );
}

export default MessageBubble;
