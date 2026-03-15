import React, { useRef } from 'react';
import '../styles/ImageUploader.css';

/**
 * ImageUploader Component
 * Handles image file selection and preview display
 * 
 * Props:
 * - onImageSelect: callback function when an image is selected
 * - selectedImage: the currently selected image (URL or File object)
 */
const ImageUploader = ({ onImageSelect, selectedImage }) => {
  const fileInputRef = useRef(null);

  /**
   * Handles file input change event
   * Reads the selected file and calls the onImageSelect callback
   */
  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file && (file.type === 'image/jpeg' || file.type === 'image/png' || file.type === 'image/jpg')) {
      onImageSelect(file);
    } else {
      alert('Please upload a valid image file (JPG or PNG)');
    }
  };

  /**
   * Triggers the file input click when upload button is clicked
   */
  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="image-uploader">
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        accept="image/jpeg,image/png,image/jpg"
        style={{ display: 'none' }}
      />
      <button 
        className="upload-button" 
        onClick={handleUploadClick}
        type="button"
      >
        {selectedImage ? 'Change Image' : 'Upload Image'}
      </button>
    </div>
  );
};

export default ImageUploader;

