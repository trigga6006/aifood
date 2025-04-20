// This file will handle all API calls to your backend
const API_URL = process.env.NODE_ENV === 'production' 
  ? 'https://api.yourdomain.com' 
  : 'http://localhost:5000';

export const sendMessage = async (message, restaurantId) => {
  try {
    const response = await fetch(`${API_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        restaurantId
      }),
    });
    
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error sending message:', error);
    return {
      message: "Sorry, I'm having trouble connecting to the server. Please try again later.",
      error: true
    };
  }
};

export const getRestaurantInfo = async (restaurantId) => {
  try {
    const response = await fetch(`${API_URL}/api/restaurant/${restaurantId}`);
    
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching restaurant info:', error);
    return null;
  }
};