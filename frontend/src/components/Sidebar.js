import React from 'react';
import './Sidebar.css';

const Sidebar = ({ activeItem, onItemClick }) => {
  // Organize menu items by category
  const managementItems = [
    { id: 'dashboard', icon: '📊', label: 'Dashboard' },
    { id: 'menu', icon: '🍽️', label: 'Menu Management' },
    { id: 'hours', icon: '📅', label: 'Hours & Operations' },
    { id: 'orders', icon: '🛒', label: 'Orders' },
    { id: 'customers', icon: '👥', label: 'Customers' }
  ];
  
  const configItems = [
    { id: 'settings', icon: '⚙️', label: 'Settings' },
    { id: 'integrations', icon: '🔄', label: 'Integrations' },
    { id: 'ai-assistant', icon: '🤖', label: 'AI Assistant' }
  ];
  
  const analyticsItems = [
    { id: 'analytics', icon: '📈', label: 'Reports' },
    { id: 'feedback', icon: '💬', label: 'Feedback' }
  ];
  
  const supportItems = [
    { id: 'faqs', icon: '❓', label: 'Help Center' },
    { id: 'contact', icon: '📞', label: 'Contact' }
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <a className="logo" href="#">X<span>XXX</span></a>
        <div className="restaurant-name">Lumière Bistro</div>
      </div>
      
      <nav className="sidebar-menu">
        <div className="menu-title">Management</div>
        <ul className="menu-list">
          {managementItems.map((item) => (
            <li key={item.id}>
              <div
                className={`menu-item ${activeItem === item.id ? 'active' : ''}`}
                onClick={() => onItemClick(item.id)}
              >
                <span className="menu-icon">{item.icon}</span>
                <span className="menu-text">{item.label}</span>
              </div>
            </li>
          ))}
        </ul>
        
        <div className="menu-title">Configuration</div>
        <ul className="menu-list">
          {configItems.map((item) => (
            <li key={item.id}>
              <div
                className={`menu-item ${activeItem === item.id ? 'active' : ''}`}
                onClick={() => onItemClick(item.id)}
              >
                <span className="menu-icon">{item.icon}</span>
                <span className="menu-text">{item.label}</span>
              </div>
            </li>
          ))}
        </ul>
        
        <div className="menu-title">Analytics</div>
        <ul className="menu-list">
          {analyticsItems.map((item) => (
            <li key={item.id}>
              <div
                className={`menu-item ${activeItem === item.id ? 'active' : ''}`}
                onClick={() => onItemClick(item.id)}
              >
                <span className="menu-icon">{item.icon}</span>
                <span className="menu-text">{item.label}</span>
              </div>
            </li>
          ))}
        </ul>
        
        <div className="menu-title">Support</div>
        <ul className="menu-list">
          {supportItems.map((item) => (
            <li key={item.id}>
              <div
                className={`menu-item ${activeItem === item.id ? 'active' : ''}`}
                onClick={() => onItemClick(item.id)}
              >
                <span className="menu-icon">{item.icon}</span>
                <span className="menu-text">{item.label}</span>
              </div>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
};

export default Sidebar;