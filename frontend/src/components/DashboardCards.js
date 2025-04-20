import React from 'react';

function DashboardCards() {
  return (
    <div className="dashboard-grid">
      <div className="dashboard-card">
        <div className="card-header">
          <h2 className="card-title">Reservations</h2>
        </div>
        <div className="card-body">
          <div className="stat">38</div>
          <div className="stat-label">Total Reservations This Week</div>
        </div>
        <div className="card-footer">
          <div className="trend trend-up">
            ↑ 12% from last week
          </div>
          <a className="card-action" href="#">View Details →</a>
        </div>
      </div>
      
      <div className="dashboard-card">
        <div className="card-header">
          <h2 className="card-title">AI Interactions</h2>
        </div>
        <div className="card-body">
          <div className="stat">124</div>
          <div className="stat-label">Guest Inquiries Handled</div>
        </div>
        <div className="card-footer">
          <div className="trend trend-up">
            ↑ 23% from last week
          </div>
          <a className="card-action" href="#">View Details →</a>
        </div>
      </div>
      
      <div className="dashboard-card">
        <div className="card-header">
          <h2 className="card-title">AI Knowledge Completeness</h2>
        </div>
        <div className="card-body">
          <div className="stat">68%</div>
          <div className="stat-label">Training Data Completion</div>
        </div>
        <div className="card-footer">
          <div className="trend trend-up">
            ↑ 15% from last week
          </div>
          <a className="card-action" href="#knowledge-gaps">View Knowledge Gaps →</a>
        </div>
      </div>
      
      <div className="dashboard-card">
        <div className="card-header">
          <h2 className="card-title">Average Response Time</h2>
        </div>
        <div className="card-body">
          <div className="stat">8s</div>
          <div className="stat-label">Average AI Response Time</div>
        </div>
        <div className="card-footer">
          <div className="trend trend-up">
            ↑ 15% faster than last week
          </div>
          <a className="card-action" href="#">View Report →</a>
        </div>
      </div>
    </div>
  );
}

export default DashboardCards;