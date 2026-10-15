# Lung Histopathology Triage — Workspace Summary

## What This Project Is
A 3-class lung histopathology tumor classifier (adenocarcinoma, squamous_cell_carcinoma, benign) with a FastAPI backend for NHS triage.

## Key Files
- `model.py` — ResNet50 backbone (ImageNet pretrained), 3-class head
- `pretrained_cnn.py` — Ghost-141 architecture (LC25000CNN), pre-trained weights
- `train.py` — Two-phase training: frozen backbone → full fine-tune
- `dataset.py` — ImageFolder data loaders, 80/20 train/val split
- `api.py` — FastAPI: `/predict`, `/health`, Grad-CAM visualization
- `inference.py` — CLI inference on single images or directories
- `smoke_test.py` — End-to-end smoke test (model load, inference, Grad-CAM, API routes)
- `data_download.py` — Kaggle LC25000 dataset downloader
- `config.yaml` — Training hyperparameters (epochs, lr, scheduler)
- `requirements.txt` — torch, torchvision, opendatasets, fastapi, etc.
- `railway.toml` — Railway deployment config
- `DEPLOYMENT.md` — Deployment guide

## Current State
- ✅ Code written and tested
- ✅ Two model checkpoints included: `model.pth` and `LungDisease_Classifier.pth`
- ❌ `data/processed/` doesn't exist — needs `data_download.py` to run
- ❌ `backend/` folder referenced in DEPLOYMENT.md doesn't exist
- ❌ Railway config references `main.py` but API is in `api.py`

## Next Steps (in order)
1. Download LC25000 dataset via `data_download.py`
2. Train model with two-phase approach (frozen → fine-tune)
3. Validate accuracy
4. Start FastAPI server
5. Test predictions
6. Deploy to Railway

## Common Issues
- Use `.venv\Scripts\python.exe` not bare `python`
- Context usage: ~15% (29.7K / 200K tokens) — watch this
- Free model = openrouter/free (Gemma/Nemotron/GPT-OSS)
- **SESSION START PROTOCOL:** Every new session must ask (1) model selection (default `qwen/qwen3-coder-flash`) and (2) session summary. Files at same workspace path: `SESSION_START.md`, `SESSION_PROTOCOL.md`. Note: `AGENTS.md` references `/vault/spec.md` and `/agents/skills/` which don't exist here; use workspace files (`pretrained_cnn.py`, `cloned_dark_lung_dashboard/index.html`, `config.yaml`) instead.
- **Harness errors (session ~09:15):** (a) agent read `C:\workspace\BEST_MODEL.md` — correct path is workspace root above; (b) endpoint returned `400 Reasoning is mandatory`. `free_search_test` (ddg/bing) works independently; `web_search` auth relies on harness openrouter key. Model stays `qwen/qwen3-coder-flash`.