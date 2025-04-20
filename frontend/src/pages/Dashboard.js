import React from 'react';
import Sidebar from '../components/Sidebar';
import './Dashboard.css';

const Dashboard = () => {
  const [activeItem, setActiveItem] = React.useState('dashboard');

  const handleItemClick = (itemId) => {
    setActiveItem(itemId);
    // In a real app, this would navigate to different pages or sections
    console.log(`Navigating to: ${itemId}`);
  };

  return (
    <div className="dashboard-container">
      <Sidebar activeItem={activeItem} onItemClick={handleItemClick} />
      
      <main className="main-content">
        {/* Page Header */}
        <div className="page-header">
          <h1 className="page-title">Dashboard</h1>
          <div className="header-actions">
            <button className="btn btn-outline">Last 30 Days ▼</button>
            <button className="btn">Update All Information</button>
          </div>
        </div>
        
        {/* Success Alert */}
        <div className="alert alert-success">
          <div className="alert-icon">✓</div>
          <div className="alert-content">
            <div className="alert-title">Setup Complete</div>
            <div className="alert-message">Your restaurant profile is now active. The AI assistant is ready to handle guest inquiries and reservations. Please complete all information sections for optimal AI performance.</div>
          </div>
          <button className="alert-close">×</button>
        </div>
        
        {/* Dashboard Overview Cards */}
        <div className="dashboard-grid">
          <DashboardCard 
            title="Reservations" 
            stat="38" 
            label="Total Reservations This Week" 
            trend="up" 
            trendText="12% from last week" 
            actionLink="#" 
            actionText="View Details" 
          />
          
          <DashboardCard 
            title="AI Interactions" 
            stat="124" 
            label="Guest Inquiries Handled" 
            trend="up" 
            trendText="23% from last week" 
            actionLink="#" 
            actionText="View Details" 
          />
          
          <DashboardCard 
            title="AI Knowledge Completeness" 
            stat="68%" 
            label="Training Data Completion" 
            trend="up" 
            trendText="15% from last week" 
            actionLink="#knowledge-gaps" 
            actionText="View Knowledge Gaps" 
          />
          
          <DashboardCard 
            title="Average Response Time" 
            stat="8s" 
            label="Average AI Response Time" 
            trend="up" 
            trendText="15% faster than last week" 
            actionLink="#" 
            actionText="View Report" 
          />
        </div>
        
        {/* Restaurant Profile Section would go here */}
        {/* Additional sections would go here */}
      </main>
    </div>
  );
};

// Helper component for dashboard cards
const DashboardCard = ({ title, stat, label, trend, trendText, actionLink, actionText }) => {
  return (
    <div className="dashboard-card">
      <div className="card-header">
        <h2 className="card-title">{title}</h2>
      </div>
      <div className="card-body">
        <div className="stat">{stat}</div>
        <div className="stat-label">{label}</div>
      </div>
      <div className="card-footer">
        <div className={`trend trend-${trend}`}>
          {trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→'} {trendText}
        </div>
        <a className="card-action" href={actionLink}>{actionText} →</a>
      </div>
    </div>
  );
};

export default Dashboard;