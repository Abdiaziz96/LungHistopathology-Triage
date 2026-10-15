"""
Lung Histopathology Triage - FastAPI Backend for Railway Deployment
"""
import os
import io
import json
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
import torch
import torch.nn as nn
from torchvision import transforms
from PIL import Image
import uvicorn
import numpy as np

app = FastAPI(
    title="Lung Histopathology Triage API",
    description="AI-assisted lung cancer classification from histopathology slides",
    version="1.0.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Model Definition (matches your trained model) ───
class SimpleCNN(nn.Module):
    def __init__(self, num_classes=3):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, 3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, 3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.AdaptiveAvgPool2d((7, 7)),
        )
        self.classifier = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(128 * 7 * 7, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(512, num_classes)
        )

    def forward(self, x):
        x = self.features(x)
        x = torch.flatten(x, 1)
        x = self.classifier(x)
        return x

# ─── Class labels ───
CLASS_LABELS = {
    0: "Benign",
    1: "Adenocarcinoma", 
    2: "Squamous Cell Carcinoma"
}

# ─── Load Model ───
MODEL_PATH = os.getenv("MODEL_PATH", "model.pth")
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = None
model_loaded = False

def load_model():
    global model, model_loaded
    try:
        if os.path.exists(MODEL_PATH):
            model = SimpleCNN(num_classes=3)
            checkpoint = torch.load(MODEL_PATH, map_location=DEVICE)
            
            # Handle different checkpoint formats
            if isinstance(checkpoint, dict):
                if 'state_dict' in checkpoint:
                    model.load_state_dict(checkpoint['state_dict'])
                elif 'model_state_dict' in checkpoint:
                    model.load_state_dict(checkpoint['model_state_dict'])
                else:
                    model.load_state_dict(checkpoint)
            else:
                model.load_state_dict(checkpoint)
            
            model.to(DEVICE)
            model.eval()
            model_loaded = True
            print(f"✅ Model loaded from {MODEL_PATH}")
        else:
            print(f"⚠️ Model file not found at {MODEL_PATH}")
            model_loaded = False
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        model_loaded = False

# Load on startup
load_model()

# ─── Image Transforms ───
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# ─── Pydantic Models ───
class PredictionResponse(BaseModel):
    prediction: str
    confidence: float
    all_probabilities: dict
    processing_time_ms: float

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    device: str
    model_path: str

# ─── Routes ───
@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="ok" if model_loaded else "degraded",
        model_loaded=model_loaded,
        device=str(DEVICE),
        model_path=MODEL_PATH
    )

@app.post("/predict", response_model=PredictionResponse)
async def predict(file: UploadFile = File(...)):
    import time
    start_time = time.time()
    
    if not model_loaded:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    # Validate file
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Read and process image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        
        # Transform
        input_tensor = transform(image).unsqueeze(0).to(DEVICE)
        
        # Predict
        with torch.no_grad():
            outputs = model(input_tensor)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)[0]
            predicted_class = torch.argmax(probabilities).item()
            confidence = probabilities[predicted_class].item()
        
        # Format response
        all_probs = {CLASS_LABELS[i]: float(probabilities[i]) for i in range(len(CLASS_LABELS))}
        processing_time = (time.time() - start_time) * 1000
        
        return PredictionResponse(
            prediction=CLASS_LABELS[predicted_class],
            confidence=confidence,
            all_probabilities=all_probs,
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.post("/predict/batch")
async def predict_batch(files: List[UploadFile] = File(...)):
    """Predict multiple images at once"""
    if not model_loaded:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    results = []
    for file in files:
        try:
            contents = await file.read()
            image = Image.open(io.BytesIO(contents)).convert("RGB")
            input_tensor = transform(image).unsqueeze(0).to(DEVICE)
            
            with torch.no_grad():
                outputs = model(input_tensor)
                probabilities = torch.nn.functional.softmax(outputs, dim=1)[0]
                predicted_class = torch.argmax(probabilities).item()
                confidence = probabilities[predicted_class].item()
            
            all_probs = {CLASS_LABELS[i]: float(probabilities[i]) for i in range(len(CLASS_LABELS))}
            
            results.append({
                "filename": file.filename,
                "prediction": CLASS_LABELS[predicted_class],
                "confidence": confidence,
                "all_probabilities": all_probs
            })
        except Exception as e:
            results.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return {"results": results}

@app.get("/")
async def root():
    return {
        "message": "Lung Histopathology Triage API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        workers=1
    )