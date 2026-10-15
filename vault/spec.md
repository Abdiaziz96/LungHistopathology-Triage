# Vault Spec — Lung Histopathology Triage

Version: 4.1.0  |  Model: LC25000CNN (5-class, 192x192 input, 3-class lung subset)  |  Checkpoint: `LungDisease_Classifier.pth` or `model.pth`

## Scope
Full, verified system: FastAPI backend (`api.py`), React/Vite/Tailwind dashboard (`lung-dashboard/`), 3 skills, 2 verifier sub-agents, 2 safety hooks.

## 1. Backend (FastAPI — `api.py`)
- `POST /predict`: upload `.png`/`.jpg`/`.jpeg`/`.tiff`/`.tif`/`.svs`; preprocess to 192x192; return `prediction` (Adenocarcinoma / Squamous / Benign), `confidence` (%), `probabilities` dict, `heatmap_base64` (Grad-CAM PNG base64, overlay alpha=0.45), `time_saved_pct` (stub), `secondary_predictions`, `prediction_label` (Malignant/Benign), `model_status`.
- `GET /health`: `{status, device, model_version, num_classes}`.
- CORS: allow origins `http://localhost:5173` (tighten later), methods `GET/POST`, headers `*`.
- Lifespan loads checkpoint at startup; falls back to untrained weights if missing.
- Grad-CAM: hook on `conv_layers`; resize CAM to 192x192; overlay via JET colormap.

## 2. Frontend (`lung-dashboard/` — React + Vite + Tailwind + shadcn/ui)
- Single-page dashboard. Header: NHS branding (`#005EB8`), live `/health` status. Mobile-first responsive.
- Drag-and-drop upload zone (whole-slide or tile images). Stats panel: Prediction, Confidence (%), Time Saved (%), secondary predictions.
- Component to display `heatmap_base64` image. Clean clinical design.

## 3. Data & Model
- `LC25000CNN` (5-class). Use only `LUNG_CLASS_INDICES = [0,1,2]` for predictions; ignore colon. `CLASS_NAMES_3` = ["adenocarcinoma","benign","squamous_cell_carcinoma"].
- Preprocessing: `Resize(192)`, `ToTensor()`; no extra ImageNet normalization in current version (matches `pretrained_cnn.py`).

## 4. Skills (`/agents/skills/`)
- `test_model.md` + `scripts/test_model.py`: test against LC25000 test samples; output `tested / accuracy / per-class`.
- `backend_deploy.md`: stop/restart/health-check steps.
- `dashboard_start.md`: start React dev server in `lung-dashboard`.

## 5. Sub-Agent Verifiers
- UI Verifier: headless Playwright; check header branding, drag-drop zone, `/predict` call, heatmap display, responsiveness at 375px/768px/1440px. Report pass/fail + errors.
- Backend Verifier: integration tests against `/predict` and `/health`; verify response schema and data. Report pass/fail + errors.

## 6. Safety Hooks (must stay active)
- Block `git reset --hard` executions.
- Block direct `psql`; only allow `docker exec psql ...`.

## 7. Policies
- Reasoning mandatory; approval disabled (`never`); `danger-full-access` applies. Never include `sandbox_permissions` in any call.
- Model selection: use free-models router (`openrouter/free`). qwen preference removed.

## 8. Implementation Order
A. Confirm `spec.md` present. B. Verify skills exist. C. Run `scripts/test_model.py`. D. Start backend. E. Start dashboard. F. Spawn UI + Backend verifiers. G. Fix any failures; re-run; compile final report.