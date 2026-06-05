"""
QUICK TEST GUIDE - New Features
Test the newly integrated features with these commands
"""

# ============================================================================
# AVAILABLE ENDPOINTS (After Integration)
# ============================================================================

# Feature 1: Analytics Dashboard
GET /features/analytics/summary

# Feature 2: Confidence Threshold Prediction
POST /features/predict_with_threshold

# Feature 3: Already integrated, use with custom routers
# Functions available from: features.heatmap_feature


# ============================================================================
# CURL COMMANDS - Test in Terminal
# ============================================================================

# 1. Get analytics summary (requires JWT token)
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  http://localhost:8000/features/analytics/summary


# 2. Test confidence threshold prediction
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "file=@path/to/your/image.jpg" \
  -F "confidence_threshold=0.5" \
  http://localhost:8000/features/predict_with_threshold


# ============================================================================
# PYTHON TEST SCRIPT - test_features.py
# ============================================================================

"""
Save this as backend/test_features.py and run: python test_features.py

import requests
import json
from pathlib import Path

# Configuration
API_URL = "http://localhost:8000"
TOKEN = "YOUR_JWT_TOKEN_HERE"  # Get this from login response

headers = {
    "Authorization": f"Bearer {TOKEN}"
}

def test_analytics():
    '''Test analytics endpoint'''
    print("\\n=== Testing Analytics Feature ===")
    response = requests.get(
        f"{API_URL}/features/analytics/summary",
        headers=headers
    )
    print("Status:", response.status_code)
    print("Response:", json.dumps(response.json(), indent=2))

def test_threshold_prediction(image_path: str, threshold: float = 0.5):
    '''Test confidence threshold prediction'''
    print("\\n=== Testing Confidence Threshold Prediction ===")

    with open(image_path, "rb") as f:
        files = {"file": f}
        params = {"confidence_threshold": threshold}

        response = requests.post(
            f"{API_URL}/features/predict_with_threshold",
            headers=headers,
            files=files,
            params=params
        )

    print("Status:", response.status_code)
    data = response.json()
    print(f"Detections found: {data.get('count', 0)}")
    print(f"Threshold used: {data.get('confidence_threshold', 0)}")
    if data.get('detections'):
        print("Detections:")
        for det in data['detections']:
            print(f"  - {det['class']}: {det['confidence']:.2f}")

if __name__ == "__main__":
    # Test both features
    test_analytics()

    # Test with an image file
    image_file = "path/to/test/image.jpg"
    if Path(image_file).exists():
        test_threshold_prediction(image_file, threshold=0.5)
    else:
        print(f"\\nImage file not found: {image_file}")
        print("Please provide a valid image path")
"""


# ============================================================================
# FRONTEND INTEGRATION - React Example
# ============================================================================

"""
// Save as src/components/AnalyticsDashboard.jsx

import { useState, useEffect } from 'react';
import axios from 'axios';

export function AnalyticsDashboard() {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const token = localStorage.getItem('access_token');
        const response = await axios.get(
          'http://localhost:8000/features/analytics/summary',
          {
            headers: { Authorization: `Bearer ${token}` }
          }
        );
        setAnalytics(response.data);
      } catch (error) {
        console.error('Failed to fetch analytics:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, []);

  if (loading) return <div>Loading analytics...</div>;
  if (!analytics) return <div>Failed to load analytics</div>;

  return (
    <div className="analytics-dashboard">
      <h2>Detection Analytics</h2>

      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Detections</h3>
          <p className="stat-value">{analytics.total_detections}</p>
        </div>

        <div className="stat-card">
          <h3>Most Detected</h3>
          <p className="stat-value">{analytics.most_detected_class}</p>
        </div>

        <div className="stat-card">
          <h3>Average Confidence</h3>
          <p className="stat-value">{(analytics.average_confidence * 100).toFixed(1)}%</p>
        </div>
      </div>

      <div className="class-breakdown">
        <h3>Detection Breakdown</h3>
        <ul>
          {Object.entries(analytics.class_counts).map(([className, count]) => (
            <li key={className}>
              {className}: <strong>{count}</strong> detections
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}


// Save as src/components/ThresholdPredictor.jsx

import { useState } from 'react';
import axios from 'axios';

export function ThresholdPredictor() {
  const [image, setImage] = useState(null);
  const [threshold, setThreshold] = useState(0.25);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handlePredict = async (e) => {
    e.preventDefault();
    if (!image) return;

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', image);
      formData.append('confidence_threshold', threshold);

      const token = localStorage.getItem('access_token');
      const response = await axios.post(
        'http://localhost:8000/features/predict_with_threshold',
        formData,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'multipart/form-data'
          }
        }
      );

      setResult(response.data);
    } catch (error) {
      console.error('Prediction failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="threshold-predictor">
      <h2>Predict with Confidence Threshold</h2>

      <form onSubmit={handlePredict}>
        <div className="form-group">
          <label>Confidence Threshold: {threshold.toFixed(2)}</label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={threshold}
            onChange={(e) => setThreshold(parseFloat(e.target.value))}
          />
        </div>

        <div className="form-group">
          <input
            type="file"
            accept="image/*"
            onChange={(e) => setImage(e.target.files[0])}
          />
        </div>

        <button type="submit" disabled={!image || loading}>
          {loading ? 'Processing...' : 'Predict'}
        </button>
      </form>

      {result && (
        <div className="results">
          <img src={result.output_image} alt="Result" />
          <p>Detections: {result.count}</p>
          <ul>
            {result.detections.map((det, i) => (
              <li key={i}>
                {det.class}: {(det.confidence * 100).toFixed(1)}%
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
"""


# ============================================================================
# WHAT YOU SHOULD SEE
# ============================================================================

"""
When you run the backend now:

✅ All three feature routers are loaded
✅ New endpoints available at:
   - GET /features/analytics/summary
   - POST /features/predict_with_threshold

✅ Can be tested via:
   - FastAPI interactive docs at: http://localhost:8000/docs
   - Swagger UI at: http://localhost:8000/redoc
   - Direct API calls with your frontend

Next Steps:
1. Get a JWT token by logging in
2. Use that token to test the endpoints
3. Integrate the React components into your frontend
4. Display analytics and threshold predictions in your UI
"""
