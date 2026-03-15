"""
Confidence Threshold Control Feature - Run inference with custom confidence thresholds
"""

from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from auth import verify_token
from utils import process_image, image_to_base64, YOLO_AVAILABLE, model
import cv2
import numpy as np
from pathlib import Path
from datetime import datetime

router = APIRouter(prefix="/features", tags=["prediction"])
security = HTTPBearer()

# Default confidence threshold
DEFAULT_THRESHOLD = 0.25


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Extract user ID from JWT token"""
    payload = verify_token(credentials.credentials)
    return payload.get("sub")


def run_inference_with_threshold(image: np.ndarray, threshold: float = DEFAULT_THRESHOLD) -> tuple:
    """
    Run YOLOv8 inference on image with custom confidence threshold

    Args:
        image: Input image as numpy array (BGR format)
        threshold: Confidence threshold (0.0 to 1.0). Default is 0.25

    Returns:
        tuple: (annotated_image, detections_list)
            - annotated_image: Image with bounding boxes drawn
            - detections_list: List of detected objects with format:
                [
                    {"class": "echinus", "confidence": 0.95},
                    ...
                ]

    Raises:
        HTTPException: If YOLO is not available or model is not loaded
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

    # Validate threshold
    if not (0.0 <= threshold <= 1.0):
        raise ValueError("Confidence threshold must be between 0.0 and 1.0")

    # Run inference with custom confidence threshold
    results = model(image, conf=threshold)
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


@router.post("/predict_with_threshold")
async def predict_with_threshold(
    file: UploadFile = File(...),
    confidence_threshold: float = DEFAULT_THRESHOLD,
    user_id: str = Depends(get_current_user_id)
):
    """
    POST /features/predict_with_threshold

    Run object detection with a custom confidence threshold

    Query Parameters:
        - confidence_threshold: Confidence score threshold (0.0-1.0). Default: 0.25

    Request Body:
        - file: Image file to analyze

    Returns:
        JSONResponse with:
        - success: Boolean indicating success
        - output_image: Base64 encoded annotated image
        - detections: List of detected objects
        - count: Number of objects detected
        - confidence_threshold: The threshold used
        - output_path: Path where output image was saved

    Example:
        POST /features/predict_with_threshold
        Content-Type: multipart/form-data

        file: <image_file>
        confidence_threshold: 0.5
    """
    if not YOLO_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="YOLO not available. Please fix PyTorch DLL error."
        )

    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="File must be an image"
            )

        # Validate confidence threshold
        if not (0.0 <= confidence_threshold <= 1.0):
            raise HTTPException(
                status_code=400,
                detail="Confidence threshold must be between 0.0 and 1.0"
            )

        # Process image
        image, filename = process_image(file)

        # Run inference with custom threshold
        annotated_image, detections = run_inference_with_threshold(
            image,
            threshold=confidence_threshold
        )

        # Convert annotated image to base64
        output_image_base64 = image_to_base64(annotated_image)

        # Save output image with correct path
        BACKEND_DIR = Path(__file__).parent.parent  # Go up from features/ to backend/
        OUTPUT_DIR = BACKEND_DIR / "outputs"
        OUTPUT_DIR.mkdir(exist_ok=True)
        output_filename = f"threshold_{confidence_threshold}_{user_id}_{datetime.utcnow().timestamp()}_{filename}"
        output_path = OUTPUT_DIR / output_filename
        cv2.imwrite(str(output_path), annotated_image)

        # Format response
        response_data = {
            "success": True,
            "output_image": output_image_base64,
            "detections": detections,
            "count": len(detections),
            "confidence_threshold": confidence_threshold,
            "output_path": str(output_path),
        }

        return JSONResponse(content=response_data)

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error during threshold prediction: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )
