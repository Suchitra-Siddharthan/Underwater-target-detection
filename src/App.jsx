import React, { useState } from 'react';
import './styles.css';
import ImageUploader from './components/ImageUploader';
import OutputViewer from './components/OutputViewer';
import Loader from './components/Loader';

/**
 * Main App Component
 * 
 * This is the root component of the Underwater Target Detection application.
 * 
 * CURRENT IMPLEMENTATION:
 * - Frontend-only with mock/dummy detection results
 * - No backend API integration
 * - Simulates ML model inference with dummy data
 * 
 * FUTURE INTEGRATION:
 * - Backend API endpoint will be integrated here
 * - ML model inference (YOLO) will be called via API
 * - Real detection results will replace mock data
 */
function App() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [outputImage, setOutputImage] = useState(null);
  const [detectionResults, setDetectionResults] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);

  /**
   * Handles image selection from the ImageUploader component
   * Creates a preview URL for the selected image
   */
  const handleImageSelect = (file) => {
    const imageUrl = URL.createObjectURL(file);
    setSelectedImage(file);
    setImagePreview(imageUrl);
    // Reset previous results when new image is uploaded
    setOutputImage(null);
    setDetectionResults([]);
  };

  /**
   * Simulates the detection process
   * 
   * TODO: Replace this function with actual API call to backend
   * Example API integration:
   * 
   * const handleDetect = async () => {
   *   setIsProcessing(true);
   *   const formData = new FormData();
   *   formData.append('image', selectedImage);
   *   
   *   try {
   *     const response = await fetch('http://localhost:8000/api/detect', {
   *       method: 'POST',
   *       body: formData
   *     });
   *     const data = await response.json();
   *     setOutputImage(data.outputImage);
   *     setDetectionResults(data.detections);
   *   } catch (error) {
   *     console.error('Detection failed:', error);
   *     alert('Detection failed. Please try again.');
   *   } finally {
   *     setIsProcessing(false);
   *   }
   * };
   */
  const handleDetect = () => {
    if (!selectedImage) {
      alert('Please upload an image first');
      return;
    }

    setIsProcessing(true);

    // Simulate API processing delay (2-3 seconds)
    setTimeout(() => {
      // MOCK DATA: These will be replaced with actual API response
      // For now, we'll use the same image as output (in real implementation,
      // backend will return image with bounding boxes drawn)
      setOutputImage(imagePreview);

      // MOCK DETECTION RESULTS: Replace with actual API response
      // In production, this will come from YOLO model inference
      const mockDetections = [
        { class: 'Starfish', confidence: 0.92 },
        { class: 'Fish', confidence: 0.87 },
        { class: 'Coral', confidence: 0.75 }
      ];
      
      setDetectionResults(mockDetections);
      setIsProcessing(false);
    }, 2500);
  };

  return (
    <div className="App">
      <header className="app-header">
        <h1>Underwater Target Detection</h1>
        <p className="subtitle">Using Deep Learning</p>
      </header>

      <main className="app-main">
        <section className="input-section">
          <h2>Input Image</h2>
          <ImageUploader 
            onImageSelect={handleImageSelect}
            selectedImage={imagePreview}
          />
          {imagePreview && (
            <div className="input-image-container">
              <img 
                src={imagePreview} 
                alt="Input" 
                className="input-image"
              />
            </div>
          )}
        </section>

        <section className="action-section">
          <button 
            className="detect-button" 
            onClick={handleDetect}
            disabled={!selectedImage || isProcessing}
          >
            {isProcessing ? 'Processing...' : 'Detect Underwater Targets'}
          </button>
        </section>

        {isProcessing && (
          <section className="loading-section">
            <Loader />
          </section>
        )}

        {!isProcessing && (outputImage || detectionResults.length > 0) && (
          <section className="output-section">
            <h2>Detection Output</h2>
            <OutputViewer 
              outputImage={outputImage}
              detectionResults={detectionResults}
            />
          </section>
        )}
      </main>

      <footer className="app-footer">
        <p>B.E CSE Creative and Innovative Project</p>
        <p className="note">Note: Currently using mock detection results. Backend integration pending.</p>
      </footer>
    </div>
  );
}

export default App;

