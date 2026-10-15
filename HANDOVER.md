HANDOVER — LungHistopathology-Triage
Created: 2026-07-25 | Session state: continuation (not new session) | Approval: never | Sandbox: danger-full-access

MODEL
- Active: qwen/qwen3-coder-flash (BEST_MODEL.md, workspace root path — NOT C:\workspace which caused a prior read failure)
- Previous: tried deepseek-v4-flash (not in openrouter manifest; removed)
- Session-start protocol (SESSION_START.md): reference-only; NOT enforcing 2 questions (previous enforcement caused session-start failures)

WORKING STATE
- `free_search_test`: ddg OK, bing OK
- `web_search` (openrouter/free endpoint): auth still blocked by bad harness key (****a228 — see WORKSPACE_SUMMARY.md line 40); search plugin itself works
- Endpoint `400 Reasoning is mandatory`: occurred at session ~09:15; cleared by staying on qwen with reasoning=true (reasoning parameter endpoint-level, not file-level)
- Dashboard: `cloned_dark_lung_dashboard/index.html` rebuilt (clinical theme, header, triage upload, footer — see previous turns)
- Workspace docs: WORKSPACE_SUMMARY.md (line 39+ updated with protocol + harness errors), SESSION_PROTOCOL.md, SESSION_START.md

UNFINISHED / KNOWN BLOCKS
- `data/processed/` missing (needs `data_download.py`)
- `backend/` folder missing (DEPLOYMENT.md reference broken)
- `railway.toml` references `main.py` but API is `api.py`
- `AGENTS.md` references `/vault/spec.md` and `/agents/skills/` which do not exist in this workspace; rely on workspace files (`pretrained_cnn.py`, `config.yaml`, `cloned_dark_lung_dashboard/index.html`)
- `WORKSPACE_SUMMARY.md` line 39: full session protocol + harness errors documented

WHAT NEXT AGENT SHOULD DO (new chat / handover)
1. Use BEST_MODEL.md (qwen/qwen3-coder-flash, reasoning=true) — don't invent model IDs
2. Use workspace root path (`C:\Users\Abdurrahman\Documents\DeepSeekHarness-Projects\LungHistopathology-Triage`) — don't read `C:\workspace`
3. If `400 Reasoning is mandatory` recurs: endpoint-level; either restart harness with reasoning enabled or accept current working state
4. `SESSION_START.md` is reference-only — don't enforce 2 questions; use previous chat / WORKSPACE_SUMMARY.md / BEST_MODEL.md for context
5. Don't invent openrouter auth keys; document web-search block in WORKSPACE_SUMMARY.md instead
6. Reference `AGENTS.md` rules (approval=never, danger-full-access, verifier rerun loop) before backend/UI changes; `/vault/spec.md` missing — use workspace files

FILES TO READ FIRST IN NEW SESSION (in this order)
- BEST_MODEL.md (model state)
- WORKSPACE_SUMMARY.md (workspace state + protocol + errors)
- SESSION_START.md (session context — reference only)
- AGENTS.md (project rules — /vault/spec.md missing, use workspace files)
- `cloned_dark_lung_dashboard/index.html` (current dashboard output)
- `pretrained_cnn.py` / `model.py` / `api.py` (domain content — not from memory)
