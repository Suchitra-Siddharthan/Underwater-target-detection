import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import '../styles/Analytics.css';

function Analytics() {
  const { getAuthHeader } = useAuth();
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Define the 4 species in order
  const SPECIES_ORDER = ['echinus', 'scallop', 'holothurian', 'starfish'];

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch('http://localhost:8000/features/analytics/summary', {
        headers: getAuthHeader()
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch analytics: ${response.status}`);
      }

      const data = await response.json();
      setAnalytics(data);
    } catch (err) {
      console.error('Analytics error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="analytics-container">
        <div className="analytics-loading">Loading analytics...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="analytics-container">
        <div className="analytics-error">
          <h3>Error Loading Analytics</h3>
          <p>{error}</p>
          <button className="dashboard-button primary-button" onClick={fetchAnalytics}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  // Sort class_counts by the defined species order
  const sortedClassCounts = {};
  SPECIES_ORDER.forEach(species => {
    sortedClassCounts[species] = analytics?.class_counts?.[species] || 0;
  });

  return (
    <div className="analytics-container">
      <h2 className="analytics-title">Detection Analytics Dashboard</h2>

      <div className="analytics-stats-grid">
        <div className="analytics-stat-card">
          <div className="stat-icon">🎯</div>
          <div className="stat-content">
            <h3 className="stat-label">Total Detections</h3>
            <p className="stat-value">{analytics?.total_detections || 0}</p>
          </div>
        </div>

        <div className="analytics-stat-card">
          <div className="stat-icon">🏆</div>
          <div className="stat-content">
            <h3 className="stat-label">Most Detected Species</h3>
            <p className="stat-value">{analytics?.most_detected_class || 'N/A'}</p>
          </div>
        </div>

        <div className="analytics-stat-card">
          <div className="stat-icon">📈</div>
          <div className="stat-content">
            <h3 className="stat-label">Average Confidence</h3>
            <p className="stat-value">{((analytics?.average_confidence || 0) * 100).toFixed(1)}%</p>
          </div>
        </div>
      </div>

      <div className="analytics-breakdown">
        <h3 className="breakdown-title">📋 Species Detection Breakdown</h3>

        <div className="breakdown-list">
          {Object.entries(sortedClassCounts).map(([className, count]) => {
            const percentage = analytics.total_detections > 0
              ? ((count / analytics.total_detections) * 100).toFixed(1)
              : 0;

            // Capitalize first letter
            const displayName = className.charAt(0).toUpperCase() + className.slice(1);

            return (
              <div key={className} className="breakdown-item">
                <div className="breakdown-label">
                  <span className="class-name">{displayName}</span>
                  <span className="class-count">{count}</span>
                </div>
                <div className="breakdown-bar">
                  <div
                    className="breakdown-fill"
                    style={{ width: `${percentage}%` }}
                  />
                </div>
                <span className="percentage">{percentage}%</span>
              </div>
            );
          })}
        </div>
      </div>

      <button className="dashboard-button primary-button" onClick={fetchAnalytics}>
        🔄 Refresh Analytics
      </button>

      <div className="analytics-note">
        <p>
          📝 <strong>Note:</strong> Analytics displays data from your detection history (non-deleted items).
          Only the 4 primary marine species are tracked: Echinus, Scallop, Holothurian, and Starfish.
        </p>
      </div>
    </div>
  );
}

export default Analytics;
