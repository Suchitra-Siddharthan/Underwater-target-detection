# Underwater Target Detection System

## Overview

The Underwater Target Detection System is a full-stack AI-powered application designed to detect and analyze underwater objects from images using deep learning. The system integrates a YOLOv8 object detection model with a FastAPI backend, React frontend, and MongoDB database to provide an end-to-end solution for underwater image analysis.

The project performs underwater image enhancement, object detection, confidence analysis, marine ecosystem summarization, and prediction history management through a secure authenticated platform.

---

## Features

* User Registration and Login
* JWT-based Authentication and Authorization
* Underwater Image Upload
* Underwater Image Enhancement
* YOLOv8-based Object Detection
* Confidence Score Analysis
* Heatmap-based Visualization
* Marine Ecosystem Summary Generation
* Detection History Tracking
* MongoDB Integration
* RESTful API Architecture
* Responsive React Frontend

---

## System Architecture

```text
React Frontend
        │
        ▼
FastAPI Backend
        │
        ▼
YOLOv8 Detection Model
        │
        ▼
MongoDB Database
```

---

## Tech Stack

### Frontend

* React.js
* JavaScript
* HTML
* CSS

### Backend

* FastAPI
* Python

### AI / Machine Learning

* YOLOv8 (Ultralytics)
* OpenCV
* NumPy
* Jupyter Notebook

### Database

* MongoDB

### Authentication

* JWT (JSON Web Tokens)

### Development Tools

* Git
* GitHub
* Google Colab

---

## Dataset

### Dataset Used

URPC2020 Underwater Object Detection Dataset

The dataset contains underwater images with annotated bounding boxes for object detection tasks.

### Dataset Structure

```text
dataset/
│
├── train/
│   ├── images/
│   └── labels/
│
├── valid/
│   ├── images/
│   └── labels/
│
└── test/
    ├── images/
    └── labels/
```

### Annotation Format

YOLO annotation format:

```text
<class_id> <x_center> <y_center> <width> <height>
```

All coordinate values are normalized between 0 and 1.

### Dataset Split

| Dataset    | Images |
| ---------- | ------ |
| Training   | 10,649 |
| Validation | 814    |
| Testing    | ~840   |

Approximate split:

```text
Train : Validation : Test
85% : 7% : 8%
```

---

## Model Training

### Model Used

YOLOv8

### Training Environment

* Google Colab
* NVIDIA Tesla T4 GPU

### Training Process

1. Dataset preparation and annotation verification
2. Data loading using YOLO format
3. Model training using YOLOv8
4. Validation after every epoch
5. Performance evaluation on unseen test data
6. Exporting trained weights for deployment

### Example Training Command

```python
from ultralytics import YOLO

model = YOLO("yolov8n.pt")

model.train(
    data="data.yaml",
    epochs=50,
    imgsz=640
)
```

---

## Image Preprocessing

To improve underwater visibility and detection performance, preprocessing techniques are applied before inference.

### Techniques Used

#### Gaussian Blur

* Reduces underwater noise
* Smooths distortions

#### CLAHE (Contrast Limited Adaptive Histogram Equalization)

* Improves local contrast
* Enhances visibility in uneven lighting conditions

#### White Balance Correction

* Removes underwater blue/green color cast
* Restores natural color balance

#### Brightness and Contrast Enhancement

* Improves object visibility
* Enhances feature extraction

---

## Model Evaluation

### Evaluation Metrics

#### Precision

Measures how many predicted detections are correct.

#### Recall

Measures how many actual objects are successfully detected.

#### mAP@50

Mean Average Precision at IoU threshold 50%.

#### mAP@50-95

Mean Average Precision averaged across IoU thresholds from 50% to 95%.

### Performance

| Metric    | Value  |
| --------- | ------ |
| Precision | ~80.8% |
| Recall    | ~73.2% |
| mAP@50    | ~81.0% |
| mAP@50-95 | ~46.0% |

---

## API Endpoints

### Authentication

#### Register

```http
POST /auth/register
```

#### Login

```http
POST /auth/login
```

Returns JWT access token.

---

### Object Detection

```http
POST /predict
```

Uploads an image and performs underwater object detection.

---

### Detection History

```http
GET /history/
```

Retrieves prediction history for authenticated users.

---

## Database Design

### Users Collection

```json
{
  "_id": "...",
  "username": "...",
  "email": "...",
  "hashed_password": "..."
}
```

### Prediction History Collection

```json
{
  "_id": "...",
  "user_id": "...",
  "image_name": "...",
  "detections": [],
  "confidence_scores": [],
  "marine_summary": "...",
  "timestamp": "..."
}
```

---

## Security Features

* JWT Authentication
* Password Hashing
* Protected API Routes
* Input Validation
* Image File Validation
* Error Handling
* Secure Frontend-Backend Communication

---

## Real-World Applications

* Marine Biodiversity Monitoring
* Coral Reef Conservation
* Ocean Research
* Underwater Robotics
* Autonomous Underwater Vehicles (AUVs)
* Underwater Surveillance
* Environmental Monitoring
* Offshore Infrastructure Inspection

---

## Future Enhancements

* Real-Time Video Detection
* Edge Deployment on Underwater Robots
* Cloud-Based Inference
* Advanced Image Enhancement Techniques
* Additional Marine Species Detection
* Live Analytics Dashboard
* Role-Based Access Control
* Model Optimization for Faster Inference

---

## Installation

### Clone Repository

```bash
git clone https://github.com/Suchitra-Siddharthan/Underwater-target-detection.git
```

### Backend Setup

```bash
cd backend

pip install -r requirements.txt

uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

---

## Learning Outcomes

This project provided practical experience in:

* Deep Learning
* Computer Vision
* Object Detection
* YOLOv8 Training and Deployment
* Image Processing
* REST API Development
* Authentication and Authorization
* MongoDB Integration
* Full-Stack Development
* Model Deployment and Integration

---

## Author

Suchitra Siddharthan

Computer Science and Engineering

