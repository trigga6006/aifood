import React from 'react';
import './Sidebar.css';

const Sidebar = ({ activeItem, onItemClick }) => {
  const menuItems = [
    { id: 'dashboard', icon: 'fas fa-home', label: 'Dashboard' },
    { id: 'menu', icon: 'fas fa-utensils', label: 'Menu Management' },
    { id: 'hours', icon: 'far fa-clock', label: 'Hours & Operations' },
    { id: 'dietary', icon: 'fas fa-leaf', label: 'Dietary Information' },
    { id: 'specials', icon: 'fas fa-percentage', label: 'Specials & Promotions' },
    { id: 'beverages', icon: 'fas fa-glass-martini-alt', label: 'Beverage Menu' },
    { id: 'accessibility', icon: 'fas fa-wheelchair', label: 'Accessibility Features' },
    { id: 'location', icon: 'fas fa-map-marker-alt', label: 'Location & Directions' },
    { id: 'photos', icon: 'fas fa-camera', label: 'Photos & Gallery' },
    { id: 'faqs', icon: 'fas fa-question-circle', label: 'FAQs' },
    { id: 'settings', icon: 'fas fa-cog', label: 'Settings' },
    { id: 'analytics', icon: 'fas fa-chart-line', label: 'Analytics' }
  ];

  return (
    <div className="sidebar">
      {menuItems.map((item) => (
        <div
          key={item.id}
          className={`sidebar-item ${activeItem === item.id ? 'active' : ''}`}
          onClick={() => onItemClick(item.id)}
        >
          <i className={item.icon}></i>
          <span>{item.label}</span>
        </div>
      ))}
    </div>
  );
};

export default Sidebar;