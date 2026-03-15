import React from 'react';
import '../styles/OutputViewer.css';

/**
 * OutputViewer Component
 * Displays the detection results in a compact table format.
 * 
 * Props:
 * - detectionResults: Array of detection objects with class and confidence
 */
const OutputViewer = ({ detectionResults }) => {
  if (!detectionResults || detectionResults.length === 0) {
    return (
      <div className="detection-summary-card-content">
        <p className="no-detections-message">No objects detected.</p>
      </div>
    );
  }

  const getConfidenceClass = (percentage) => {
    if (percentage >= 75) return 'confidence-high';
    if (percentage >= 50) return 'confidence-mid';
    return 'confidence-low';
  };

  const getClassIcon = (label) => {
    const name = String(label || '').toLowerCase();
    if (name.includes('echinus')) return '🟣';
    if (name.includes('starfish')) return '⭐';
    if (name.includes('holothurian')) return '🟩';
    if (name.includes('scallop')) return '🟡';
    return '🔹';
  };

  return (
    <div className="detection-summary-shell">
      <div className="detection-summary-header">
        <div>
          <h3 className="detection-summary-title">Detection Summary</h3>
          <div className="detection-summary-title-underline" />
        </div>
      </div>
      <div className="detection-summary-card-content">
        {detectionResults.map((result, index) => {
          const percentage = Number((result.confidence * 100).toFixed(1));
          const confidenceClass = getConfidenceClass(percentage);

          return (
            <div key={index} className="detection-row-card">
              <div className="detection-row-main">
                <div className="detection-object-info">
                  <div className="detection-object-name">
                    <span>{getClassIcon(result.class)}</span>
                    <span>{result.class}</span>
                  </div>
                  <div className="detection-confidence-text">
                    Confidence: {percentage}%
                  </div>
                </div>
              </div>
              <div className="confidence-bar-shell">
                <div
                  className={`confidence-bar-fill ${confidenceClass}`}
                  style={{ '--target-width': `${percentage}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default OutputViewer;

