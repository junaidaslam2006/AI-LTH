import React, { useState, useRef } from 'react';
import { uploadImage } from '../utils/api';

function CameraCapture() {
  const [streaming, setStreaming] = useState(false);
  const [captured, setCaptured] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [debugInfo, setDebugInfo] = useState('');
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);

  const startCamera = async () => {
    setError(null);
    setDebugInfo('Requesting camera access...');
    
    try {
      console.log('🎥 Starting camera...');
      
      // Set streaming first to render the video element
      setStreaming(true);
      
      // Wait a tiny bit for React to render the video element
      await new Promise(resolve => setTimeout(resolve, 50));
      
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { facingMode: 'environment' }
      });
      
      console.log('✅ Stream obtained:', stream);
      setDebugInfo('Camera access granted! Loading video...');
      
      streamRef.current = stream;
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        console.log('✅ Stream assigned to video element');
        
        setDebugInfo('Video streaming active!');
        
        // Try to play
        videoRef.current.play().catch(e => console.log('Play attempt:', e));
      } else {
        setDebugInfo('ERROR: Video element not found!');
        setStreaming(false);
      }
    } catch (err) {
      console.error('❌ Camera error:', err);
      setError(`Camera error: ${err.message}`);
      setDebugInfo(`Error: ${err.message}`);
      setStreaming(false);
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      setStreaming(false);
    }
  };

  const captureImage = () => {
    const canvas = canvasRef.current;
    const video = videoRef.current;
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0);
    
    const imageData = canvas.toDataURL('image/jpeg');
    setCaptured(imageData);
    stopCamera();
  };

  const analyzeCapture = async () => {
    if (!captured) return;

    setLoading(true);
    setError(null);

    try {
      // Convert base64 to blob
      const response = await fetch(captured);
      const blob = await response.blob();
      const file = new File([blob], 'capture.jpg', { type: 'image/jpeg' });
      
      const result = await uploadImage(file);
      setResult(result);
    } catch (err) {
      console.error('Analysis error:', err);
      const errorMessage = err.response?.data?.message || err.response?.data?.suggestion || err.message || 'Failed to analyze image. Please try again.';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const retake = () => {
    setCaptured(null);
    setResult(null);
    setError(null);
    startCamera();
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-dark-bg-start/50 backdrop-blur-md rounded-2xl shadow-glow-green p-6 border border-primary/20">
        <h2 className="text-2xl font-bold text-primary mb-4">Live Camera Scan</h2>

        {/* Camera View */}
        <div className="mb-6">
          {!streaming && !captured && (
            <div className="text-center py-12 bg-dark-bg-end/30 rounded-2xl border border-primary/20">
              <button
                onClick={startCamera}
                className="px-6 py-3 bg-primary text-white rounded-xl hover:bg-accent hover:shadow-glow-green-lg transition-all transform hover:scale-105"
              >
                📷 Start Camera
              </button>
              <p className="text-gray-400 text-sm mt-4">Click to activate camera</p>
            </div>
          )}

          {streaming && (
            <div className="relative bg-black rounded-2xl overflow-hidden min-h-[400px]">
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className="w-full h-full object-cover rounded-2xl"
                style={{ minHeight: '400px' }}
              />
              <div className="absolute bottom-6 left-0 right-0 flex justify-center gap-4">
                <button
                  onClick={captureImage}
                  className="px-8 py-4 bg-primary text-white font-bold rounded-full shadow-glow-green-lg hover:bg-accent transition-all animate-glow-pulse text-lg"
                >
                  📸 Capture Photo
                </button>
                <button
                  onClick={stopCamera}
                  className="px-6 py-4 bg-red-600 text-white font-bold rounded-full hover:bg-red-700 transition-all"
                >
                  ❌ Stop
                </button>
              </div>
            </div>
          )}

          {captured && (
            <div>
              <img src={captured} alt="Captured" className="w-full rounded-2xl shadow-glow-green border border-primary/30 mb-4" />
              <div className="flex space-x-2">
                <button
                  onClick={analyzeCapture}
                  disabled={loading}
                  className="flex-1 px-6 py-3 bg-primary text-white rounded-xl hover:bg-accent hover:shadow-glow-green-lg disabled:bg-gray-600 disabled:cursor-not-allowed transition-all transform hover:scale-105"
                >
                  {loading ? 'Analyzing...' : 'Analyze'}
                </button>
                <button
                  onClick={retake}
                  className="px-6 py-3 bg-dark-bg-end/80 border border-primary/30 text-gray-300 rounded-xl hover:bg-dark-bg-end hover:border-primary transition-all"
                >
                  Retake
                </button>
              </div>
            </div>
          )}

          <canvas ref={canvasRef} className="hidden" />
        </div>

        {/* Debug Info */}
        {debugInfo && (
          <div className="mb-4 p-3 bg-blue-900/30 border border-blue-500/30 text-blue-200 rounded-xl text-sm">
            🔍 Debug: {debugInfo}
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="mb-6 p-4 bg-red-900/50 border border-red-500/50 text-red-200 rounded-xl">
            {error}
          </div>
        )}

        {/* Result - Same as ImageUploader */}
        {result && (
          <div className="bg-dark-bg-end/50 border border-primary/20 rounded-2xl p-6 space-y-4">
            <h3 className="text-xl font-bold text-primary">📸 Camera Scan Result</h3>
            
            {/* Medicine Info */}
            <div className="border-b border-primary/30 pb-3">
              <h4 className="text-lg font-bold text-accent">{result.medicine_name}</h4>
              {result.generic_name && result.generic_name !== 'N/A' && (
                <p className="text-xs text-gray-400 mt-1">Generic: {result.generic_name}</p>
              )}
              {result.manufacturer && result.manufacturer !== 'N/A' && (
                <p className="text-xs text-gray-400">Manufacturer: {result.manufacturer}</p>
              )}
            </div>

            {/* Description */}
            {result.description && (
              <div className="bg-primary/5 p-4 rounded-xl border border-primary/20">
                <h5 className="text-sm font-semibold text-primary mb-2">📋 Overview</h5>
                <p className="text-sm text-gray-200 leading-relaxed">{result.description}</p>
              </div>
            )}

            {/* Uses */}
            {result.uses && result.uses !== 'N/A' && result.uses !== 'Information not available' && (
              <div className="bg-blue-900/20 p-4 rounded-xl border border-blue-500/20">
                <h5 className="text-sm font-semibold text-blue-300 mb-2">💊 Medical Uses</h5>
                <p className="text-sm text-gray-200 leading-relaxed">{result.uses}</p>
              </div>
            )}

            {/* Side Effects */}
            {result.side_effects && Array.isArray(result.side_effects) && result.side_effects[0] !== 'Information not available' && (
              <div className="bg-orange-900/20 p-4 rounded-xl border border-orange-500/20">
                <h5 className="text-sm font-semibold text-orange-300 mb-2">⚠️ Possible Side Effects</h5>
                <ul className="space-y-1">
                  {result.side_effects.map((effect, idx) => (
                    <li key={idx} className="text-sm text-gray-200 flex items-start gap-2">
                      <span className="text-orange-400 mt-1">•</span>
                      <span>{effect}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Warnings */}
            {result.warnings && (
              <div className="bg-red-900/20 p-4 rounded-xl border border-red-500/20">
                <h5 className="text-sm font-semibold text-red-300 mb-2">🚨 Warnings</h5>
                <p className="text-sm text-gray-200 leading-relaxed">{result.warnings}</p>
              </div>
            )}

            {/* Disclaimer */}
            {result.disclaimer && (
              <div className="p-3 bg-yellow-900/30 border border-yellow-500/30 rounded-xl text-xs text-yellow-300">
                {result.disclaimer}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default CameraCapture;
