"""
History Router: Get, Delete, Download history records
"""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import FileResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from database import history_collection
from models import HistoryResponse, DetectionItem
from auth import verify_token
from bson import ObjectId
from typing import List
import os
from pathlib import Path
from features.marine_summary import generate_marine_summary

router = APIRouter(prefix="/history", tags=["history"])
security = HTTPBearer()

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Get current user ID from JWT token"""
    payload = verify_token(credentials.credentials)
    return payload.get("sub")

@router.get("/", response_model=List[HistoryResponse])
async def get_history(user_id: str = Depends(get_current_user_id)):
    """
    Get all history records for current user
    
    Args:
        user_id: Current user ID (from JWT)
        
    Returns:
        List of history records
    """
    # Query history for this user
    cursor = history_collection.find({"user_id": user_id}).sort("timestamp", -1)
    history_list = await cursor.to_list(length=100)
    
    # Convert to response models
    results = []
    for item in history_list:
        # MongoDB datetime objects are Python datetime objects
        # Ensure they're marked as UTC if naive (datetime.utcnow() creates naive datetimes)
        from datetime import timezone
        timestamp = item["timestamp"]
        if timestamp and not timestamp.tzinfo:
            # If naive datetime, assume it's UTC (since we use datetime.utcnow())
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        
        # Ensure we always have a marine summary for history output
        marine_summary = item.get("marine_summary")
        if not marine_summary:
            # Generate summary from detections if missing
            marine_summary = generate_marine_summary([
                {"class": d.get("class_name"), "confidence": d.get("confidence")} 
                for d in item.get("detections", [])
            ])

        results.append(HistoryResponse(
            id=str(item["_id"]),
            user_id=item["user_id"],
            original_filename=item["original_filename"],
            detections=[DetectionItem(**d) for d in item["detections"]],
            output_image_base64=item["output_image_base64"],
            output_path=item.get("output_path"),
            timestamp=timestamp,
            marine_summary=marine_summary
        ))
    
    return results

@router.delete("/{history_id}")
async def delete_history(history_id: str, user_id: str = Depends(get_current_user_id)):
    """
    Delete a history record (only if it belongs to current user)
    
    Args:
        history_id: History record ID
        user_id: Current user ID (from JWT)
        
    Returns:
        Success message
    """
    # Verify history exists and belongs to user
    history_item = await history_collection.find_one({
        "_id": ObjectId(history_id),
        "user_id": user_id
    })
    
    if not history_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="History record not found or you don't have permission to delete it"
        )
    
    # Delete the record
    await history_collection.delete_one({"_id": ObjectId(history_id)})
    
    # Optionally delete the output image file
    if history_item.get("output_path") and os.path.exists(history_item["output_path"]):
        try:
            os.remove(history_item["output_path"])
        except Exception as e:
            print(f"Warning: Could not delete file {history_item['output_path']}: {e}")
    
    return {"message": "History record deleted successfully"}

@router.get("/{history_id}/download/image")
async def download_image(history_id: str, user_id: str = Depends(get_current_user_id)):
    """
    Download output image for a history record
    
    Args:
        history_id: History record ID
        user_id: Current user ID (from JWT)
        
    Returns:
        Image file download
    """
    # Verify history exists and belongs to user
    history_item = await history_collection.find_one({
        "_id": ObjectId(history_id),
        "user_id": user_id
    })
    
    if not history_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="History record not found"
        )
    
    # Check if file exists
    output_path = history_item.get("output_path")
    if output_path and os.path.exists(output_path):
        return FileResponse(
            output_path,
            media_type="image/jpeg",
            filename=f"detection_{history_id}.jpg"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Output image file not found"
        )

@router.get("/{history_id}/download/result")
async def download_result(history_id: str, user_id: str = Depends(get_current_user_id)):
    """
    Download detection results as JSON
    
    Args:
        history_id: History record ID
        user_id: Current user ID (from JWT)
        
    Returns:
        JSON file download
    """
    # Verify history exists and belongs to user
    history_item = await history_collection.find_one({
        "_id": ObjectId(history_id),
        "user_id": user_id
    })
    
    if not history_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="History record not found"
        )
    
    # Prepare JSON data
    result_data = {
        "original_filename": history_item["original_filename"],
        "timestamp": history_item["timestamp"].isoformat(),
        "detections": history_item["detections"],
        "count": len(history_item["detections"])
    }
    
    # Create temporary JSON file
    import json
    import tempfile
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        json.dump(result_data, f, indent=2)
        temp_path = f.name
    
    return FileResponse(
        temp_path,
        media_type="application/json",
        filename=f"detection_result_{history_id}.json"
    )
