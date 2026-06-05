import React, { useState } from 'react';
import { jsPDF } from 'jspdf';
import './styles/Global.css';
import './styles/Dashboard.css';
import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './components/Login';
import SignUp from '././components/SignUp';
import ImageUploader from './components/ImageUploader';
import OutputViewer from './components/OutputViewer';
import History from './components/History';
import Loader from './components/Loader';
import Analytics from './components/Analytics';
import ConfidenceThresholdSlider from './components/ConfidenceThresholdSlider';

function AppContent() {
  const { isAuthenticated, logout, getAuthHeader } = useAuth();
  const [currentPage, setCurrentPage] = useState('login');
  const [selectedImage, setSelectedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [outputImage, setOutputImage] = useState(null);
  const [detectionResults, setDetectionResults] = useState([]);
  const [allDetectionResults, setAllDetectionResults] = useState([]); // Store original detections
  const [marineSummary, setMarineSummary] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentHistoryId, setCurrentHistoryId] = useState(null);
  const [confidenceThreshold, setConfidenceThreshold] = useState(0.25); // Default threshold
  const [isLoadedFromHistory, setIsLoadedFromHistory] = useState(false); // Track if loaded from history

  const handleLogin = () => {
    setCurrentPage('main');
  };

  const handleSignUp = () => {
    setCurrentPage('main');
  };

  // Filter detections based on confidence threshold
  const getFilteredDetections = (allDetections, threshold) => {
    return allDetections.filter(detection => detection.confidence >= threshold);
  };

  // Handle threshold change - only update threshold state
  // The slider component handles filtering internally
  const handleThresholdChange = (newThreshold) => {
    setConfidenceThreshold(newThreshold);
    // Note: Detection Summary shows all detections unchanged
    // Only the Filtered Detections section inside slider updates
  };

  // Load detection from history
  const handleLoadFromHistory = (historyItem) => {
    setImagePreview(historyItem.output_image_base64);
    setOutputImage(historyItem.output_image_base64);
    setCurrentHistoryId(historyItem.id);
    setMarineSummary(historyItem.marine_summary || '');
    setIsLoadedFromHistory(true);
    setConfidenceThreshold(0.25); // Reset to default threshold

    // Format detections for display
    const formattedDetections = (historyItem.detections || []).map(detection => ({
      class: detection.class_name || detection.class,
      confidence: detection.confidence
    }));

    setAllDetectionResults(formattedDetections);
    setDetectionResults(formattedDetections);
    setCurrentPage('main');
  };

  const handleImageSelect = (file) => {
    const imageUrl = URL.createObjectURL(file);
    setSelectedImage(file);
    setImagePreview(imageUrl);
    setOutputImage(null);
    setDetectionResults([]);
    setAllDetectionResults([]);
    setIsLoadedFromHistory(false);
    setConfidenceThreshold(0.25); // Reset threshold
  };

  const handleDetect = async () => {
    if (!selectedImage) {
      alert('Please upload an image first');
      return;
    }

    setIsProcessing(true);

    try {
      const formData = new FormData();
      formData.append('file', selectedImage);

      const response = await fetch('http://localhost:8000/predict', {
        method: 'POST',
        headers: getAuthHeader(),
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        if (response.status === 401) {
          alert('Session expired. Please login again.');
          logout();
          setCurrentPage('login');
          return;
        }
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      if (data.success) {
        setOutputImage(data.output_image);
        setCurrentHistoryId(data.history_id || null);
        const rawSummary = data.marine_summary || '';
        const cleanedSummary = rawSummary
          .replace(/^Marine Ecosystem Insight:\s*/i, '')
          .replace(/Image Quality Assessment:[\s\S]*$/i, '')
          .trim();
        setMarineSummary(cleanedSummary);

        const formattedDetections = data.detections.map(detection => ({
          class: detection.class,
          confidence: detection.confidence
        }));

        setAllDetectionResults(formattedDetections);
        setDetectionResults(formattedDetections);
        setIsLoadedFromHistory(false);
        setConfidenceThreshold(0.25); // Reset to default threshold
      } else {
        throw new Error('Prediction failed');
      }
    } catch (error) {
      console.error('Detection failed:', error);
      alert(`Detection failed: ${error.message}. Please make sure the backend server is running on http://localhost:8000`);
      setOutputImage(null);
      setDetectionResults([]);
      setAllDetectionResults([]);
      setMarineSummary('');
      setCurrentHistoryId(null);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDownloadImage = async () => {
    if (!currentHistoryId) {
      if (outputImage) {
        const link = document.createElement('a');
        link.href = outputImage;
        link.download = 'detection_output.jpg';
        link.click();
      }
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/history/${currentHistoryId}/download/image`, {
        headers: getAuthHeader()
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `detection_${currentHistoryId}.jpg`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        alert('Failed to download image');
      }
    } catch (error) {
      alert(`Download failed: ${error.message}`);
    }
  };

  const toDataUrl = async (src) => {
    if (!src) return null;
    if (src.startsWith('data:')) return src;
    try {
      const response = await fetch(src);
      const blob = await response.blob();
      return await new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(blob);
      });
    } catch (error) {
      console.error('Failed to convert image to data URL', error);
      return null;
    }
  };

  const handleDownloadPdf = async () => {
    if (!outputImage || detectionResults.length === 0) {
      alert('No detection report available to export.');
      return;
    }

    try {
      const doc = new jsPDF('p', 'mm', 'a4');
      const pageWidth = doc.internal.pageSize.getWidth();
      const pageHeight = doc.internal.pageSize.getHeight();
      const margin = 20;
      let y = margin;

      const ensureSpace = (needed) => {
        if (y + needed > pageHeight - margin) {
          doc.addPage();
          y = margin;
        }
      };

      // Title
      doc.setFontSize(18);
      doc.setFont('helvetica', 'bold');
      doc.text('Underwater Target Detection Report', pageWidth / 2, y, { align: 'center' });
      y += 15;

      // Detection Image
      const imgDataUrl = await toDataUrl(outputImage);
      if (imgDataUrl) {
        const imgWidth = pageWidth - 2 * margin;
        const imgHeight = (imgWidth * 3) / 4; // Assume 4:3 aspect ratio, adjust if needed
        ensureSpace(imgHeight + 10);
        doc.addImage(imgDataUrl, 'JPEG', margin, y, imgWidth, imgHeight);
        y += imgHeight + 10;
      }

      // Detection Summary
      ensureSpace(30);
      doc.setFontSize(14);
      doc.setFont('helvetica', 'bold');
      doc.text('Detection Summary', margin, y);
      y += 8;

      // Confidence Threshold Used
      ensureSpace(15);
      doc.setFontSize(11);
      doc.setFont('helvetica', 'normal');
      doc.text(`Confidence Threshold Used: ${confidenceThreshold.toFixed(2)}`, margin, y);
      y += 8;

      // Table header
      ensureSpace(20);
      doc.setFontSize(12);
      doc.setFont('helvetica', 'normal');
      doc.text('Object', margin, y);
      doc.text('Confidence', pageWidth - margin, y, { align: 'right' });
      y += 5;

      // Table line
      doc.setLineWidth(0.5);
      doc.line(margin, y, pageWidth - margin, y);
      y += 5;

      // Table rows
      detectionResults.forEach((result) => {
        ensureSpace(10);
        const pct = `${(result.confidence * 100).toFixed(1)}%`;
        doc.text(String(result.class), margin, y);
        doc.text(pct, pageWidth - margin, y, { align: 'right' });
        y += 6;
      });
      y += 10;

      // Marine Ecosystem Insight
      doc.setFontSize(14);
      doc.setFont('helvetica', 'bold');
      ensureSpace(10);
      doc.text('Marine Ecosystem Insight', margin, y);
      y += 8;

      doc.setFontSize(12);
      doc.setFont('helvetica', 'normal');
      const summaryLines = doc.splitTextToSize(marineSummary, pageWidth - 2 * margin);
      ensureSpace(summaryLines.length * 5 + 10);
      doc.text(summaryLines, margin, y);
      y += summaryLines.length * 5 + 10;

      // Footer
      doc.setFontSize(10);
      doc.setFont('helvetica', 'normal');
      const timestamp = new Date().toLocaleString();
      doc.text(`Timestamp: ${timestamp}`, margin, y);
      y += 5;
      doc.text('System Name: Underwater Target Detection System', margin, y);

      doc.save('underwater_detection_report.pdf');
    } catch (error) {
      console.error('Failed to generate PDF', error);
      alert('Failed to generate PDF report.');
    }
  };

  if (!isAuthenticated) {
    if (currentPage === 'signup') {
      return (
        <SignUp 
          onSignUp={handleSignUp} 
          onBackToLogin={() => setCurrentPage('login')} 
        />
      );
    }
    
    return (
      <Login 
        onLogin={handleLogin}
        onShowSignUp={() => setCurrentPage('signup')}
      />
    );
  }

  if (currentPage === 'history') {
    return (
      <div className="app-dashboard">
        <header className="dashboard-header">
          <h1 className="dashboard-title">Underwater Target Detection</h1>
          <div className="header-actions">
            <button
              className="dashboard-button"
              onClick={() => setCurrentPage('main')}
            >
              Detection
            </button>
            <button
              className="dashboard-button"
              onClick={() => setCurrentPage('analytics')}
            >
              Analytics
            </button>
            <button
              className="dashboard-button logout-button"
              onClick={() => { logout(); setCurrentPage('login'); }}
            >
              Logout
            </button>
          </div>
        </header>
        <main className="dashboard-main">
          <History onLoadDetection={handleLoadFromHistory} />
        </main>
      </div>
    );
  }

  if (currentPage === 'analytics') {
    return (
      <div className="app-dashboard">
        <header className="dashboard-header">
          <h1 className="dashboard-title">Underwater Target Detection</h1>
          <div className="header-actions">
            <button
              className="dashboard-button"
              onClick={() => setCurrentPage('main')}
            >
              Detection
            </button>
            <button
              className="dashboard-button"
              onClick={() => setCurrentPage('history')}
            >
              History
            </button>
            <button
              className="dashboard-button logout-button"
              onClick={() => { logout(); setCurrentPage('login'); }}
            >
              Logout
            </button>
          </div>
        </header>
        <main className="dashboard-main">
          <Analytics />
        </main>
      </div>
    );
  }

  if (currentPage === 'threshold') {
    // Redirect to main - threshold is now integrated there
    setCurrentPage('main');
    return null;
  }

  return (
    <div className="app-dashboard">
      <header className="dashboard-header">
        <h1 className="dashboard-title">Underwater Target Detection</h1>
        <div className="header-actions">
          <button
            className="dashboard-button"
            onClick={() => setCurrentPage('history')}
          >
            History
          </button>
          <button
            className="dashboard-button"
            onClick={() => setCurrentPage('analytics')}
          >
            Analytics
          </button>
          <button
            className="dashboard-button logout-button"
            onClick={() => { logout(); setCurrentPage('login'); }}
          >
            Logout
          </button>
        </div>
      </header>

      <main className="dashboard-main">
        <section className="action-bar">
          <ImageUploader 
            onImageSelect={handleImageSelect}
            selectedImage={imagePreview}
          />
          <button 
            className="dashboard-button primary-button"
            onClick={handleDetect}
            disabled={!selectedImage || isProcessing}
          >
            {isProcessing ? 'Processing...' : 'Detect Targets'}
          </button>
        </section>

        {isProcessing && (
          <section className="loading-panel">
            <Loader />
          </section>
        )}

        {!isProcessing && imagePreview && !outputImage && (
          <section className="image-output-panels single-panel">
            <div className="image-panel input-panel">
              <h2 className="panel-title">Input Image</h2>
              <div className="image-display-container">
                <img 
                  src={imagePreview} 
                  alt="Input" 
                  className="responsive-image"
                />
              </div>
            </div>
          </section>
        )}

        {!isProcessing && imagePreview && outputImage && (
          <section className="image-output-panels">
            <div className="image-panel input-panel">
              <h2 className="panel-title">Input Image</h2>
              <div className="image-display-container">
                <img 
                  src={imagePreview} 
                  alt="Input" 
                  className="responsive-image"
                />
              </div>
            </div>
            <div className="image-panel output-panel">
              <h2 className="panel-title">Detection Output</h2>
              <div className="image-display-container">
                <img 
                  src={outputImage} 
                  alt="Detection output" 
                  className="responsive-image"
                />
              </div>
            </div>
          </section>
        )}

        {outputImage && detectionResults.length > 0 && !isProcessing && (
          <section className="detection-summary-section">
            <div className="detection-results-wrapper">
              <div className="detection-summary-card-standalone">
                <OutputViewer
                  detectionResults={detectionResults}
                />
                <div className="download-actions">
                  <button
                    className="dashboard-button small-button"
                    onClick={handleDownloadImage}
                  >
                    🖼 Download Image
                  </button>
                  <button
                    className="dashboard-button small-button"
                    onClick={handleDownloadPdf}
                  >
                    📄 Download PDF
                  </button>
                </div>
              </div>
              <ConfidenceThresholdSlider
                threshold={confidenceThreshold}
                onThresholdChange={handleThresholdChange}
                allDetections={allDetectionResults}
              />
            </div>
            {marineSummary && (
              <div className="marine-summary-card">
                <h3 className="marine-summary-title">Marine Ecosystem Insight</h3>
                <pre className="marine-summary-text" style={{ whiteSpace: 'pre-wrap' }}>
                  {marineSummary}
                </pre>
              </div>
            )}
          </section>
        )}
      </main>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;

