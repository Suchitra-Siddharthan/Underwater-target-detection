"""
FastAPI Backend for Underwater Coral Detection using YOLOv8
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import uvicorn

# Import routers
from routers import auth, history, predict
from database import test_connection
from utils import set_model

# Import new feature routers
from features.analytics_feature import router as analytics_router
from features.confidence_feature import router as confidence_router

# Try to import YOLO, handle DLL errors gracefully
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except OSError as e:
    if "DLL" in str(e) or "WinError 1114" in str(e):
        print("\n" + "="*70)
        print("ERROR: PyTorch DLL loading failed!")
        print("This is a common issue with Microsoft Store Python on Windows.")
        print("\nSOLUTION: Please see backend/FIX_DLL_ERROR.md for fixes.")
        print("Quick fix: Install regular Python from python.org (not Microsoft Store)")
        print("="*70 + "\n")
    YOLO_AVAILABLE = False
    YOLO = None
except Exception as e:
    print(f"Warning: Could not import YOLO: {e}")
    YOLO_AVAILABLE = False
    YOLO = None

# Initialize FastAPI app
app = FastAPI(title="Underwater Coral Detection API", version="1.0.0")

# CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create necessary directories
# Get the directory where this script is located
BACKEND_DIR = Path(__file__).parent
UPLOAD_DIR = BACKEND_DIR / "uploads"
OUTPUT_DIR = BACKEND_DIR / "outputs"
MODEL_PATH = BACKEND_DIR / "model" / "model1.pt"

UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Load YOLOv8 model
model = None
if YOLO_AVAILABLE:
    print("Loading YOLOv8 model...")
    try:
        if MODEL_PATH.exists():
            model = YOLO(str(MODEL_PATH))
            print(f"✅ Model loaded successfully from {MODEL_PATH}")
            # Set model in utils for routers to use
            set_model(model, YOLO_AVAILABLE)
            print(f"✅ Model set in utils - ready for predictions")
        else:
            print(f"❌ Warning: Model file not found at {MODEL_PATH}")
            set_model(None, False)
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        import traceback
        traceback.print_exc()
        model = None
        set_model(None, False)
else:
    print("❌ YOLO not available. Cannot load model. See FIX_DLL_ERROR.md")
    set_model(None, False)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Underwater Coral Detection API",
        "status": "running" if YOLO_AVAILABLE else "error",
        "yolo_available": YOLO_AVAILABLE,
        "model_loaded": model is not None,
        "error": "DLL error detected. Please see FIX_DLL_ERROR.md" if not YOLO_AVAILABLE else None
    }


@app.get("/health")
async def health():
    """Health check with model status"""
    return {
        "status": "healthy" if YOLO_AVAILABLE else "degraded",
        "yolo_available": YOLO_AVAILABLE,
        "model_loaded": model is not None,
        "model_path": str(MODEL_PATH),
        "model_exists": MODEL_PATH.exists(),
        "troubleshooting": "See FIX_DLL_ERROR.md" if not YOLO_AVAILABLE else None
    }


# Include routers
app.include_router(auth.router)
app.include_router(predict.router)
app.include_router(history.router)

# Include feature routers
app.include_router(analytics_router)
app.include_router(confidence_router)


@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    await test_connection()

if __name__ == "__main__":
    if not YOLO_AVAILABLE:
        print("\n" + "="*70)
        print("WARNING: YOLO is not available due to DLL error!")
        print("The API will start but /predict endpoint will return errors.")
        print("Please see backend/FIX_DLL_ERROR.md for troubleshooting steps.")
        print("="*70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
