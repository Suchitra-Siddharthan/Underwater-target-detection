"""
MongoDB Database Connection and Configuration
"""

from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection string (default to localhost)
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "underwater_detection")

# Initialize async MongoDB client
client = AsyncIOMotorClient(MONGODB_URL)
db = client[DATABASE_NAME]

# Collections
users_collection = db["users"]
history_collection = db["history"]

# Test connection
async def test_connection():
    """Test MongoDB connection"""
    try:
        await client.admin.command('ping')
        print(f"✅ Connected to MongoDB: {DATABASE_NAME}")
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False
