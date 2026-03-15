"""
FEATURE INTEGRATION GUIDE
How to integrate the new modular features into your FastAPI backend
"""

# ============================================================================
# FEATURE 1: s Dashboard
# ============================================================================

# In main.py, add to your imports:
from features.analytics_feature import router as analytics_router

# Then, include the router with other routers:
app.include_router(analytics_router)

# This exposes:
# GET /features/analytics/summary
#
# Response:
# {
#     "total_detections": 120,
#     "most_detected_class": "echinus",
#     "class_counts": {
#         "echinus": 50,
#         "holothurian": 40,
#         "scallop": 20,
#         "starfish": 10
#     },
#     "average_confidence": 0.78
# }


# ============================================================================
# FEATURE 2: Confidence Threshold Control
# ============================================================================

# In main.py, add to your imports:
from features.confidence_feature import router as confidence_router

# Then, include the router:
app.include_router(confidence_router)

# This exposes:
# POST /features/predict_with_threshold
#
# Query Parameter:
# - confidence_threshold: float (default: 0.25)
#
# Request: multipart/form-data with image file
# Response:
# {
#     "success": true,
#     "output_image": "data:image/jpeg;base64,...",
#     "detections": [
#         {"class": "echinus", "confidence": 0.95},
#         {"class": "starfish", "confidence": 0.87}
#     ],
#     "count": 2,
#     "confidence_threshold": 0.5,
#     "output_path": "outputs/threshold_0.5_..."
# }
#
# You can also import the core function directly:
# from features.confidence_feature import run_inference_with_threshold
#
# image = cv2.imread("path/to/image.jpg")
# annotated_image, detections = run_inference_with_threshold(image, threshold=0.7)


# ============================================================================
# FEATURE 3: Detection Heatmap
# ============================================================================

# Import the heatmap functions:
from features.heatmap_feature import (
    generate_detection_heatmap,
    get_heatmap_statistics,
    get_hotspot_regions
)

# Usage in another router or feature:
def process_with_heatmap(image, detections):
    # Generate heatmap
    heatmap_result = generate_detection_heatmap(image, detections)

    # Access results:
    heatmap_overlay = heatmap_result["heatmap_image"]  # For visualization
    heatmap_data = heatmap_result["heatmap_data"]      # For analysis
    centers = heatmap_result["detection_centers"]      # Coordinates

    # Get statistics
    stats = get_heatmap_statistics(heatmap_data)
    # Returns: max_intensity, min_intensity, mean_intensity, detection_density

    # Find hotspot regions
    hotspots = get_hotspot_regions(heatmap_data, threshold_percentile=75)
    # Returns: list of regions with center_x, center_y, intensity


# ============================================================================
# COMPLETE EXAMPLE: Adding all features to main.py
# ============================================================================

"""
# At the top of main.py, in the imports section:

from routers import auth, history, predict
from database import test_connection
from utils import set_model

# ADD THESE THREE LINES FOR NEW FEATURES:
from features.analytics_feature import router as analytics_router
from features.confidence_feature import router as confidence_router
from features.heatmap_feature import (
    generate_detection_heatmap,
    get_heatmap_statistics,
    get_hotspot_regions
)

# ... rest of main.py code ...

# After the existing routers are included (around line ~107):
# app.include_router(auth.router)
# app.include_router(predict.router)
# app.include_router(history.router)

# ADD THESE LINES:
app.include_router(analytics_router)      # Adds /features/analytics/summary
app.include_router(confidence_router)     # Adds /features/predict_with_threshold
"""


# ============================================================================
# USING FEATURES IN NEW ROUTERS
# ============================================================================

"""
Example: Create a new router that combines all three features

# In backend/features/combined_analysis.py:

from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from auth import verify_token
from utils import process_image, image_to_base64, YOLO_AVAILABLE
import cv2
import base64
import io
from PIL import Image

# Import feature functions
from features.confidence_feature import run_inference_with_threshold
from features.heatmap_feature import (
    generate_detection_heatmap,
    get_heatmap_statistics
)

router = APIRouter(prefix="/features", tags=["combined"])
security = HTTPBearer()

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    payload = verify_token(credentials.credentials)
    return payload.get("sub")

@router.post("/analyze_with_heatmap")
async def analyze_with_heatmap(
    file: UploadFile = File(...),
    confidence_threshold: float = 0.25,
    user_id: str = Depends(get_current_user_id)
):
    '''
    Combined feature: Run detection with threshold + Generate heatmap

    POST /features/analyze_with_heatmap
    '''
    try:
        # Validate
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")

        # Process image
        image, filename = process_image(file)

        # Use confidence threshold feature
        annotated_image, detections = run_inference_with_threshold(
            image,
            threshold=confidence_threshold
        )

        # Use heatmap feature
        # First, convert detections format to include bounding boxes if available
        # This depends on your YOLO results format
        heatmap_result = generate_detection_heatmap(image, detections)
        heatmap_overlay = heatmap_result["heatmap_image"]
        heatmap_stats = get_heatmap_statistics(heatmap_result["heatmap_data"])

        # Convert to base64
        heatmap_base64 = image_to_base64(heatmap_overlay)

        return JSONResponse(content={
            "success": True,
            "annotated_image": image_to_base64(annotated_image),
            "heatmap_image": heatmap_base64,
            "detections": detections,
            "detection_count": len(detections),
            "heatmap_statistics": heatmap_stats,
            "confidence_threshold": confidence_threshold
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Then in main.py, add:
# from features.combined_analysis import router as combined_router
# app.include_router(combined_router)
"""


# ============================================================================
# TESTING THE FEATURES
# ============================================================================

"""
# Test Analytics Feature:
curl -H "Authorization: Bearer <YOUR_JWT_TOKEN>" \\
  http://localhost:8000/features/analytics/summary


# Test Confidence Threshold Feature:
curl -X POST -H "Authorization: Bearer <YOUR_JWT_TOKEN>" \\
  -F "file=@image.jpg" \\
  -F "confidence_threshold=0.5" \\
  http://localhost:8000/features/predict_with_threshold


# Use Python to test:
import requests

headers = {"Authorization": f"Bearer {token}"}

# Analytics
response = requests.get(
    "http://localhost:8000/features/analytics/summary",
    headers=headers
)
print(response.json())

# Threshold Prediction
with open("image.jpg", "rb") as f:
    files = {"file": f}
    params = {"confidence_threshold": 0.5}
    response = requests.post(
        "http://localhost:8000/features/predict_with_threshold",
        headers=headers,
        files=files,
        params=params
    )
print(response.json())
"""


# ============================================================================
# FEATURE FILE SUMMARY
# ============================================================================

"""
File Structure:
├── backend/
│   ├── features/
│   │   ├── analytics_feature.py         [NEW] Analytics dashboard
│   │   ├── confidence_feature.py        [NEW] Threshold control
│   │   ├── heatmap_feature.py          [NEW] Heatmap generation
│   │   ├── image_enhancement.py         [EXISTING]
│   │   └── marine_summary.py            [EXISTING]
│   ├── routers/
│   ├── main.py                          (unchanged)
│   ├── models.py                        (unchanged)
│   ├── database.py                      (unchanged)
│   └── ...

Key Features:
1. Modular Design: Each feature is independent and can be used separately
2. No Breaking Changes: Existing endpoints remain unchanged
3. Easy Integration: Simple imports and router inclusion
4. Reusable Functions: Core functions can be imported and used in custom routers
5. Well Documented: Clear comments and docstrings
"""
