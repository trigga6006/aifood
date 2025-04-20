// This is the script restaurants would add to their websites
(function() {
    // Create container for the chatbot
    const container = document.createElement('div');
    container.id = 'ai-restaurant-chatbot';
    document.body.appendChild(container);
    
    // Get restaurant ID from the script tag data attribute
    const scripts = document.getElementsByTagName('script');
    const currentScript = scripts[scripts.length - 1];
    const restaurantId = currentScript.getAttribute('data-restaurant-id');
    
    if (!restaurantId) {
      console.error('Restaurant ID is required. Add data-restaurant-id attribute to the script tag.');
      return;
    }
    
    // Load chatbot styles
    const style = document.createElement('link');
    style.rel = 'stylesheet';
    style.href = 'https://yourdomain.com/chatbot/style.css';
    document.head.appendChild(style);
    
    // Load the chatbot script
    const chatbotScript = document.createElement('script');
    chatbotScript.src = 'https://yourdomain.com/chatbot/bundle.js';
    chatbotScript.onload = function() {
      // Initialize the chatbot with the restaurant ID
      window.RestaurantAI.init(container, restaurantId);
    };
    document.head.appendChild(chatbotScript);
  })();