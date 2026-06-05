"""
FastAPI Backend for Underwater Coral Detection using YOLOv8
FALLBACK VERSION - Handles DLL errors gracefully
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import cv2
import numpy as np
from PIL import Image
import io
import base64
import os
from pathlib import Path
from typing import List, Dict
import uvicorn

# Try to import YOLO, handle errors gracefully
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except Exception as e:
    print(f"Warning: Could not import YOLO: {e}")
    print("Please install PyTorch properly. See FIX_DLL_ERROR.md")
    YOLO_AVAILABLE = False
    YOLO = None

# Initialize FastAPI app
app = FastAPI(title="Underwater Coral Detection API", version="1.0.0")

# CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create necessary directories
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")
MODEL_PATH = Path("model/best.pt")

UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Load YOLOv8 model
model = None
if YOLO_AVAILABLE:
    print("Loading YOLOv8 model...")
    try:
        if MODEL_PATH.exists():
            model = YOLO(str(MODEL_PATH))
            print(f"Model loaded successfully from {MODEL_PATH}")
        else:
            print(f"Warning: Model file not found at {MODEL_PATH}")
    except Exception as e:
        print(f"Error loading model: {e}")
        print("Please check FIX_DLL_ERROR.md for troubleshooting")
        model = None
else:
    print("YOLO not available. Please fix PyTorch installation.")


def process_image(image_file: UploadFile) -> tuple:
    """Process uploaded image and return numpy array"""
    image_bytes = image_file.file.read()
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if image is None:
        raise ValueError("Could not decode image")
    
    return image, image_file.filename


def run_inference(image: np.ndarray) -> tuple:
    """Run YOLOv8 inference on image"""
    if not YOLO_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="YOLO model not available. Please check PyTorch installation. See FIX_DLL_ERROR.md"
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
    
    # Get annotated image
    annotated_image = result.plot()
    
    return annotated_image, detections


def image_to_base64(image: np.ndarray) -> str:
    """Convert numpy array image to base64 string"""
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(image_rgb)
    buffered = io.BytesIO()
    pil_image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/jpeg;base64,{img_str}"


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Underwater Coral Detection API",
        "status": "running",
        "yolo_available": YOLO_AVAILABLE,
        "model_loaded": model is not None,
        "error": "DLL error detected. Please see FIX_DLL_ERROR.md" if not YOLO_AVAILABLE else None
    }


@app.get("/health")
async def health():
    """Health check with detailed status"""
    return {
        "status": "healthy" if YOLO_AVAILABLE else "degraded",
        "yolo_available": YOLO_AVAILABLE,
        "model_loaded": model is not None,
        "model_path": str(MODEL_PATH),
        "model_exists": MODEL_PATH.exists(),
        "troubleshooting": "See FIX_DLL_ERROR.md" if not YOLO_AVAILABLE else None
    }


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """Predict coral detection on uploaded image"""
    if not YOLO_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="YOLO not available. Please fix PyTorch DLL error. See FIX_DLL_ERROR.md for instructions."
        )
    
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        image, filename = process_image(file)
        annotated_image, detections = run_inference(image)
        output_image_base64 = image_to_base64(annotated_image)
        
        output_filename = f"output_{filename}"
        output_path = OUTPUT_DIR / output_filename
        cv2.imwrite(str(output_path), annotated_image)
        
        return JSONResponse(content={
            "success": True,
            "output_image": output_image_base64,
            "detections": detections,
            "count": len(detections),
            "output_path": str(output_path)
        })
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error during prediction: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )


if __name__ == "__main__":
    if not YOLO_AVAILABLE:
        print("\n" + "="*60)
        print("WARNING: YOLO is not available due to DLL error!")
        print("Please see FIX_DLL_ERROR.md for troubleshooting steps.")
        print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
