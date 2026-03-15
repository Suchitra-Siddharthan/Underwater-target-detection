"""
Prediction Router: Image upload and inference with history saving
"""

from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from database import history_collection
from auth import verify_token
import cv2
import numpy as np
from PIL import Image
import io
import base64
from pathlib import Path
from datetime import datetime, timezone
from utils import process_image, run_inference, image_to_base64
import utils
from features.marine_summary import generate_marine_summary
from features.image_enhancement import enhance_underwater_image

router = APIRouter(prefix="/predict", tags=["prediction"])
security = HTTPBearer()

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Get current user ID from JWT token"""
    payload = verify_token(credentials.credentials)
    return payload.get("sub")

@router.post("")
async def predict(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id)
):
    """
    Predict coral detection on uploaded image and save to history

    Args:
        file: Uploaded image file
        user_id: Current user ID (from JWT)

    Returns:
        JSONResponse with output image (base64) and detection results
    """
    print(f"DEBUG: predict endpoint called - YOLO_AVAILABLE={utils.YOLO_AVAILABLE}, model={'loaded' if utils.model else 'None'}")
    if not utils.YOLO_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="YOLO not available. Please fix PyTorch DLL error. Check backend logs for details."
        )

    if utils.model is None:
        raise HTTPException(
            status_code=500,
            detail="Model not loaded. Check backend logs for details."
        )
    
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="File must be an image"
            )
        
        # Process image
        image, filename = process_image(file)

        # Enhance image visibility before running YOLO detection
        image = enhance_underwater_image(image)

        # Run inference
        annotated_image, detections = run_inference(image)

        # Convert annotated image to base64
        output_image_base64 = image_to_base64(annotated_image)

        # Save output image with correct path
        BACKEND_DIR = Path(__file__).parent.parent  # Go up from routers/ to backend/
        OUTPUT_DIR = BACKEND_DIR / "outputs"
        OUTPUT_DIR.mkdir(exist_ok=True)
        output_filename = f"output_{user_id}_{datetime.utcnow().timestamp()}_{filename}"
        output_path = OUTPUT_DIR / output_filename
        cv2.imwrite(str(output_path), annotated_image)
        
        # Format detections for database
        detection_items = [
            {"class_name": d["class"], "confidence": d["confidence"]}
            for d in detections
        ]
        
        # Generate marine ecosystem summary from detections + image quality
        marine_summary = generate_marine_summary(detections, image)

        # Save to history
        history_doc = {
            "user_id": user_id,
            "original_filename": filename,
            "detections": detection_items,
            "output_image_base64": output_image_base64,
            "output_path": str(output_path),
            "timestamp": datetime.now(timezone.utc),
            "marine_summary": marine_summary
        }
        
        await history_collection.insert_one(history_doc)
        
        # Generate marine ecosystem summary from detections + image quality
        marine_summary = generate_marine_summary(detections, image)

        # Format response
        response_data = {
            "success": True,
            "output_image": output_image_base64,
            "detections": detections,
            "count": len(detections),
            "output_path": str(output_path),
            "history_id": str(history_doc.get("_id", "")),
            "marine_summary": marine_summary,
        }
        
        return JSONResponse(content=response_data)
        
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
