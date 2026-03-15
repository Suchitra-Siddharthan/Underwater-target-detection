# Setup Guide - Underwater Target Detection with Authentication

This guide will help you set up the complete application with authentication, history, download, and delete features.

## Prerequisites

- Python 3.8+ (not Microsoft Store version on Windows)
- Node.js 16+ and npm
- MongoDB (local or cloud instance)

## Backend Setup

### 1. Install MongoDB

**Windows:**
- Download MongoDB Community Server from https://www.mongodb.com/try/download/community
- Install and start MongoDB service

**macOS:**
```bash
brew install mongodb-community
brew services start mongodb-community
```

**Linux:**
```bash
sudo apt-get install mongodb
sudo systemctl start mongodb
```

**Or use MongoDB Atlas (Cloud):**
- Sign up at https://www.mongodb.com/cloud/atlas
- Create a free cluster
- Get your connection string

### 2. Install Python Dependencies

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the `backend` folder:

```env
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=underwater_detection

# JWT Secret Key (Change this in production!)
SECRET_KEY=your-secret-key-change-in-production-minimum-32-characters-long
```

**For MongoDB Atlas:**
```env
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=underwater_detection
SECRET_KEY=your-secret-key-change-in-production-minimum-32-characters-long
```

### 4. Start Backend Server

```bash
cd backend
python main.py
```

Or use the provided scripts:
- Windows: `start.bat`
- macOS/Linux: `bash start.sh`

The backend will run on `http://localhost:8000`

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

The frontend will run on `http://localhost:5173` (Vite) or `http://localhost:3000` (Create React App)

## Project Structure

```
backend/
├── main.py              # FastAPI app entry point
├── database.py          # MongoDB connection
├── models.py            # Pydantic models
├── auth.py              # JWT and password utilities
├── utils.py             # Image processing utilities
├── routers/
│   ├── auth.py          # Authentication endpoints
│   ├── predict.py       # Prediction endpoint (with history saving)
│   └── history.py       # History management endpoints
├── model/
│   └── best.pt          # YOLOv8 trained model
├── uploads/            # Uploaded images
├── outputs/            # Output images with detections
└── requirements.txt    # Python dependencies

frontend/
├── src/
│   ├── App.jsx         # Main app component
│   ├── context/
│   │   └── AuthContext.jsx  # Authentication context
│   └── components/
│       ├── Login.jsx    # Login page
│       ├── SignUp.jsx   # Signup page
│       ├── History.jsx  # History page
│       └── ...
└── package.json
```

## API Endpoints

### Authentication
- `POST /auth/signup` - User registration
- `POST /auth/login` - User login (returns JWT)
- `GET /auth/me` - Get current user info (requires JWT)

### Prediction
- `POST /predict/` - Upload image and run detection (requires JWT, saves to history)

### History
- `GET /history/` - Get user's prediction history (requires JWT)
- `DELETE /history/{id}` - Delete a history record (requires JWT)
- `GET /history/{id}/download/image` - Download output image (requires JWT)
- `GET /history/{id}/download/result` - Download detection results as JSON (requires JWT)

## Features

### 1. User Authentication
- Sign up with name, email, password
- Login with email and password
- JWT-based authentication
- Password hashing with bcrypt
- Protected routes

### 2. Image Prediction
- Upload image
- Run YOLOv8 inference
- View results with bounding boxes
- Download output image
- Download detection results as JSON
- All predictions saved to history

### 3. History Management
- View all past predictions
- See detection results and timestamps
- Download images and results
- Delete individual records
- User-specific history (users can only see/delete their own records)

## Usage Flow

1. **Sign Up / Login**
   - New users: Sign up with name, email, password
   - Existing users: Login with email and password

2. **Upload & Detect**
   - Upload an image
   - Click "Detect Targets"
   - View results with bounding boxes
   - Download image or JSON results

3. **View History**
   - Click "View History" button
   - Browse all past predictions
   - Download or delete records

4. **Logout**
   - Click "Logout" button
   - Returns to login page

## Troubleshooting

### MongoDB Connection Issues
- Ensure MongoDB is running: `mongosh` or `mongo` should connect
- Check `MONGODB_URL` in `.env` file
- For Atlas: Verify connection string and network access

### Backend Errors
- Check if model file exists: `backend/model/best.pt`
- Verify Python dependencies: `pip install -r requirements.txt`
- Check port 8000 is not in use

### Frontend Errors
- Check backend is running on `http://localhost:8000`
- Verify CORS settings in `backend/main.py`
- Check browser console for errors

### JWT Token Issues
- Token expires after 7 days (configurable in `backend/auth.py`)
- Clear localStorage if token is invalid
- Re-login to get new token

## Security Notes

- **Change SECRET_KEY** in production
- Use strong passwords
- Enable HTTPS in production
- Validate file uploads
- Rate limit API endpoints
- Use environment variables for secrets

## Next Steps

- Add email verification
- Add password reset functionality
- Add user profile management
- Add image preview before upload
- Add batch upload support
- Add export history as CSV
