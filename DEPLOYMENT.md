# Railway Deployment Guide

## 🚀 One-Click Deploy to Railway

### Option 1: GitHub + Railway (Recommended)
1. Push this repo to GitHub
2. Go to [railway.app](https://railway.app)
3. Click "New Project" → "Deploy from GitHub"
4. Select your repository
5. Railway auto-detects `railway.toml` and deploys!

### Option 2: Manual CLI Deploy
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up

# Get URL
railway domain
```

### Option 3: Docker Deploy
```bash
# Build and run locally to test
docker build -t lung-triage ./backend
docker run -p 8000:8000 -v $(pwd)/model.pth:/app/model.pth lung-triage

# Deploy to Railway with Docker
railway up --dockerfile ./backend/Dockerfile
```

## 📁 Project Structure
```
lung-histopathology-triage/
├── backend/
│   ├── main.py          # FastAPI server
│   ├── requirements.txt # Python deps
│   └── Dockerfile       # Optional Docker
├── model.pth            # Your trained model
├── railway.toml         # Railway config
├── .gitignore           # Exclusions
└── DEPLOYMENT.md        # This file
```

## 🔧 Configuration
Set these variables in Railway dashboard:
- `PORT` (auto-set by Railway, usually 8000)
- `MODEL_PATH` (defaults to "model.pth" in root)

## 🌐 Endpoints
- `GET /health` - Health check
- `POST /predict` - Single image prediction
- `POST /predict/batch` - Multiple images
- `GET /docs` - Interactive API docs

## 💰 Cost
- **Free Tier**: 500 hours/month (enough for 24/7 small app)
- **Model Storage**: Included in free tier
- **Bandwidth**: 1TB/month free

## 📝 Notes
- Model.pth will be deployed with your code
- First deploy may take 5-10 minutes (dependency install)
- Subsequent deploys are faster (~2-3 min)
- Auto-scales based on traffic
- Includes HTTPS automatically