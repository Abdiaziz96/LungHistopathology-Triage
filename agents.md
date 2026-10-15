# LungHistopathology-Triage — Agent Guidelines

## Project
AI-driven lung histopathology triage: FastAPI backend (`/predict`, `/health`, Grad-CAM) + React/Vite/Tailwind dashboard (NHS blue #005EB8). Verified by UI and Backend Verifier sub-agents.

## Rules for agents
- Read `/vault/spec.md` before changing backend or UI.
- Model file: `model.pth` (or `LungDisease_Classifier.pth`) — 18MB CNN, expects 224x224 normalized.
- Skills live in `/agents/skills/`; deterministic scripts in `scripts/`.
- Research artifacts (downloaded READMEs, blog posts, third-party analyses) go in `research/`. That folder is gitignored and must never be committed or imported by product code.
- Safety hooks (`git reset --hard` blocker; `psql` -> `docker exec psql` only) must stay active.
- Approval is disabled (`never`) — do not ask, and do not escalate via `sandbox_permissions` (it will fail). `danger-full-access` applies.
- If any verifier reports failure: fix, re-run, compile report. Repeat until pass.
