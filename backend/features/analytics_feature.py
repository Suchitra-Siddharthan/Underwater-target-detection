"""
Detection Analytics Feature - Analyze detection history and provide insights
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from database import history_collection
from auth import verify_token
from typing import Dict, List, Any

router = APIRouter(prefix="/features/analytics", tags=["analytics"])
security = HTTPBearer()


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Extract user ID from JWT token"""
    payload = verify_token(credentials.credentials)
    return payload.get("sub")


async def get_analytics_summary(user_id: str) -> Dict[str, Any]:
    """
    Analyze detection history for a user using MongoDB aggregation pipeline

    Only counts the 4 primary marine species:
    - echinus
    - scallop
    - holothurian
    - starfish

    Args:
        user_id: User ID to fetch analytics for

    Returns:
        Dictionary containing:
        - total_detections: Total number of objects detected
        - most_detected_class: Class name with highest detection count
        - class_counts: Dictionary of class names and their detection counts (always includes all 4 species)
        - average_confidence: Average confidence score across all detections
    """
    try:
        # Define the 4 valid species
        VALID_SPECIES = ["echinus", "scallop", "holothurian", "starfish"]

        # MongoDB aggregation pipeline
        pipeline = [
            # Step 1: Match documents for this user
            {
                "$match": {"user_id": user_id}
            },
            # Step 2: Unwind detections array to create separate documents
            {
                "$unwind": "$detections"
            },
            # Step 3: Filter to only valid species (case-insensitive)
            {
                "$match": {
                    "detections.class_name": {
                        "$in": VALID_SPECIES
                    }
                }
            },
            # Step 4: Group by class name to count and calculate average confidence
            {
                "$group": {
                    "_id": "$detections.class_name",
                    "count": {"$sum": 1},
                    "avg_confidence": {"$avg": "$detections.confidence"}
                }
            },
            # Step 5: Sort by count descending
            {
                "$sort": {"count": -1}
            }
        ]

        # Execute aggregation
        results = await history_collection.aggregate(pipeline).to_list(None)

        # Initialize all species with 0 count
        class_counts = {species: 0 for species in VALID_SPECIES}
        total_detections = 0
        confidence_values = []
        most_detected_class = None
        max_count = 0

        # Process results and update class_counts
        for result in results:
            class_name = result["_id"]
            count = result["count"]
            avg_conf = result["avg_confidence"]

            # Only include valid species (safety check)
            if class_name in VALID_SPECIES:
                class_counts[class_name] = count
                total_detections += count
                confidence_values.extend([avg_conf] * count)

                # Track most detected class
                if count > max_count:
                    max_count = count
                    most_detected_class = class_name

        # If no detections, set most_detected_class to the first species with 0
        if most_detected_class is None and total_detections == 0:
            most_detected_class = "N/A"

        # Calculate overall average confidence
        average_confidence = (
            sum(confidence_values) / len(confidence_values)
            if confidence_values else 0.0
        )

        return {
            "total_detections": total_detections,
            "most_detected_class": most_detected_class or "N/A",
            "class_counts": class_counts,
            "average_confidence": round(average_confidence, 4)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate analytics: {str(e)}"
        )


@router.get("/summary")
async def analytics_summary(
    user_id: str = Depends(get_current_user_id)
):
    """
    GET /features/analytics/summary

    Returns detection analytics for the authenticated user

    Response Example:
    {
        "total_detections": 120,
        "most_detected_class": "echinus",
        "class_counts": {
            "echinus": 50,
            "holothurian": 40,
            "scallop": 20,
            "starfish": 10
        },
        "average_confidence": 0.78
    }
    """
    analytics_data = await get_analytics_summary(user_id)
    return JSONResponse(content=analytics_data)
