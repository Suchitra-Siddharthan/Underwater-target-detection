"""
Authentication Router: Signup and Login
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends
from database import users_collection
from models import UserCreate, UserLogin, UserResponse, Token
from auth import get_password_hash, verify_password, create_access_token
from bson import ObjectId
from datetime import datetime, timezone

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

@router.post("/signup", response_model=UserResponse)
async def signup(user_data: UserCreate):
    """
    User registration endpoint
    
    Args:
        user_data: User registration data (name, email, password)
        
    Returns:
        UserResponse with user details
    """
    # Validate password length (bcrypt limit is 72 bytes)
    if len(user_data.password.encode('utf-8')) > 72:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is too long. Maximum length is 72 bytes."
        )
    
    # Check if user already exists
    existing_user = await users_collection.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    hashed_password = get_password_hash(user_data.password)
    print(f"DEBUG: Password hashed successfully for {user_data.email}")
    
    # Create user document
    user_doc = {
        "name": user_data.name,
        "email": user_data.email,
        "password": hashed_password,
        "created_at": datetime.now(timezone.utc)
    }
    
    # Insert user
    result = await users_collection.insert_one(user_doc)
    
    return UserResponse(
        id=str(result.inserted_id),
        name=user_data.name,
        email=user_data.email
    )

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    """
    User login endpoint
    
    Args:
        credentials: Login credentials (email, password)
        
    Returns:
        Token with JWT access token
    """
    # Find user
    user = await users_collection.find_one({"email": credentials.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verify password
    try:
        print(f"DEBUG: Verifying password for {credentials.email}")
        password_valid = verify_password(credentials.password, user["password"])
        print(f"DEBUG: Password verification result: {password_valid}")
        if not password_valid:
            print(f"DEBUG: Password verification failed for {credentials.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Password verification error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user["_id"]), "email": user["email"]})
    
    return Token(access_token=access_token, token_type="bearer")

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Get current authenticated user
    
    Args:
        credentials: JWT token from Authorization header
        
    Returns:
        UserResponse with user details
    """
    from auth import verify_token
    
    # Verify token
    payload = verify_token(credentials.credentials)
    user_id = payload.get("sub")
    
    # Get user from database
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        id=str(user["_id"]),
        name=user["name"],
        email=user["email"]
    )
