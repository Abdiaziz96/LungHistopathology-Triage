# QUICK READ — Rapid Workspace Comprehension Skill

Purpose: Understand a workspace in <30s without re-reading everything.

Steps (ordered by time cost):
1. Read WORKSPACE_SUMMARY.md if it exists (maintenance: always keep it updated)
2. List root files only: `ls *.py *.yaml *.toml *.md *.pth`
3. Check critical directories exist: `data/`, `checkpoints/`, `backend/`
4. Read config first (usually 20 lines): `config.yaml`
5. Read module headers (first 20 lines of `model.py`, `train.py`, `api.py`)
6. Identify the gap: what's implemented vs missing (data, deployment, checks)

Do NOT: recursively list .venv/; re-read full source files from scratch; start new chats.

Usage: Before asking about the workspace, run this. Keep WORKSPACE_SUMMARY.md current.
