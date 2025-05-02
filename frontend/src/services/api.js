// src/services/api.js (previously saved as app.js)
import axios from 'axios';

// Base URL for API calls - use port 5000 for your Flask server
const API_BASE_URL = 'http://localhost:5000';

// Restaurant API calls
export const getRestaurant = async (restaurantId) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/restaurant/${restaurantId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching restaurant:', error);
    throw error;
  }
};

// Update this to match your working implementation
export const sendChatMessage = async (restaurantId, message, sessionId = null) => {
  try {
    // Note the different endpoint and parameter names
    const response = await axios.post(`${API_BASE_URL}/api/chat`, {
      message: message,                   // Match your Flask endpoint parameters
      restaurantId: restaurantId || 'demo-restaurant'  // Match your Flask endpoint parameters
    });
    
    // Reformat the response to match what the component expects
    return {
      response: response.data.message,   // Map from data.message to response.response
      session_id: sessionId || 'new-session'
    };
  } catch (error) {
    console.error('Error sending message to chatbot:', error);
    throw error;
  }
};