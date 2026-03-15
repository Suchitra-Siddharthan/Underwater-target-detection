import React from 'react';
import '../styles/Loader.css';

/**
 * Loader Component
 * Displays a loading spinner while processing the image
 */
const Loader = () => {
  return (
    <div className="loader-container">
      <div className="spinner"></div>
      <p>Processing image...</p>
    </div>
  );
};

export default Loader;

