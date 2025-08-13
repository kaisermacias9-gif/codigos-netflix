import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API_BASE = `${BACKEND_URL}/api`;

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// API functions
export const subscribersApi = {
  // Get all subscribers
  getAll: async () => {
    const response = await api.get('/subscribers');
    return response.data;
  },

  // Create new subscriber
  create: async (subscriberData) => {
    const response = await api.post('/subscribers', subscriberData);
    return response.data;
  },

  // Get subscriber by ID
  getById: async (id) => {
    const response = await api.get(`/subscribers/${id}`);
    return response.data;
  },

  // Update subscriber
  update: async (id, updateData) => {
    const response = await api.put(`/subscribers/${id}`, updateData);
    return response.data;
  },

  // Delete subscriber
  delete: async (id) => {
    const response = await api.delete(`/subscribers/${id}`);
    return response.data;
  }
};

export const statsApi = {
  // Get dashboard statistics
  get: async () => {
    const response = await api.get('/stats');
    return response.data;
  }
};

export const messagesApi = {
  // Send message to subscriber
  send: async (messageData) => {
    const response = await api.post('/send-message', messageData);
    return response.data;
  }
};

export const servicesApi = {
  // Get available streaming services
  getAll: async () => {
    const response = await api.get('/services');
    return response.data;
  }
};

// Health check
export const healthCheck = async () => {
  try {
    const response = await api.get('/');
    return response.data;
  } catch (error) {
    throw new Error('Backend not available');
  }
};

export default api;