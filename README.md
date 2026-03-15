# Underwater Target Detection

A full-stack web application for detecting underwater targets (coral, fish, etc.) using YOLOv8 deep learning model.

## 🎯 Features

- **Modern React Frontend** with underwater-themed UI
- **FastAPI Backend** with YOLOv8 model inference
- **Real-time Object Detection** with bounding boxes
- **User Authentication** (Login, Sign Up, Forgot Password)
- **Glassmorphism Design** with animated underwater background
- **Responsive Design** for desktop, tablet, and mobile

## 📁 Project Structure

```
Underwater-target-detection/
├── backend/                 # FastAPI backend
│   ├── main.py            # FastAPI application
│   ├── requirements.txt   # Python dependencies
│   ├── model/
│   │   └── best.pt        # YOLOv8 trained model
│   ├── uploads/           # Temporary upload storage (gitignored)
│   └── outputs/           # Processed images (gitignored)
│
├── frontend/               # React frontend
│   ├── src/
│   │   ├── App.jsx        # Main application component
│   │   ├── components/    # React components
│   │   └── styles.css     # Global styles
│   └── public/            # Static assets
│
└── README.md              # This file
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** (NOT Microsoft Store Python - see backend/README.md)
- **Node.js 14+** and npm
- **Trained YOLOv8 model** (`best.pt`) in `backend/model/`

### Backend Setup

1. **Navigate to backend:**
   ```bash
   cd backend
   ```

2. **Create virtual environment (recommended):**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify model location:**
   - Ensure `best.pt` is in `backend/model/best.pt`

5. **Start the server:**
   ```bash
   python main.py
   ```
   
   Server runs on `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm start
   ```
   
   Frontend runs on `http://localhost:3000`

## 🔧 API Endpoints

### Health Check
```
GET http://localhost:8000/health
```

### Prediction
```
POST http://localhost:8000/predict
Content-Type: multipart/form-data
Body: file (image file)
```

**Response:**
```json
{
  "success": true,
  "output_image": "data:image/jpeg;base64,...",
  "detections": [
    {
      "class": "coral",
      "confidence": 0.95
    }
  ],
  "count": 1
}
```

## 🛠️ Technology Stack

### Frontend
- React 18
- CSS3 (Glassmorphism, Animations)
- Fetch API

### Backend
- FastAPI
- YOLOv8 (Ultralytics)
- OpenCV
- Python 3.8+

## 📝 Usage

1. **Start both servers** (backend and frontend)
2. **Login** to the application
3. **Upload** an underwater image
4. **Click "Detect Targets"** to run inference
5. **View results** with bounding boxes and confidence scores

## 🐛 Troubleshooting

### Backend Issues

- **DLL Error (Windows):** See `backend/FIX_DLL_ERROR.md`
- **Model not loading:** Check `backend/model/best.pt` exists
- **Port already in use:** Change port in `main.py`

### Frontend Issues

- **CORS errors:** Ensure backend CORS allows your frontend port
- **API connection failed:** Verify backend is running on port 8000
- **Image not displaying:** Check browser console for errors

## 📚 Documentation

- **Backend:** See `backend/README.md`
- **Installation Issues:** See `backend/INSTALL.md`
- **DLL Errors:** See `backend/FIX_DLL_ERROR.md`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is part of a B.E CSE Creative and Innovative Project.

## 👥 Authors

- B.E CSE Project Team

## 🙏 Acknowledgments

- Ultralytics for YOLOv8
- FastAPI team
- React community

---

**Note:** Make sure to keep `backend/model/best.pt` secure and don't commit it if it contains proprietary data. The current `.gitignore` is configured to allow it, but you may want to exclude it for security.
