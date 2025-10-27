import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

export const queryMedicine = async (query) => {
  const response = await axios.post(`${API_BASE_URL}/query`, { query });
  return response.data;
};

export const uploadImage = async (imageFile) => {
  const formData = new FormData();
  formData.append('image', imageFile);
  
  const response = await axios.post(`${API_BASE_URL}/image`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
  return response.data;
};

export const getAllMedicines = async () => {
  const response = await axios.get(`${API_BASE_URL}/medicines`);
  return response.data;
};

export const getMedicine = async (name) => {
  const response = await axios.get(`${API_BASE_URL}/medicine/${name}`);
  return response.data;
};

export const getAgentsStatus = async () => {
  const response = await axios.get(`${API_BASE_URL}/agents/status`);
  return response.data;
};
