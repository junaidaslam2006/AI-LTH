import React, { useState } from 'react';
import { uploadImage } from '../utils/api';

function ImageUploader() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      setPreview(URL.createObjectURL(file));
      setResult(null);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setLoading(true);
    setError(null);

    try {
      const response = await uploadImage(selectedFile);
      setResult(response);
    } catch (err) {
      console.error('Upload error:', err);
      const errorMessage = err.response?.data?.message || err.response?.data?.suggestion || err.message || 'Failed to process image. Please try again.';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-dark-bg-start/50 backdrop-blur-md rounded-2xl shadow-glow-green p-6 border border-primary/20">
        <h2 className="text-2xl font-bold text-primary mb-4">Upload Medicine Image</h2>
        
        {/* File Input */}
        <div className="mb-6">
          <label className="block w-full">
            <div className="border-2 border-dashed border-primary/40 rounded-2xl p-8 text-center hover:border-primary hover:shadow-glow-green transition-all cursor-pointer bg-dark-bg-end/30">
              <input
                type="file"
                accept="image/*"
                onChange={handleFileSelect}
                className="hidden"
              />
              <div className="text-gray-300">
                <svg className="mx-auto h-12 w-12 text-primary" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                  <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
                <p className="mt-2 text-white">Click to upload medicine image</p>
                <p className="text-sm text-gray-400">PNG, JPG up to 10MB</p>
              </div>
            </div>
          </label>
        </div>

        {/* Preview */}
        {preview && (
          <div className="mb-6">
            <img src={preview} alt="Preview" className="max-h-64 mx-auto rounded-2xl shadow-glow-green border border-primary/30" />
            <button
              onClick={handleUpload}
              disabled={loading}
              className="mt-4 w-full px-6 py-3 bg-primary text-white rounded-xl hover:bg-accent hover:shadow-glow-green-lg disabled:bg-gray-600 transition-all transform hover:scale-105"
            >
              {loading ? 'Processing...' : 'Analyze Image'}
            </button>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="mb-6 p-4 bg-red-900/50 border border-red-500/50 text-red-200 rounded-xl">
            {error}
          </div>
        )}

        {/* Result */}
        {result && (
          <div className="bg-dark-bg-end/50 border border-primary/20 rounded-2xl p-6 space-y-4">
            <h3 className="text-xl font-bold text-primary">📸 Image Analysis Result</h3>
            
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

export default ImageUploader;
