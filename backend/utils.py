"""
Utility functions for image processing and inference
"""

import cv2
import numpy as np
from PIL import Image
import io
import base64
from fastapi import UploadFile, HTTPException
from pathlib import Path

# Try to import YOLO, handle DLL errors gracefully
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except OSError as e:
    if "DLL" in str(e) or "WinError 1114" in str(e):
        print("\n" + "="*70)
        print("ERROR: PyTorch DLL loading failed!")
        print("This is a common issue with Microsoft Store Python on Windows.")
        print("="*70 + "\n")
    YOLO_AVAILABLE = False
    YOLO = None
except Exception as e:
    print(f"Warning: Could not import YOLO: {e}")
    YOLO_AVAILABLE = False
    YOLO = None

# Global model variable (will be set from main.py)
model = None
MODEL_PATH = Path("model/model1.pt")

def set_model(yolo_model, yolo_available):
    """Set the YOLO model from main.py"""
    global model, YOLO_AVAILABLE
    model = yolo_model
    YOLO_AVAILABLE = yolo_available
    print(f"DEBUG: set_model called - YOLO_AVAILABLE={yolo_available}, model={'loaded' if model is not None else 'None'}")

def process_image(image_file: UploadFile) -> tuple:
    """
    Process uploaded image and return numpy array
    
    Returns:
        tuple: (image_array, original_filename)
    """
    image_bytes = image_file.file.read()
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if image is None:
        raise ValueError("Could not decode image")
    
    return image, image_file.filename

def run_inference(image: np.ndarray) -> tuple:
    """
    Run YOLOv8 inference on image
    
    Returns:
        tuple: (annotated_image, detections_list)
    """
    if not YOLO_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="YOLO not available. Please fix PyTorch DLL error."
        )
    
    if model is None:
        raise HTTPException(
            status_code=500,
            detail="Model not loaded. Please check model path and PyTorch installation."
        )
    
    # Run inference
    results = model(image)
    result = results[0]
    
    # Extract detections
    detections = []
    if result.boxes is not None:
        for box in result.boxes:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])
            class_name = result.names[class_id]
            
            detections.append({
                "class": class_name,
                "confidence": confidence
            })
    
    # Get annotated image (with bounding boxes)
    annotated_image = result.plot()
    
    return annotated_image, detections

def image_to_base64(image: np.ndarray) -> str:
    """
    Convert numpy array image to base64 string
    
    Returns:
        str: Base64 encoded image
    """
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(image_rgb)
    buffered = io.BytesIO()
    pil_image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/jpeg;base64,{img_str}"
