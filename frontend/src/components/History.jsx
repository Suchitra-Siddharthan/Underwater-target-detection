import React, { useState, useEffect } from 'react';
import { jsPDF } from 'jspdf';
import { useAuth } from '../context/AuthContext';
import '../styles/History.css';

/**
 * History Component
 * Displays user's prediction history with download, view, and delete options
 *
 * Props:
 * - onLoadDetection: Callback function to load a detection into the main page
 */
const History = ({ onLoadDetection }) => {
  const { getAuthHeader, isAuthenticated } = useAuth();
  const [history, setHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const generateSummaryFromDetections = (detections = []) => {
    const speciesOrder = ["echinus", "holothurian", "scallop", "starfish"];
    const counts = detections.reduce((acc, det) => {
      const name = (det.class_name || det.class || '').toLowerCase();
      if (speciesOrder.includes(name)) {
        acc[name] = (acc[name] || 0) + 1;
      }
      return acc;
    }, {});

    const total = Object.values(counts).reduce((sum, v) => sum + v, 0);
    if (total === 0) {
      return 'No marine organisms detected in the image.';
    }

    const dominant = Object.keys(counts).reduce((a, b) => (counts[a] >= counts[b] ? a : b));
    const parts = speciesOrder
      .filter((s) => counts[s])
      .map((s) => `${counts[s]} ${s}`);

    const countsStr = parts.length > 1 ? `${parts.slice(0, -1).join(', ')} and ${parts.slice(-1)}` : parts[0];
    return `The image reveals ${countsStr} (total: ${total} organisms), indicating a ${dominant}-dominant underwater environment. This suggests a region with active benthic marine life.`;
  };

  useEffect(() => {
    if (isAuthenticated) {
      fetchHistory();
    }
  }, [isAuthenticated]);

  /**
   * Fetch history from backend
   */
  const fetchHistory = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:8000/history/', {
        headers: {
          ...getAuthHeader(),
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setHistory(data);
      } else {
        const errorData = await response.json().catch(() => ({ detail: 'Failed to fetch history' }));
        setError(errorData.detail || 'Failed to fetch history');
      }
    } catch (error) {
      setError(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Delete a history record
   */
  const handleDelete = async (historyId) => {
    if (!window.confirm('Are you sure you want to delete this record?')) {
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/history/${historyId}`, {
        method: 'DELETE',
        headers: getAuthHeader()
      });

      if (response.ok) {
        // Remove from local state
        setHistory(history.filter(item => item.id !== historyId));
      } else {
        const errorData = await response.json().catch(() => ({ detail: 'Delete failed' }));
        alert(errorData.detail || 'Failed to delete record');
      }
    } catch (error) {
      alert(`Delete failed: ${error.message}`);
    }
  };

  /**
   * Download output image
   */
  const handleDownloadImage = async (historyId, filename) => {
    try {
      const response = await fetch(`http://localhost:8000/history/${historyId}/download/image`, {
        headers: getAuthHeader()
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `detection_${filename || historyId}.jpg`;
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

  /**
   * Download detection report as PDF for a history record
   */
  const handleDownloadPdf = async (item) => {
    if (!item) return;

    try {
      const doc = new jsPDF('p', 'mm', 'a4');
      const pageWidth = doc.internal.pageSize.getWidth();
      const pageHeight = doc.internal.pageSize.getHeight();
      let y = 20;

      doc.setFontSize(18);
      doc.text('Underwater Target Detection Report', pageWidth / 2, y, { align: 'center' });
      y += 6;

      doc.setLineWidth(0.4);
      doc.line(20, y, pageWidth - 20, y);
      y += 10;

      // Detection image (from history thumbnail/base64)
      if (item.output_image_base64) {
        let imgData = item.output_image_base64;
        if (typeof imgData === 'string' && !imgData.startsWith('data:')) {
          imgData = `data:image/jpeg;base64,${imgData}`;
        }

        const imgMaxWidth = pageWidth - 40;
        const imgHeight = (imgMaxWidth * 9) / 16; // approximate aspect ratio

        doc.setFontSize(13);
        doc.text('Detection Image', 20, y);
        y += 6;

        try {
          doc.addImage(imgData, 'JPEG', 20, y, imgMaxWidth, imgHeight, undefined, 'FAST');
          y += imgHeight + 10;
        } catch (imgError) {
          console.warn('Failed to embed history image in PDF', imgError);
        }
      }

      // Detection summary table
      doc.setFontSize(14);
      doc.text('Detection Summary', 20, y);
      y += 6;

      doc.setFontSize(11);
      doc.text('Object', 20, y);
      doc.text('Confidence', pageWidth - 55, y);
      y += 4;
      doc.setLineWidth(0.2);
      doc.line(20, y, pageWidth - 20, y);
      y += 6;

      (item.detections || []).forEach((detection) => {
        if (y > pageHeight - 60) {
          doc.addPage();
          y = 20;
          doc.setFontSize(11);
          doc.text('Object', 20, y);
          doc.text('Confidence', pageWidth - 55, y);
          y += 4;
          doc.line(20, y, pageWidth - 20, y);
          y += 6;
        }
        const pct = `${(detection.confidence * 100).toFixed(1)}%`;
        doc.text(String(detection.class_name), 20, y);
        doc.text(pct, pageWidth - 55, y);
        y += 6;
      });

      // Marine Ecosystem Insight
      const summaryText = item.marine_summary || generateSummaryFromDetections(item.detections);
      if (summaryText) {
        y += 10;
        doc.setFontSize(14);
        doc.text('Marine Ecosystem Insight', 20, y);
        y += 8;

        doc.setFontSize(11);
        const insightLines = doc.splitTextToSize(summaryText, pageWidth - 40);
        insightLines.forEach((line) => {
          if (y > pageHeight - 30) {
            doc.addPage();
            y = 20;
          }
          doc.text(line, 20, y);
          y += 6;
        });
      }

      y += 10;
      doc.setFontSize(11);
      const timestamp = formatDate(item.timestamp);
      doc.text(`Timestamp: ${timestamp}`, 20, y);
      y += 6;
      doc.text('System Name: Underwater Target Detection System', 20, y);

      doc.setFontSize(9);
      doc.text(
        'Generated by Underwater Target Detection System',
        pageWidth / 2,
        pageHeight - 10,
        { align: 'center' }
      );

      const safeName = (item.original_filename || `history_${item.id}`).replace(/\s+/g, '_');
      doc.save(`${safeName}_report.pdf`);
    } catch (error) {
      console.error('Failed to generate PDF from history', error);
      alert('Failed to generate PDF report for this record.');
    }
  };

  /**
   * Format timestamp for display
   */
  const formatDate = (timestamp) => {
    try {
      // Handle both ISO string and datetime object
      const date = timestamp instanceof Date ? timestamp : new Date(timestamp);
      
      // Check if date is valid
      if (isNaN(date.getTime())) {
        return 'Invalid date';
      }
      
      // Format as: "Jan 15, 2024, 3:45:30 PM"
      return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        second: '2-digit',
        hour12: true
      });
    } catch (error) {
      console.error('Error formatting date:', error, timestamp);
      return 'Invalid date';
    }
  };

  if (isLoading) {
    return (
      <section className="results-section">
        <h2>History</h2>
        <div className="loading-section">
          <p>Loading history...</p>
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="results-section">
        <h2>History</h2>
        <div className="loading-section">
          <p style={{ color: '#ff6b6b' }}>Error: {error}</p>
        </div>
      </section>
    );
  }

  return (
    <section className="history-dashboard-section">
      <h2 className="dashboard-panel-title">Prediction History</h2>
      {history.length === 0 ? (
        <div className="dashboard-message-card">
          <p>No history records found. Start detecting to see your history here!</p>
        </div>
      ) : (
        <div className="history-list">
          {history.map((item) => (
            <div key={item.id} className="history-item glass-card">
              <div className="history-image">
                <img 
                  src={item.output_image_base64} 
                  alt="Detection output" 
                  className="history-thumbnail"
                />
              </div>
              <div className="history-details">
                <h3 className="history-filename">{item.original_filename}</h3>
                <p className="history-date">{formatDate(item.timestamp)}</p>
                <div className="history-detections-summary">
                  {item.detections.length > 0 ? (
                    item.detections.map((detection, idx) => (
                      <span key={idx} className="detection-badge">
                        {detection.class_name}: {(detection.confidence * 100).toFixed(1)}%
                      </span>
                    ))
                  ) : (
                    <span className="detection-badge">No detections</span>
                  )}
                </div>
              </div>
              <div className="history-actions">
                <button
                  className="dashboard-button small-button download-image"
                  onClick={() => handleDownloadImage(item.id, item.original_filename)}
                  title="Download Image"
                >
                  🖼 Download Image
                </button>
                <button
                  className="dashboard-button small-button download-pdf"
                  onClick={() => handleDownloadPdf(item)}
                  title="Download PDF"
                >
                  📄 Download PDF
                </button>
                <button
                  className="dashboard-button small-button view-btn"
                  onClick={() => onLoadDetection && onLoadDetection(item)}
                  title="View Detection"
                >
                  👁️ View
                </button>
                <button
                  className="dashboard-button small-button delete-btn delete-button"
                  onClick={() => handleDelete(item.id)}
                  title="Delete"
                >
                  🗑️ Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
};

export default History;
