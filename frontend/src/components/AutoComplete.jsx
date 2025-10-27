import React, { useState, useEffect } from 'react';
import { getAllMedicines } from '../utils/api';

function AutoComplete({ value, onChange, onSelect }) {
  const [suggestions, setSuggestions] = useState([]);
  const [allMedicines, setAllMedicines] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);

  useEffect(() => {
    const fetchMedicines = async () => {
      try {
        const data = await getAllMedicines();
        setAllMedicines(data.medicines || []);
      } catch (error) {
        console.error('Failed to fetch medicines:', error);
      }
    };
    fetchMedicines();
  }, []);

  useEffect(() => {
    if (value.length > 0) {
      const filtered = allMedicines.filter(med =>
        med.toLowerCase().includes(value.toLowerCase())
      ).slice(0, 5);
      setSuggestions(filtered);
      setShowSuggestions(filtered.length > 0);
    } else {
      setSuggestions([]);
      setShowSuggestions(false);
    }
  }, [value, allMedicines]);

  const handleSelect = (medicine) => {
    onSelect(medicine);
    setShowSuggestions(false);
  };

  return (
    <div className="relative">
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Type medicine name..."
        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
      />
      
      {showSuggestions && (
        <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-48 overflow-y-auto">
          {suggestions.map((medicine, index) => (
            <div
              key={index}
              onClick={() => handleSelect(medicine)}
              className="px-4 py-2 hover:bg-blue-50 cursor-pointer text-gray-700"
            >
              {medicine}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default AutoComplete;
