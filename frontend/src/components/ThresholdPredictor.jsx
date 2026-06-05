import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import '../styles/ThresholdPredictor.css';

function ThresholdPredictor() {
  const { getAuthHeader } = useAuth();
  const [selectedImage, setSelectedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [threshold, setThreshold] = useState(0.25);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleImageChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setSelectedImage(file);
    const reader = new FileReader();
    reader.onloadend = () => {
      setImagePreview(reader.result);
      setResult(null);
      setError(null);
    };
    reader.readAsDataURL(file);
  };

  const handlePredict = async () => {
    if (!selectedImage) {
      setError('Please select an image first');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedImage);
      formData.append('confidence_threshold', threshold);

      const response = await fetch(
        'http://localhost:8000/features/predict_with_threshold',
        {
          method: 'POST',
          headers: getAuthHeader(),
          body: formData
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      console.error('Prediction error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="threshold-predictor-container">
      <h2 className="threshold-title">🎚️ Confidence Threshold Predictor</h2>

      <div className="threshold-content">
        <div className="threshold-controls">
          <div className="control-group">
            <label className="control-label">
              Confidence Threshold: <span className="threshold-value">{threshold.toFixed(2)}</span>
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={threshold}
              onChange={(e) => setThreshold(parseFloat(e.target.value))}
              className="threshold-slider"
              disabled={loading}
            />
            <div className="threshold-hints">
              <span className="hint-low">0.0 (Detect All)</span>
              <span className="hint-high">1.0 (Strict)</span>
            </div>
          </div>

          <div className="control-group">
            <label className="control-label">Select Image</label>
            <div className="file-input-wrapper">
              <input
                type="file"
                accept="image/*"
                onChange={handleImageChange}
                className="file-input"
                disabled={loading}
                id="threshold-file-input"
              />
              <label htmlFor="threshold-file-input" className="file-label">
                {selectedImage ? selectedImage.name : 'Choose Image...'}
              </label>
            </div>
          </div>

          <button
            className="dashboard-button primary-button threshold-button"
            onClick={handlePredict}
            disabled={!selectedImage || loading}
          >
            {loading ? '⏳ Processing...' : '🔍 Predict'}
          </button>
        </div>

        {imagePreview && !result && (
          <div className="threshold-preview">
            <h3>Input Image</h3>
            <img src={imagePreview} alt="Preview" className="threshold-image" />
          </div>
        )}

        {error && (
          <div className="threshold-error">
            <h3>❌ Error</h3>
            <p>{error}</p>
          </div>
        )}

        {result && (
          <div className="threshold-results">
            <div className="results-images">
              <div className="result-image-container">
                <h3>Annotated Result</h3>
                <img src={result.output_image} alt="Result" className="threshold-image" />
              </div>
            </div>

            <div className="results-summary">
              <div className="summary-card">
                <h3>📊 Detection Results</h3>
                <div className="summary-stats">
                  <div className="summary-stat">
                    <span className="stat-label">Threshold Used:</span>
                    <span className="stat-value">{result.confidence_threshold.toFixed(2)}</span>
                  </div>
                  <div className="summary-stat">
                    <span className="stat-label">Objects Detected:</span>
                    <span className="stat-value">{result.count}</span>
                  </div>
                </div>

                {result.count > 0 ? (
                  <div className="detections-list">
                    <h4>Detected Objects:</h4>
                    <ul>
                      {result.detections.map((det, idx) => (
                        <li key={idx}>
                          <span className="det-class">{det.class.toUpperCase()}</span>
                          <span className="det-confidence">{(det.confidence * 100).toFixed(1)}%</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                ) : (
                  <p className="no-detections">No objects detected at this threshold</p>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default ThresholdPredictor;
