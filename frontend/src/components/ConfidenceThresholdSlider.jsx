import React from 'react';
import '../styles/ConfidenceThresholdSlider.css';

/**
 * Confidence Threshold Slider Component
 * Displays an interactive slider to filter detections by confidence level
 * Shows filtered detections below the slider
 *
 * Props:
 * - threshold: Current threshold value (0-1)
 * - onThresholdChange: Callback function when threshold changes
 * - allDetections: All original detections from inference
 */
const ConfidenceThresholdSlider = ({ threshold, onThresholdChange, allDetections = [] }) => {
  const handleSliderChange = (e) => {
    const value = parseFloat(e.target.value);
    onThresholdChange(value);
  };

  // Calculate filtered detections based on current threshold
  const filteredDetections = allDetections.filter(
    (detection) => detection.confidence >= threshold
  );

  const getClassIcon = (label) => {
    const name = String(label || '').toLowerCase();
    if (name.includes('echinus')) return '🟣';
    if (name.includes('starfish')) return '⭐';
    if (name.includes('holothurian')) return '🟩';
    if (name.includes('scallop')) return '🟡';
    return '🔹';
  };

  const getConfidenceClass = (percentage) => {
    if (percentage >= 75) return 'confidence-high';
    if (percentage >= 50) return 'confidence-mid';
    return 'confidence-low';
  };

  return (
    <div className="confidence-threshold-container">
      {/* Slider Section */}
      <div className="slider-section">
        <div className="threshold-header">
          <h3 className="threshold-title">🎚️ Confidence Filter</h3>
        </div>

        <div className="threshold-content">
          <div className="threshold-visualization">
            <div className="threshold-slider-wrapper">
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={threshold}
                onChange={handleSliderChange}
                className="threshold-slider-input"
              />
              <div className="threshold-track-background" />
            </div>
          </div>

          <div className="threshold-info">
            <div className="threshold-value-display">
              <span className="threshold-label">Current Threshold:</span>
              <span className="threshold-value">{threshold.toFixed(2)}</span>
            </div>
            <p className="threshold-hint">
              {threshold < 0.25 && "🔓 Show All (More detections, lower accuracy)"}
              {threshold >= 0.25 && threshold < 0.5 && "⚖️ Balanced (Recommended)"}
              {threshold >= 0.5 && threshold < 0.75 && "🔒 Selective (Higher accuracy)"}
              {threshold >= 0.75 && "🔐 Strict (Only high-confidence detections)"}
            </p>
          </div>

          <div className="threshold-scale">
            <div className="scale-item">
              <span className="scale-label">Low</span>
              <span className="scale-value">0.0</span>
            </div>
            <div className="scale-item">
              <span className="scale-label">Medium</span>
              <span className="scale-value">0.5</span>
            </div>
            <div className="scale-item">
              <span className="scale-label">High</span>
              <span className="scale-value">1.0</span>
            </div>
          </div>
        </div>
      </div>

      {/* Filtered Detections Section */}
      <div className="filtered-detections-section">
        <h3 className="filtered-detections-title">
          📋 Filtered Detections ({filteredDetections.length})
        </h3>

        {filteredDetections.length === 0 ? (
          <div className="no-filtered-detections">
            <p>No detections meet the current threshold.</p>
            <p className="hint-text">Try lowering the threshold to see more results.</p>
          </div>
        ) : (
          <div className="filtered-detections-list">
            {filteredDetections.map((detection, index) => {
              const percentage = Number((detection.confidence * 100).toFixed(1));

              return (
                <div key={index} className="filtered-detection-item">
                  <div className="detection-name">
                    <span className="detection-icon">{getClassIcon(detection.class)}</span>
                    <span className="detection-label">{detection.class}</span>
                  </div>
                  <div className="detection-confidence-text">
                    Confidence: {percentage}%
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default ConfidenceThresholdSlider;
