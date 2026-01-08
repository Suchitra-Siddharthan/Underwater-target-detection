import React from 'react';
import '../styles.css';

/**
 * OutputViewer Component
 * Displays the detection results including output image and detection details
 * 
 * Props:
 * - outputImage: URL of the processed/output image (with bounding boxes)
 * - detectionResults: Array of detection objects with class and confidence
 */
const OutputViewer = ({ outputImage, detectionResults }) => {
  // Mock detection results - will be replaced with actual API response
  // Format: [{ class: 'Starfish', confidence: 0.92 }, ...]
  
  if (!outputImage && (!detectionResults || detectionResults.length === 0)) {
    return null;
  }

  return (
    <div className="output-viewer">
      {outputImage && (
        <div className="output-image-container">
          <img 
            src={outputImage} 
            alt="Detection output" 
            className="output-image"
          />
        </div>
      )}
      
      {detectionResults && detectionResults.length > 0 && (
        <div className="detection-details">
          <h3>Detection Results</h3>
          <div className="results-list">
            {detectionResults.map((result, index) => (
              <div key={index} className="result-item">
                <span className="result-label">Object:</span>
                <span className="result-value">{result.class}</span>
                <span className="result-label">Confidence:</span>
                <span className="result-value">{(result.confidence * 100).toFixed(2)}%</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default OutputViewer;

