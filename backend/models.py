"""
Database Models/Schemas
"""

from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


# User Models
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# History Models
class DetectionItem(BaseModel):
    class_name: str
    confidence: float

class HistoryCreate(BaseModel):
    user_id: str
    original_filename: str
    detections: List[DetectionItem]
    output_image_base64: str
    output_path: Optional[str] = None
    marine_summary: Optional[str] = None

class HistoryResponse(BaseModel):
    id: str
    user_id: str
    original_filename: str
    detections: List[DetectionItem]
    output_image_base64: str
    output_path: Optional[str] = None
    timestamp: datetime
    marine_summary: Optional[str] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }