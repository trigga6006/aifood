import React from 'react';
import { Link } from 'react-router-dom';
import './Sidebar.css';

const Sidebar = ({ activeItem, onItemClick }) => {
  // Organize menu items by category
  const managementItems = [
    { id: 'dashboard', icon: '📊', label: 'Dashboard', path: '/' },
    { id: 'menu', icon: '🍽️', label: 'Menu Management', path: '/menu' },
    { id: 'hours', icon: '📅', label: 'Hours & Operations', path: '/hours' },
    { id: 'orders', icon: '🛒', label: 'Orders', path: '/orders' },
    { id: 'customers', icon: '👥', label: 'Customers', path: '/customers' }
  ];
  
  const configItems = [
    { id: 'settings', icon: '⚙️', label: 'Settings', path: '/settings' },
    { id: 'integrations', icon: '🔄', label: 'Integrations', path: '/integrations' },
    { id: 'ai-assistant', icon: '🤖', label: 'AI Assistant', path: '/ai-assistant' },
    { id: 'chatbot-demo', icon: '💬', label: 'Chatbot Demo', path: '/chatbot-demo' } // Added new item
  ];
  
  const analyticsItems = [
    { id: 'analytics', icon: '📈', label: 'Reports', path: '/analytics' },
    { id: 'feedback', icon: '💬', label: 'Feedback', path: '/feedback' }
  ];
  
  const supportItems = [
    { id: 'faqs', icon: '❓', label: 'Help Center', path: '/faqs' },
    { id: 'contact', icon: '📞', label: 'Contact', path: '/contact' }
  ];

  // Helper function to render menu items
  const renderMenuItems = (items) => {
    return items.map((item) => (
      <li key={item.id}>
        <Link to={item.path}>
          <div
            className={`menu-item ${activeItem === item.id ? 'active' : ''}`}
            onClick={() => onItemClick(item.id)}
          >
            <span className="menu-icon">{item.icon}</span>
            <span className="menu-text">{item.label}</span>
          </div>
        </Link>
      </li>
    ));
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <a className="logo" href="#">X<span>XXX</span></a>
        <div className="restaurant-name">Lumière Bistro</div>
      </div>
      
      <nav className="sidebar-menu">
        <div className="menu-title">Management</div>
        <ul className="menu-list">
          {renderMenuItems(managementItems)}
        </ul>
        
        <div className="menu-title">Configuration</div>
        <ul className="menu-list">
          {renderMenuItems(configItems)}
        </ul>
        
        <div className="menu-title">Analytics</div>
        <ul className="menu-list">
          {renderMenuItems(analyticsItems)}
        </ul>
        
        <div className="menu-title">Support</div>
        <ul className="menu-list">
          {renderMenuItems(supportItems)}
        </ul>
      </nav>
    </aside>
  );
};

export default Sidebar;