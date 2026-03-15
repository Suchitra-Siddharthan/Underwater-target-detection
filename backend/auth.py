"""
Authentication utilities: JWT, password hashing
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from fastapi import HTTPException, status
import os
from dotenv import load_dotenv

load_dotenv()

# Secret key for JWT (in production, use environment variable)
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# bcrypt has a 72-byte limit for passwords
MAX_PASSWORD_LENGTH = 72

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    try:
        # Convert password to bytes if needed, and truncate if too long
        password_bytes = plain_password.encode('utf-8')[:MAX_PASSWORD_LENGTH]
        # Hashed password should already be a string from database, convert to bytes
        hashed_bytes = hashed_password.encode('utf-8') if isinstance(hashed_password, str) else hashed_password
        result = bcrypt.checkpw(password_bytes, hashed_bytes)
        if not result:
            print(f"Password verification failed for user")
        return result
    except Exception as e:
        print(f"Password verification error: {e}")
        import traceback
        traceback.print_exc()
        return False

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt"""
    # Convert password to bytes and truncate if longer than 72 bytes
    password_bytes = password.encode('utf-8')[:MAX_PASSWORD_LENGTH]
    # Generate salt and hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
